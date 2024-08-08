## Norman PD Incident Data Pipeline and Visualization

**Name:** Pratham Sharma  
**Email:** sharmapratham@ufl.edu

## Assignment Description

This project processes and augments data from incident reports from the Norman, Oklahoma City Police Department. It extracts events from PDF files, uses the Google Maps API to geocode event locations, determines parts of the city for each event based on coordinates, calculates event and location groups, and assigns weather information to the data at each time and event using the Historical Weather API. The goal is to provide improved event insights for further analysis.

## How to Run the Code

### Installation Instructions

Ensure that you have `pipenv` installed. If not, install it using:

```bash
pip install pipenv
```

Set up the project environment with:

```bash
pipenv install
```

### Running the Code

To execute the code, use the following command:

```bash
pipenv run python assignment.py --urls <path_to_file_with_pdf_urls>
```

Replace `<path_to_file_with_pdf_urls>` with the path to a text file containing URLs of the PDF files to be processed, one URL per line. For example:

```bash
pipenv run python main.py --urls pdf_urls.txt
```

This command will process the PDFs listed in `pdf_urls.txt`, extract incident data, geocode locations, augment data with side of town and weather information, and output the augmented data in a tab-separated CSV file.

### Running the Visualization

To run the Streamlit app for visualization, use:

```bash
pipenv run streamlit run src/norman.py
```

## Functions Overview

This project includes a set of tools for extracting, processing, and improving incident report data from PDF files. Here is an overview of each function and its purpose:

- **`extract_incidents_from_pdf(pdf_path)`**: Parses PDF files to extract incident report data, structuring it into a pandas DataFrame for further processing.
- **`calculate_location_rank(df)`**: Ranks locations according to the frequency of incidents, helping identify places with higher event counts.
- **`calculate_incident_rank(df)`**: Ranks incident types ('Nature') based on their occurrence frequency, indicating common types of incidents.
- **`calculate_day_of_week(df)`**: Adds a column indicating the day of the week for each incident, aiding in temporal analysis.
- **`calculate_time_of_day(df)`**: Appends a column for the hour of the day each incident occurred, useful for identifying time-related trends.
- **`extract_nature_column(df)`**: Isolates the 'Nature' column, focusing analysis on the types of incidents reported.
- **`calculate_emsstat(df)`**: Identifies records marked as EMSSTAT or later records with the same time and place, indicating situations requiring emergency medical attention.
- **`geocode_address_google(address, api_key, append_info="Norman, OK")`**: Converts incident locations into geographic coordinates using the Google Maps Geocoding API.
- **`ensure_geocoding(df, api_key)`**: Ensures each incident location is geocoded, adding latitude and longitude coordinates to the DataFrame.
- **`calculate_initial_compass_bearing(pointA, pointB)`**: Calculates the compass bearing between two points, used in determining sides of town.
- **`extract_cardinal_direction(location)`**: Extracts cardinal directions from location strings, providing a fallback method for determining sides of town.
- **`determine_side_of_town(lat, lon)`**: Determines the side of town for each incident based on its geographic coordinates relative to the town center.
- **`side_of_town(df)`**: Processes the DataFrame to assign each incident a side of town, based on either geocoded coordinates or extracted cardinal directions.
- **`fetch_weather_code_for_df(df)`**: Augments the DataFrame with weather conditions at the time of each incident, using weather codes fetched from a weather API.
- **`download_pdf(url, save_path)`**: Downloads a PDF file from a specified URL to a local path, facilitating offline data extraction.
- **`read_urls_from_file(filename)`**: Reads a list of URLs from a file, supporting batch processing of multiple PDF files.
- **`create_augmented_dataframe(all_incidents_df)`**: Compiles and augments data from multiple incident reports into a comprehensive DataFrame for analysis or export.

This comprehensive set of functions allows for a detailed analysis of incident reports by enriching the raw data with temporal, geographic, and weather-related information.

## About the Process

### Geocoding with Google Maps API
The project uses the Google Maps Geocoding API to provide each incident with additional geographic information. The location text found in incident reports is converted into exact latitude and longitude coordinates. The ensuing spatial analysis, which includes identifying the side of town where occurrences happen, depends on this geocoding stage. Geocoded coordinates enable spatial insights that are crucial for public safety and resource allocation plans.

### Weather Data Integration
Understanding the weather at the time of each incident gives additional context. The project uses a Historical Weather API to retrieve meteorological information based on each incident's date, time, and geographic locations. This integration allows investigation of how weather conditions may impact the occurrence or nature of incidents.

### Data Augmentation and Analysis
The project enables comprehensive examination of public safety situations by integrating weather and geographic data. Analysts can explore patterns such as the frequency of incidents in specific areas, times of day, days of the week, or weather conditions. This enriched dataset supports diverse analyses, guiding the deployment of resources and public safety policies.

## Tools and Libraries Used

- **argparse**: Parses command-line arguments and options.
- **urllib.request**: Fetches data from the web.
- **os**: Interacts with the operating system for path manipulations.
- **pandas**: Handles dataframes for data extraction, processing, and augmentation.
- **fitz (PyMuPDF)**: Interacts with PDF files to extract text.
- **datetime**: Manages date and time data.
- **geopy**: Geocodes addresses to latitude and longitude coordinates.
- **math**: Performs mathematical calculations.
- **requests**: Makes HTTP requests to web services.
- **re (Regular Expression)**: Matches specific pieces of data in text.
- **requests_cache**: Caches HTTP requests to improve efficiency.
- **openmeteo_requests**: Interacts with the Open-Meteo API to provide historical weather data.

These libraries collectively support the project's aim to process, enrich, and analyze incident report data, transforming raw PDF documents into a rich, multi-dimensional dataset ready for in-depth analysis.

## Bugs and Assumptions

### Assumptions:
- Addresses that couldn't be geocoded directly have "Norman, OK" appended to improve geocoding success.
- If geocoding fails even with "Norman, OK", cardinal directions are extracted from the address using regex.
- The center of Norman, Oklahoma, is assumed to be at (35.220833, -97.443611) for determining sides of town.
- If the side of town cannot be determined by either geocoding or regex extraction, it is marked as "Could not determine".

### Bugs:
- **Geocoding Limitations**: Accurate latitude and longitude readings may not always be obtained, particularly for non-standard or recently constructed addresses.
- **Regex Limitations**: This method may not always work, especially for addresses deviating from standard naming conventions.
- **Weather Data Acquisition**: Weather data will not be fetched for locations marked as "Could not determine", limiting analysis of environmental factors.
- **Cost of Using Google Maps API**: Multiple accesses or extensive use of the API can result in significant costs, which may limit the frequency or scale of data collection and updates.

## Testing Instructions

To ensure everything is running correctly, activate your virtual environment and use the following command:

```bash
pipenv run python -m pytest
```

This will run all tests to ensure the script's functionality is performing correctly.

### Test Overview

- **`test_calculate_day_of_week`**: Verifies that the `calculate_day_of_week` function correctly calculates the day of the week for each date.
- **`test_calculate_incident_rank`**: Ensures the `calculate_incident_rank` function correctly assigns ranks based on the frequency of incident natures.
- **`test_calculate_time_of_day`**: Checks that the `calculate_time_of_day` function properly extracts the hour of the day from the 'Date/Time' column.
- **`test_calculate_location_rank`**: Ensures the `calculate_location_rank` function accurately assigns ranks to locations based on their frequency of occurrence.
- **`test_extract_nature_column`**: Verifies the `extract_nature_column` function by checking if it accurately extracts the 'Nature' column.
- **`test_calculate_emsstat`**: Confirms the `calculate_emsstat` function correctly identifies EMS-related incidents.
- **`test_side_of_town`**: Verifies the `side_of_town` function, ensuring it accurately determines the side of town for each location.
- **`test_fetch_weather_code_for_df`**: Ensures the `fetch_weather_code_for_df` function correctly accesses and processes weather data to obtain the WMO weather codes.

## Walkthrough Video

A walkthrough video demonstrating the process and visualization can be found here:

[![Walkthrough Video](https://img.youtube.com/vi/your_video_id/maxresdefault.jpg)](https://www.youtube.com/watch?v=your_video_id)

