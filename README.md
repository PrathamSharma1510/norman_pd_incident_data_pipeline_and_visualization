## CIS6930SP24 - Assignment2 - Incident Report Processing

**Name:** Pratham Sharma
**UFID:** 99812068

## Assignment Description

This project is designed to process and augment data from incident reports from the Norman, Oklahoma City Police Department. It extracts events from PDF files, uses the Google Maps API to geocode the locations of these events, based on geocoded coordinates shows parts of the city for each event, calculates events and location groups, assigns weather information to the data goes ahead at each time and event using the Historical Weather API. The goal is to provide improved event insights for further analysis.

## How to Run the Code

## Installation Instructions

Ensure that you have a `pipenv` installed. If not, install it using command :- `pip install pipenv`. Now, set up the project environment with command:

```
pipenv install
```

## How to Run the code

To execute the code following command is used:

```
python main.py --urls <path_to_file_with_pdf_urls>
```

Replace `<path_to_file_with_pdf_urls>` with the path to a text file containing URLs of the PDF files to be processed, one URL per line.

 Example :- 

```
python main.py --urls pdf_urls.txt
```

This command will process the PDFs listed in `pdf_urls.txt`, extract incident data, geocode locations, augment data with side of town and weather information, and output the augmented data in a tab-separated CSV file.

## Functions Overview


A set of tools for extracting, processing, and improving incident report data from PDF files are included in this project. An outline of each application function and its goal is provided below:

- **`extract_incidents_from_pdf(pdf_path)`**: Parses PDF files to extract incident report data, structuring it into a pandas DataFrame for further processing.

- **`calculate_location_rank(df)`**: Helps to find places with greater event counts by ranking locations according to the frequency of incidents.

- **`calculate_incident_rank(df)`**: Ranks incident types ('Nature') based on their occurrence frequency, indicating common types of incidents.

- **`calculate_day_of_week(df)`**: Adds a column indicating the day of the week for each incident, aiding in temporal analysis and is then also used in Weather api.

- **`calculate_time_of_day(df)`**: Appends a column for the hour of the day each incident occurred, useful for identifying time-related trends.

- **`extract_nature_column(df)`**: Isolates the 'Nature' column, focusing analysis on the types of incidents reported.

- **`calculate_emsstat(df)`**: Identifies records marked as EMSSTAT or later records that have the same time and place, indicating situations that require emergency medical attention.

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

This project implements a comprehensive framework for enhancing and analyzing incident report data extracted from PDF files. The key step in this process uses advanced APIs and data manipulation techniques to provide a deeper understanding of events. Here is a summary:

### Geocoding with Google Maps API
The project makes use of the Google Maps Geocoding API to provide each incident with additional geographic information. The location text, including addresses, that can be found in incident reports is converted into exact latitude and longitude coordinates using this API. The ensuing spatial analysis, which includes identifying the side of town where occurrences occur, depends on this geocoding stage. The application can analyse incidents in relation to particular geographic locations thanks to the geocoded coordinates, adding spatial insights to the dataset that are crucial for public safety and resource allocation plans.

### Weather Data Integration
Knowing the weather at the time of each incidence gives the study an additional level of context. In order to do this, the project uses a Historical meteorological API to retrieve meteorological information based on each incident's date, time, and geographic locations. In particular, the project returns a standard meteorological condition represented by the WMO (World Meteorological Organisation) code. This integration gives a more complete view of the circumstances surrounding each event by enabling the investigation of how weather may affect the occurrence or character of occurrences.

### Data Augmentation and Analysis
Through the incorporation of weather and geographic data into the event data, the project enables a comprehensive examination of public safety situations. Patterns such as the frequency of particular incidences in particular areas, at particular times of day, on particular days of the week, or in particular weather conditions can be investigated by analysts. The spatial distribution of occurrences across the town and temporal trends in relation to weather conditions are just two examples of the many studies that may be supported by this enhanced dataset, providing insights that help guide the deployment of resources and public safety policies.

This procedure shows how merging data from several sources—including external datasets controlled by APIs—can greatly increase the original data's value and give decision-makers a more thorough picture of situations.

## Tools and Libraries Used

These libraries collectively support the project's aim to process, enrich, and analyze incident report data, transforming raw PDF documents into a rich, multi-dimensional dataset ready for in-depth analysis.
This project processes, enriches, and analyses incident report data using a range of Python packages and tools. An outline of each element and its function in the project is provided below:

- **argparse**: used to parse arguments and options from the command line. This library makes it easier to run the script with particular input parameters through the user interface.

- **urllib.request**: Provides an interface for fetching data from the web. It's used in this project to download PDF files containing incident reports from specified URLs.

- **os**: Offers a way to interact with the operating system. In this project, it's used for path manipulations and to ensure the existence of directories.

- **pandas**: A powerful data manipulation and analysis library for Python. It's used extensively throughout the project to handle dataframes—everything from data extraction to processing and augmenting the data with additional information.

- **fitz (PyMuPDF)**: A library that allows for interaction with PDF files. It's used to extract text from downloaded PDF incident reports.

- **datetime**: Provides classes for manipulating dates and times. This project uses it to handle and transform date and time data, crucial for correlating incidents with weather conditions and other time-based analyses.

- **geopy**: Facilitates geocoding (converting addresses into latitude and longitude coordinates) and other geographical operations. It's particularly useful for enriching the dataset with spatial information.

- **math**: Offers access to mathematical functions. In this project, it's used for calculations related to determining the side of town based on geographic coordinates.

- **requests**: A simple HTTP library for Python, used to make requests to web services like the Google Maps Geocoding API and the Historical Weather API.

- **re (Regular Expression)**: Provides regular expression matching operations. It's used for parsing and extracting specific pieces of data from text.

- **requests_cache**: Enables caching of HTTP requests. This reduces the number of repeated requests made to APIs, improving efficiency and reducing latency.

- **openmeteo_requests**: A custom implementation (assumed for the context of this explanation) for interacting with the Open-Meteo API, which provides historical weather data necessary for the project.

Each of these components plays a vital role in the project's ability to process raw data, enrich it with additional context, and prepare it for a comprehensive analysis.

## Bugs and Assumptions

### Assumptions:
- I have added "Norman, OK" to addresses that could not be geocoded directly in order to determine the side of town. This method provides the geocoding API with more context, which raises the likelihood of successful geocoding.
- When even adding "Norman, OK" would not yield latitude or longitude, I used regex to extract the cardinal directions (if any) straight from the address. For instance, the side of town for an address like "1122 24TH AVE SW" would be determined by extracting the "SW" cardinal direction using regex.
- It is assumed that center of Norman, Oklahoma, is located at (35.220833, -97.443611). Geographic coordinates are used to determine the side of town, with reference to this place.
- The element is indicated as "Could not determine" if the side of town cannot be determined by either regex extraction or geocoding. As a result, the inability to determine the exact location of these incidences will prevent the calculation of the weather.

### Bugs:
- **Geocoding Limitations**: Accurate latitude and longitude readings may not always be obtained by attaching "Norman, OK" to addresses for geocoding, particularly for non-standard or recently constructed addresses.
- **Regex Limitations**: It is assumed that such indications are present and appropriately indicate the side of town when using regex to extract cardinal directions from addresses. This approach might not always work, particularly for addresses that deviate from standard naming conventions or that incorporate the cardinal directions into the street name instead of indicating the location's side of town.
- **Weather Data Acquisition**: The process of fetching weather data is dependent on successfully geocoding each incident location to obtain accurate latitude and longitude values. For locations that are marked as "Could not determine", weather data will not be fetched, which might limit the analysis of environmental factors on incident patterns.
- **Cost of Using Google Maps API** : Utilizing the Google Maps API for geocoding addresses is financially burdensome due to its pricing model. Multiple accesses or extensive use of the API can result in significant costs, which may limit the frequency or scale at which data can be collected and updated.

## Testing Instructions
When you wanna make sure everything's running like it should, just pop into your virtual environment and hit this up:
```markdown
pipenv run python -m pytest
```

It'll run through all the checks to make sure the script's functionality is performing correctly.

## Test Overview

### `test_calculate_day_of_week`
This test verifies that the `calculate_day_of_week` function correctly calculates the day of the week for each date in the DataFrame, ensuring Sunday equals 1 through Saturday equals 7.

### `test_calculate_incident_rank`
Tests the `calculate_incident_rank` function to ensure it correctly assigns ranks based on the frequency of incident natures. Incidents with the same nature should receive the same rank, with more frequent natures receiving a lower rank number (eg:- 1,2).

### `test_calculate_time_of_day`
Checks the `calculate_time_of_day` function to ensure it properly extracts and assigns the hour of the day from the 'Date/Time' column in the DataFrame. This test confirms that the time of day is correctly captured as a numerical hour.

### `test_calculate_location_rank`
This test ensures that the `calculate_location_rank` function accurately assigns ranks to locations based on their frequency of occurrence. Locations that appear more frequently are expected to have a higher rank (lower rank number).

### `test_extract_nature_column`
Verifies the `extract_nature_column` function by checking if it accurately extracts the 'Nature' column from the DataFrame. This test ensures that the extracted column matches the expected series of incident natures.

### `test_calculate_emsstat`
Tests the `calculate_emsstat` function to confirm it correctly identifies EMS-related incidents within the DataFrame. The test checks if the 'EMSSTAT' flag is accurately set for incidents with the 'EMSSTAT' indicator.

### `test_side_of_town`
This test verifies the `side_of_town` function, ensuring that it accurately determines the side of town for each location in the DataFrame based on latitude and longitude. It uses predefined locations to test if the function assigns the correct cardinal direction or side of town.

### `test_fetch_weather_code_for_df`
This test verifies the `fetch_weather_code_for_df` function by checking if the Historical Weather Data is correctly accessed and processed to obtain the WMO weather codes, which are then accurately appended to the dataframe. It ensures that the function can handle real-world data inputs and consistently produce the correct weather classification based on the specified dates and locations.

These tests collectively ensure that each component of the script functions as expected, covering key functionalities from processing incident data to augmenting it with additional insights such as incident ranks, day of the week, and geographical information.

