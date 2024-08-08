import argparse
import urllib.request
import os
import pandas as pd
import fitz  # PyMuPDF
from datetime import datetime
import math
import requests
import re
import requests_cache
from retry_requests import retry
import openmeteo_requests

#for Historical Weather api data.
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
    # print(location_counts[['Location', 'Counts']])
    # Making my open rank so that i can satisfy the condition in assignment2 doc
    location_counts['Rank'] = 1  
    rank = 1
    for i in range(1, len(location_counts)):
        if location_counts.at[i, 'Counts'] < location_counts.at[i-1, 'Counts']:
            rank = i + 1  
        location_counts.at[i, 'Rank'] = rank
    
    location_to_rank = pd.Series(location_counts.Rank.values,index=location_counts.Location).to_dict()
    #using dictionary to map for future usage.
    df['Location Rank'] = df['Location'].map(location_to_rank)
    return df['Location Rank']

def calculate_incident_rank(df): #done in almost same way as location rank is done 
    # Calculate frequency of each incident nature
    nature_counts = df['Nature'].value_counts().reset_index()
    nature_counts.columns = ['Nature', 'Counts']
    nature_counts.sort_values('Counts', ascending=False, inplace=True)
    
    nature_counts['Rank'] = 1  
    rank = 1
    for i in range(1, len(nature_counts)):
        if nature_counts.at[i, 'Counts'] < nature_counts.at[i-1, 'Counts']:
            rank = i + 1 
        nature_counts.at[i, 'Rank'] = rank
    
    # Create a dictionary mapping natures to their ranks
    nature_to_rank = pd.Series(nature_counts.Rank.values,index=nature_counts.Nature).to_dict()
    # Use the dictionary to map each nature in the DataFrame to its rank
    df['Incident Rank'] = df['Nature'].map(nature_to_rank)
    return df['Incident Rank']


#for day of the week code 
def get_day_of_week(date_str):
    date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
    return (date_obj.weekday() + 1) % 7 + 1

def calculate_day_of_week(df):
    df['Day of Week'] = df['Date/Time'].apply(get_day_of_week)
    return df['Day of Week'].reset_index(drop=True)


#code for calculating time of day 
def get_time_of_day(date_str):
    # Parse the date string into a datetime object using the correct format
    date_obj = datetime.strptime(date_str, "%m/%d/%Y %H:%M")
    # Extract and return the hour component
    return date_obj.hour
    
def calculate_time_of_day(df):
    df['Time of Day'] = df['Date/Time'].apply(get_time_of_day)
    return df


#extract name from column , Just need to copy from original df.
def extract_nature_column(df):
    return df['Nature']

def calculate_emsstat(df):
    #EMsstat col creat
    df['EMSSTAT'] = False
    # Iterate over the DataFrame to mark direct EMSSTAT occurrences
    for i in range(len(df)):
        if df.loc[i, 'Incident ORI'] == 'EMSSTAT':
            df.loc[i, 'EMSSTAT'] = True
    
    # Identify groups by 'Date/Time' and 'Location' that contain any EMSSTAT and mark all records in those groups
    emsstat_groups = df[df['EMSSTAT'] == True].groupby(['Date/Time', 'Location']).groups #got every of them and then mark as true
    for (date_time, location), indexes in emsstat_groups.items():
        df.loc[df[(df['Date/Time'] == date_time) & (df['Location'] == location)].index, 'EMSSTAT'] = True

    return df['EMSSTAT']

geocode_cache = {}
def geocode_address_google(address, api_key, append_info="Norman, OK"):
    # AIzaSyApMAgl_myEP06P6-GHzeTsAYbTdOsMa70
    #if we already have lang and lat just use them and not hit api for it.
    if address in geocode_cache:
        return geocode_cache[address]
    if ';' in address:
        try:
            lat_str, lon_str = address.split(';')
            lat, lon = float(lat_str), float(lon_str)
            geocode_cache[address] = (lat, lon)
            return float(lat_str), float(lon_str)
        except ValueError:
            # print(f"Invalid coordinate format for address: {address}")
            return None, None

    full_address = f"{address}, {append_info}"
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": full_address, "key": api_key}
    response = requests.get(base_url, params=params)
    #if works then it will go here to give long and latitude
    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK":
            lat = data["results"][0]["geometry"]["location"]["lat"]
            lon = data["results"][0]["geometry"]["location"]["lng"]
            geocode_cache[address] = (lat, lon)
            return lat, lon
        else:
            #otherwise will return NONE in both the cases
            return None, None
    else:
        # print(f"HTTP error: {response.status_code} for address {address}")
        return None, None

def ensure_geocoding(df, api_key):
    if 'Latitude' not in df.columns:
        #store in df for further use
        df['Latitude'] = pd.Series([None]*len(df), index=df.index)
    if 'Longitude' not in df.columns:
        #store in df for further use
        df['Longitude'] = pd.Series([None]*len(df), index=df.index)

    for index, row in df.iterrows():
        # Now safely check if Latitude or Longitude needs to be geocoded
        if pd.isnull(row['Latitude']) or pd.isnull(row['Longitude']):
            lat, lon = geocode_address_google(row['Location'], api_key)
            if lat is not None and lon is not None:
                df.at[index, 'Latitude'] = lat
                df.at[index, 'Longitude'] = lon
            else:
                # Explicitly set to None if geocoding fails
                df.at[index, 'Latitude'] = None
                df.at[index, 'Longitude'] = None
    return df

def calculate_compass_bearing(start_point, end_point):
    # Convert the latitude of both points from degrees to radians
    lat1 = math.radians(start_point[0])
    lat2 = math.radians(end_point[0])

    # Calculate the difference in longitude between the two points, also in radians
    longitude_difference = math.radians(end_point[1] - start_point[1])

    # Calculate the components of the vector pointing from start to end point
    x = math.sin(longitude_difference) * math.cos(lat2)
    z=math.sin(lat1) * math.cos(lat2) * math.cos(longitude_difference)
    y = math.cos(lat1) * math.sin(lat2) - z

    # Compute the initial bearing by taking the arctangent of x and y components
    initial_bearing = math.atan2(x, y)

    # Convert the initial bearing from radians to degrees and adjust the angle to be between 0 and 360
    compass_bearing = (math.degrees(initial_bearing) + 360) % 360
    #return of the bearning 
    return compass_bearing

def extract_cardinal_direction(location):
    #use of re if api fails so we can check from here
    pattern = r'\b(N|S|E|W|NW|NE|SW|SE)\b'
    match = re.search(pattern, location)
    if match:
        return match.group(1)
    return None

def determine_side_of_town(lat, lon):
    center_of_town = (35.220833, -97.443611)
    bearing = calculate_compass_bearing(center_of_town, (lat, lon))
    # Complete mapping from bearing to side of town
    if bearing >= 337.5 or bearing < 22.5:
        return 'N'
    elif bearing >= 22.5 and bearing < 67.5:
        return 'NE'
    elif bearing >= 112.5 and bearing < 157.5:
        return 'SE'
    elif bearing >= 67.5 and bearing < 112.5:
        return 'E'
    elif bearing >= 202.5 and bearing < 247.5:
        return 'SW'
    elif bearing >= 157.5 and bearing < 202.5:
        return 'S'
    elif bearing >= 292.5 and bearing < 337.5:
        return 'NW'
    elif bearing >= 247.5 and bearing < 292.5:
        return 'W'
    else:
        return "Could not determine side of town"

def side_of_town(df):
    """Determine the side of town for each record based on its latitude and longitude."""
    for index, row in df.iterrows():
        lat = row['Latitude']
        lon = row['Longitude']
        location = row.get('Location', '')  # Get 'Location' if it exists, else default is empty string

        # Check if latitude and longitude are available
        if pd.notna(lat) and pd.notna(lon):
            side = determine_side_of_town(lat, lon)
            # If no valid side found from lat/lon, try to get it from location
            if side is None or side == "":
                cardinal_direction = extract_cardinal_direction(location)
                if cardinal_direction:
                    # If we got a cardinal direction, use it
                    df.at[index, 'Side of Town'] = cardinal_direction
                else:
                    # No side or direction found, set as could not determine
                    df.at[index, 'Side of Town'] = "Could not determine"
            else:
                # Valid side found, assign it
                df.at[index, 'Side of Town'] = side
        else:
            # Lat and Lon not available, try to determine side from location directly
            cardinal_direction = extract_cardinal_direction(location)
            if cardinal_direction:
                df.at[index, 'Side of Town'] = cardinal_direction
            else:
                # If everything fails, we can't determine the side of town
                df.at[index, 'Side of Town'] = "Could not determine"
    
    return df

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
            # print(f"Failed to fetch weather data for index {index}")
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
    
    
    augmented_df['Day of the Week'] = calculate_day_of_week(all_incidents_df)
    augmented_df['Time of Day'] = all_incidents_df['Time of Day'].copy()
    augmented_df['Weather'] = fetch_weather_code_for_df(all_incidents_df)
    augmented_df['Location Rank'] = calculate_location_rank(all_incidents_df)
    augmented_df['Side of Town']=all_incidents_df['Side of Town'].copy()
    augmented_df['Incident Rank'] = calculate_incident_rank(all_incidents_df)
    # augmented_df['Location'] = all_incidents_df['Location'].copy()
    augmented_df['Nature'] = all_incidents_df['Nature'].copy()
    augmented_df['EMSSTAT'] = calculate_emsstat(all_incidents_df)

    return augmented_df
def main(urls_filename):
    # apikey
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
    # print(all_incidents_df)
    ans_df=create_augmented_dataframe(all_incidents_df)
    file_path = './ans.csv'
    ans_df.to_csv(file_path, sep='\t', index=False)
    pd.set_option('display.max_rows', None)
    print(ans_df)
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Process incident data from PDF URLs listed in a file.")
    parser.add_argument("--urls", type=str, required=True, help="Filename containing the list of PDF URLs.")
    
    args = parser.parse_args()
    
    main(args.urls)


