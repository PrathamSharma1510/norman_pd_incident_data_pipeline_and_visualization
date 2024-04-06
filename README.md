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

### Example :- 

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
Understanding the weather conditions at the time of each incident adds another layer of context to the analysis. To achieve this, the project taps into a Historical Weather API, fetching weather conditions based on the date, time, and geographic coordinates of each incident. Specifically, the project retrieves the WMO (World Meteorological Organization) code, which represents a standardized weather condition. This integration allows for the examination of how weather might influence the occurrence or nature of incidents, providing a fuller picture of the circumstances surrounding each event.

### Data Augmentation and Analysis
By enriching the incident data with geographic and weather information, the project facilitates a multifaceted analysis of public safety incidents. Analysts can explore patterns such as the frequency of certain types of incidents in specific locations, times of day, days of the week, or under certain weather conditions. This augmented dataset supports a wide range of analyses—from spatial distribution of incidents across different parts of town to temporal patterns in relation to weather conditions—offering insights that can inform public safety strategies and resource deployment.

This process exemplifies how combining data from various sources, including API-driven external datasets, can significantly enhance the value of the original data, providing a comprehensive understanding of incidents for more informed decision-making.

## Tools and Libraries Used

This project leverages a variety of tools and Python libraries to process, enrich, and analyze incident report data. Below is a brief overview of each component and its role in the project:

- **argparse**: Used for parsing command-line options and arguments. This library facilitates the user interface for running the script with specific input parameters.

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

- **retry_requests**: Implements retry logic for HTTP requests, enhancing the robustness of web service calls by retrying failed requests.

- **openmeteo_requests**: A custom implementation (assumed for the context of this explanation) for interacting with the Open-Meteo API, which provides historical weather data necessary for the project.

- **timedelta**: Part of the datetime module, used to represent differences in dates and times (durations). This project utilizes timedelta for time-based calculations and manipulations.

Each of these components plays a vital role in the project's ability to process raw data, enrich it with additional context, and prepare it for a comprehensive analysis.

For your README, here's how you could describe running the tests and provide an overview of each test function:

```markdown
## Testing Instructions

When you wanna make sure everything's running like it should, just pop into your virtual environment and hit this up:

```bash
pipenv run python -m pytest
```

It'll run through all the checks to make sure the script's functionality is performing correctly.

## Test Overview

### `test_calculate_day_of_week`
This test verifies that the `calculate_day_of_week` function correctly calculates the day of the week for each date in the DataFrame, ensuring Sunday=1 through Saturday=7.

### `test_calculate_incident_rank`
Tests the `calculate_incident_rank` function to ensure it correctly assigns ranks based on the frequency of incident natures. Incidents with the same nature should receive the same rank, with more frequent natures receiving a lower rank number.

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


These tests collectively ensure that each component of the script functions as expected, covering key functionalities from processing incident data to augmenting it with additional insights such as incident ranks, day of the week, and geographical information.
```
