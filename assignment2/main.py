import argparse
import urllib.request
import os
import pandas as pd
import fitz  # PyMuPDF
import sys
from datetime import datetime
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError
import math
import requests
import re
import requests_cache
from retry_requests import retry
import openmeteo_requests
from datetime import timedelta

cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def extract_incidents_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_text = ""
    for page in doc:
        all_text += page.get_text()
    doc.close()

    lines = all_text.split('\n')
    data = {'Date/Time': [], 'Incident Number': [], 'Location': [], 'Nature': [], 'Incident ORI': []}

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if '/' in line and ':' in line:  # Likely a 'Date/Time' entry
            data['Date/Time'].append(line)
            i += 1  # Move to the next line for 'Incident Number'
            
            # Ensure subsequent values are captured or set to 'NULL' if not present or if the next record starts
            for field in ['Incident Number', 'Location', 'Nature', 'Incident ORI']:
                # if field == 'Nature' and 'RAMP' in lines[i].upper():
                #         data[field].append(lines[i+1].strip() if lines[i+1].strip() else "null")
                if i < len(lines) and not ('/' in lines[i] and ':' in lines[i]):
                    if(field=='Nature' and lines[i]=="RAMP"):
                        data[field].append(lines[i+1].strip() if lines[i+1].strip() else "")
                    else:
                        data[field].append(lines[i].strip() if lines[i].strip() else "")
                    i += 1
                else:
                    # If the expected value is missing, append 'NULL' and do not increment 'i'
                    data[field].append("")
        else:
            # If the line doesn't match the expected start of a new record, increment 'i' to check the next line
            i += 1

    # Validate lengths of lists before creating DataFrame
    if not all(len(lst) == len(data['Date/Time']) for lst in data.values()):
        raise ValueError("Error: Mismatch in list lengths within the data dictionary.")
    
    if data['Date/Time']:  # Ensure there's at least one record
        for key in data:
            data[key].pop(-1)
    return pd.DataFrame(data)

def calculate_location_rank(df):
    # Calculate frequency of each location
    location_counts = df['Location'].value_counts().reset_index()
    location_counts.columns = ['Location', 'Counts']
    location_counts.sort_values('Counts', ascending=False, inplace=True)
    

# Now, you can print 'Location Rank' and 'Counts' from location_counts DataFrame
    # print(location_counts[['Location', 'Counts']])
    # Apply your custom rank calculation
    location_counts['Rank'] = 1  # Initialize all ranks as 1
    rank = 1
    for i in range(1, len(location_counts)):
        if location_counts.at[i, 'Counts'] < location_counts.at[i-1, 'Counts']:
            rank = i + 1  # Increment rank based on your condition
        location_counts.at[i, 'Rank'] = rank
    
    # Create a dictionary mapping locations to their ranks
    location_to_rank = pd.Series(location_counts.Rank.values,index=location_counts.Location).to_dict()

    # Use the dictionary to map each location in the DataFrame to its rank
    df['Location Rank'] = df['Location'].map(location_to_rank)
    return df['Location Rank']

def calculate_incident_rank(df):
    # Calculate frequency of each incident nature
    nature_counts = df['Nature'].value_counts().reset_index()
    nature_counts.columns = ['Nature', 'Counts']
    nature_counts.sort_values('Counts', ascending=False, inplace=True)
    
    # Initialize all ranks as 1 and apply custom rank calculation
    nature_counts['Rank'] = 1  
    rank = 1
    for i in range(1, len(nature_counts)):
        if nature_counts.at[i, 'Counts'] < nature_counts.at[i-1, 'Counts']:
            rank = i + 1  # Increment rank based on your condition
        nature_counts.at[i, 'Rank'] = rank
    
    # Create a dictionary mapping natures to their ranks
    nature_to_rank = pd.Series(nature_counts.Rank.values,index=nature_counts.Nature).to_dict()

    # Use the dictionary to map each nature in the DataFrame to its rank
    df['Incident Rank'] = df['Nature'].map(nature_to_rank)

    return df['Incident Rank']



def calculate_day_of_week(df):
    """
    Add a 'Day of Week' column to the DataFrame based on the 'Date / Time' field.
    Converts day of the week such that 1 corresponds to Sunday and 7 to Saturday.
    """
    def get_day_of_week(date_str):
        date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
        # Adjust calculation to correctly reflect Sunday as 1 through Saturday as 7
        return (date_obj.weekday() + 1) % 7 + 1

    df['Day of Week'] = df['Date/Time'].apply(get_day_of_week)
    return df['Day of Week'].reset_index(drop=True)

def calculate_time_of_day(df):
    """
    Adds a 'Time of Day' column to the DataFrame based on the 'Date / Time' field,
    extracting the hour from the date and time information.
    The 'Time of Day' is a numeric code from 0 to 24 describing the hour of the incident.
    """
    def get_time_of_day(date_str):
        # Parse the date string into a datetime object using the correct format
        date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
        # Extract and return the hour component
        return date_obj.hour

    # Apply the function to each row in the DataFrame
    df['Time of Day'] = df['Date/Time'].apply(get_time_of_day)

    return df

def extract_nature_column(df):
    return df['Nature']

def calculate_emsstat(df):
    # Pre-populate 'EMSSTAT' column with False
    df['EMSSTAT'] = False
    
    # Iterate over the DataFrame to mark direct EMSSTAT occurrences
    for i in range(len(df)):
        if df.loc[i, 'Incident ORI'] == 'EMSSTAT':
            df.loc[i, 'EMSSTAT'] = True
    
    # Identify groups by 'Date/Time' and 'Location' that contain any EMSSTAT and mark all records in those groups
    emsstat_groups = df[df['EMSSTAT'] == True].groupby(['Date/Time', 'Location']).groups
    for (date_time, location), indexes in emsstat_groups.items():
        df.loc[df[(df['Date/Time'] == date_time) & (df['Location'] == location)].index, 'EMSSTAT'] = True

    return df['EMSSTAT']

def geocode_address_google(address, api_key, append_info="Norman, OK"):
    """
    Geocode addresses using Google Maps API and return latitude and longitude.
    """
    # Check if the address is in the format of coordinates
    if ';' in address:
        try:
            lat_str, lon_str = address.split(';')
            return float(lat_str), float(lon_str)
        except ValueError:
            print(f"Invalid coordinate format for address: {address}")
            return None, None

    full_address = f"{address}, {append_info}"
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": full_address, "key": api_key}
    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lon = data["results"][0]["geometry"]["location"]["lng"]
            return lat, lon
        else:
            return None, None
    else:
        print(f"HTTP error: {response.status_code} for address {address}")
        return None, None

def ensure_geocoding(df, api_key):
    # Ensure the DataFrame has the necessary columns initialized if they don't exist.
    if 'Latitude' not in df.columns:
        df['Latitude'] = pd.Series([None]*len(df), index=df.index)
    if 'Longitude' not in df.columns:
        df['Longitude'] = pd.Series([None]*len(df), index=df.index)

    for index, row in df.iterrows():
        # Now safely check if Latitude or Longitude needs to be geocoded
        if pd.isnull(row['Latitude']) or pd.isnull(row['Longitude']):
            lat, lon = geocode_address_google(row['Location'], api_key)
            if lat is not None and lon is not None:
                df.at[index, 'Latitude'] = lat
                df.at[index, 'Longitude'] = lon
    return df


def calculate_initial_compass_bearing(pointA, pointB):
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    compass_bearing = (math.degrees(initial_bearing) + 360) % 360
    return compass_bearing

def extract_cardinal_direction(location):
    """
    Extracts cardinal direction from the location string using regex.
    Looks for one of the eight cardinal directions {N, S, E, W, NW, NE, SW, SE}.
    """
    pattern = r'\b(N|S|E|W|NW|NE|SW|SE)\b'
    match = re.search(pattern, location)
    if match:
        return match.group(1)
    return None
def determine_side_of_town(lat, lon):
    center_of_town = (35.220833, -97.443611)
    bearing = calculate_initial_compass_bearing(center_of_town, (lat, lon))
    # Complete mapping from bearing to side of town
    if bearing >= 337.5 or bearing < 22.5:
        return 'N'
    elif bearing >= 22.5 and bearing < 67.5:
        return 'NE'
    elif bearing >= 67.5 and bearing < 112.5:
        return 'E'
    elif bearing >= 112.5 and bearing < 157.5:
        return 'SE'
    elif bearing >= 157.5 and bearing < 202.5:
        return 'S'
    elif bearing >= 202.5 and bearing < 247.5:
        return 'SW'
    elif bearing >= 247.5 and bearing < 292.5:
        return 'W'
    elif bearing >= 292.5 and bearing < 337.5:
        return 'NW'
    else:
        return "Could not determine side of town"

def side_of_town(df):
    """Determine the side of town for each record based on its latitude and longitude."""
    for index, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        
        if pd.notna(lat) and pd.notna(lon):
            side = determine_side_of_town(lat, lon)
            df.at[index, 'Side of Town'] = side
        else:
            df.at[index, 'Side of Town'] = "Could not determine"
    
    return df

# def side_of_town(df, api_key):
#     # Ensure DataFrame has necessary columns
#     if 'Latitude' not in df.columns:
#         df['Latitude'] = None
#     if 'Longitude' not in df.columns:
#         df['Longitude'] = None
#     if 'Side of Town' not in df.columns:
#         df['Side of Town'] = None
    
#     for index, row in df.iterrows():
#         # Only geocode if lat and lon are not already provided or are invalid
#         if pd.isna(row['Latitude']) or pd.isna(row['Longitude']):
#             lat, lon = geocode_address_google(row['Location'], api_key, "Norman, OK")
#             # Update the DataFrame with the obtained latitude and longitude
#             df.at[index, 'Latitude'] = lat
#             df.at[index, 'Longitude'] = lon
#         else:
#             # Use existing latitude and longitude
#             lat = row['Latitude']
#             lon = row['Longitude']
        
#         # Determine the side of town using the latitude and longitude
#         if lat is not None and lon is not None:
#             side = determine_side_of_town(lat, lon)
#             df.at[index, 'Side of Town'] = side
#         else:
#             # Attempt to extract a cardinal direction from the location string if geocoding failed
#             cardinal_direction = extract_cardinal_direction(row['Location'])
#             if cardinal_direction:
#                 df.at[index, 'Side of Town'] = cardinal_direction
#             else:
#                 df.at[index, 'Side of Town'] = "Could not determine"
    
#     return df['Side of Town']

def fetch_weather_code_for_df(df):
    for index, row in df.iterrows():
        # Parse 'Date/Time' string to a datetime object with the correct format
        datetime_obj = pd.to_datetime(row['Date/Time'], format='%m/%d/%Y %H:%M')

        # Convert datetime object to date string in ISO format for the API request
        start_date = datetime_obj.date().isoformat()
        # Setup parameters for the API request
        params = {
            "latitude": row['Latitude'],
            "longitude": row['Longitude'],
            "start_date": start_date,
            "end_date": start_date,  # Ensure this is the day after start_date
            "hourly": ["weather_code"]
        }

        # Use the Open-Meteo API client to retrieve weather data
        responses = openmeteo.weather_api("https://archive-api.open-meteo.com/v1/archive", params=params)


        # Check if responses are available and process them
        if responses:
            response = responses[0]
            # Assuming 'hourly_weather_code' is specified in the API response
            # You need to adjust this part based on the actual structure of your response
            hourly_weather_code = response.Hourly().Variables(0).ValuesAsNumpy()

            # Example to extract a single weather code, adjust as needed
            time_of_day = int(row['Time of Day'])
            if len(hourly_weather_code) > 0:
                df.at[index, 'WMO Code'] = hourly_weather_code[time_of_day]
            else:
                df.at[index, 'WMO Code'] = None
        else:
            print(f"Failed to fetch weather data for index {index}")
            df.at[index, 'WMO Code'] = None

    return df['WMO Code']

def download_pdf(url, save_path='/tmp/incident_report.pdf'):
    """Download PDF from a specified URL to a local file path."""
    headers = {'User-Agent': "Mozilla/5.0"}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(request)
    data = response.read()
    with open(save_path, 'wb') as file:
        file.write(data)
    return save_path

def read_urls_from_file(filename):
    """Read URLs from a file, returning a list of URLs."""
    with open(filename, 'r') as file:
        urls = file.read().splitlines()
    return urls
def create_augmented_dataframe(all_incidents_df):
    augmented_df = pd.DataFrame()
    
    augmented_df['Location'] = all_incidents_df['Location'].copy()
    augmented_df['Day of the Week'] = calculate_day_of_week(all_incidents_df)
    augmented_df['Time of Day'] = all_incidents_df['Time of Day'].copy()
    augmented_df['Location Rank'] = calculate_location_rank(all_incidents_df)
    augmented_df['WMO Code'] = fetch_weather_code_for_df(all_incidents_df)
    augmented_df['Side of Town']=all_incidents_df['Side of Town'].copy()
    augmented_df['Incident Rank'] = calculate_incident_rank(all_incidents_df)
    augmented_df['Nature'] = all_incidents_df['Nature'].copy()
    augmented_df['EMSSTAT'] = calculate_emsstat(all_incidents_df)

    return augmented_df
def main(urls_filename):
    api_key = "AIzaSyCh28Jy9e30ULUW0crS3-9NtT6khonR0sI" 
    """Process incident data from multiple PDF URLs listed in a given file."""
    if not os.path.exists('resources'):
        os.makedirs('resources')
    # Read URLs from the provided file
    urls = read_urls_from_file(urls_filename)

    # Initialize an empty DataFrame for collecting data from all PDFs
    all_incidents_df = pd.DataFrame()

    for url in urls:
        pdf_path = download_pdf(url)
        incidents_df = extract_incidents_from_pdf(pdf_path)
        
        # Append the data from this PDF to the collective DataFrame
        all_incidents_df = pd.concat([all_incidents_df, incidents_df], ignore_index=True)
        
    all_incidents_df = ensure_geocoding(all_incidents_df, api_key)    
    all_incidents_df = side_of_town(all_incidents_df)
    all_incidents_df = calculate_time_of_day(all_incidents_df)
    print(all_incidents_df)
    ans_df=create_augmented_dataframe(all_incidents_df)
    file_path = './ans.csv'

    ans_df.to_csv(file_path, sep='\t', index=False)
    




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process incident data from PDF URLs listed in a file.")
    parser.add_argument("--urls", type=str, required=True, help="Filename containing the list of PDF URLs.")
    
    args = parser.parse_args()
    
    main(args.urls)


