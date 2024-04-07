# Datasheets for Datasets

## Motivation ➖

### Q) For what purpose was the dataset created? Was there a specific task in mind? Was there a specific gap that needed to be filled? Please provide a description.

A dataset was created to provide more contextual information for incident reports that were already available to the Norman, Oklahoma City Police Department. The specific objective was to enable detailed analysis by variables such as Day of the Week, Time of the day,Weather, rank of a location, side of the town (eg:- N, S, E, W, NW, NE, SW, SE),Rank of the incident, Nature and whether Emergency Medical Services (EMSSTAT).Tis augmentation helps by preventing contextual knowledge in unstructured data, this breakthrough seeks to provide advanced insights and analytics for public safety, resource allocation, and community awareness.

### Q) Who created the dataset (e.g., which team, research group) and on behalf of which entity (e.g., company, institution, organization)?

This dataset which I am working on was created by an individual or a research group with the aim of enhancing public datasets for broader analyses. The augmentation process was carried out by me independently, not on behalf of any specific entity, but for the benefit of the community, researchers, and policymakers interested in a deeper understanding of local safety and incident patterns (as a part of my assignment 2 in course cis6930sp24).

### Q) Who funded the creation of the dataset? If there is an associated grant, please provide the name of the grantor and the grant name and number.

The augmentation of this dataset was not directly funded by any specific grants or external funding sources. It was a part of course cis6930sp24 which can be help in enhancing further comprehensive analysis.

### Q) Any other comments?

The addition of time, location, and weather information to the dataset enhances its usefulness significantly. It turns the dataset from a basic incident log into a wealth of data that can be examined to find trends, patterns, and possible areas for intervention. The endeavour to enhance this data is indicative of an expanding movement to increase the accessibility and use of public data for a variety of analytical purposes.

## Composition ➖

### Q) What do the instances that comprise the dataset represent?

Images in the dataset represent incidents reported from The Norman, Oklahoma Police Department with additional context. Each instance corresponds to a specific incident report, with information such as incident type, location, date/time, day of week, time of day, weather, zone of location, zone of town, sequence of events , and EMS Status included (EMSSTAT) (EMSSTAT).

### Q) How many instances are there in total?

Total number of instances dependent on the original dataset and the dates/years it has covered we are working on incidents pdfs which are for march 2024 and April 2024 only. And each pds contributes to the cumulative total of instances.

### Q) Is the dataset a sample of instances from a larger set?

The dataset is a carefully chosen portion of the broader collection of all incident reports that the Norman Police Department has made accessible. Although it is thorough in the context of the reports that are now available, reporting and data collection limitations may prevent it from being entirely representative of all incidents that could occur in the given period or location.

### Q) What data does each instance consist of?

Each instance is a selection of "raw" data extracted from a PDF report, enhanced with statistical features such as weather, day of week, etc. This combination provides the content and context of the original report a nice resource for research.

### Q) Is any information missing from individual instances?

Yes, some of the information is missing in the original dataset; it might not be reported and this can affect the augmented data as well.

### Q) Are relationships between individual instances made explicit?

In the augmented data there are relation amounts for the instances for example, Weather is dependent upon Time of Day so that we can get the accurate result and side of the Town and weather is also dependent upon Longitude and latitude of the accurate answers rest are not.

### Q) Are there recommended data splits?

To evaluate the model's prediction performance over time, suggested splits for training, validation, and testing could be based on temporal divisions (e.g., using data from earlier years for training and later years for testing).

### Q) Are there any errors, sources of noise, or redundancies in the dataset?

Potential sources of noise include incorrect incident reporting, changes in the accuracy of weather data, and incorrect geocoding. There may be a reduction in people in the reporting of similar events in nearby space or time. and then this can cause redundancies in the augmented data.

### Q) Is the dataset self-contained, or does it link to external resources?

External features have been added to the data set, primarily for weather information and Side of Town, which uses the city's Google Maps API and Historical Weather API There is no assurance as to the durability of these external features, a depending on availability and long-term stability.

### Q) Does the dataset contain data that might be considered confidential or sensitive?

The augmented data does not have any confidential or sensitive data in it. If names were mentioned in the dataset it would have been confidential data.

### Q) Any other comments?

This dataset represents an innovative way to enrich public safety datasets with contextual information to enable detailed analysis. This is a step towards using open data to increase community awareness and safety measures through data-driven insights.

## Collection Process

### Q) How was the data associated with each instance acquired?

Data for each sample were obtained directly from publicly available PDF reports published by the Norman, Oklahoma Police Department. These reports included incidents, arrests, and activities observed by police and recorded in chronological order. Enhancements, such as weather and city features, were made using external APIs (e.g.Historical Weather API), and the rest were derived from Python libraries (e.g., Panda for datetime manipulation) based on existing data.

### Q) What mechanisms or procedures were used to collect the data?

The initial incident was collected through the police department’s operations system and documented in a PDF report. The improvement plan included the following:

Analysis of PDF documents to extract structured data using libraries such as PyMuPDF (Fitz).
Geocoding connections to latitude and longitude using the Google Maps API.
To retrieve historical weather data using the Historical Weather API.
Each step in this process was automated using Python scripts, ensuring accuracy and repeatability of data development.

### Q) If the dataset is a sample from a larger set, what was the sampling strategy?

The data set contains all available incident reports published by the Norman, Oklahoma Police Department at a particular point in time rather than a sample from a larger cohort so the purpose of the data set is comprehensive on data from of the source.

### Q) Who was involved in the data collection process and how were they compensated?

The initial data collection (i.e., the recording of incidents) was conducted by the police officers as part of their regular duties. The data augmentation process was carried out by me with the help of a pre-existing dataset and external api s.

### Q) Over what timeframe was the data collected?

The data was collected by the Norman, Oklahoma police department for the duration of March 2024 and April 2024 under section Daily Activity Reports. Data augmentation is also done over this duration.

### Q) Were any ethical review processes conducted?

As the dataset is derived from publicly available reports published by a government agency and enhanced by publicly accessible APIs for climate and geographic data, specific ethical review processes transcend conduct standard measures of goodness may apply to the use of public data

### Q) Does the dataset relate to people?

Data is not directly related to people because names are not mentioned it is indirectly related to them because of the data it contains. The dataset's primary goal is to examine incident patterns and trends rather than to identify specific individuals.

### Q) Did you collect the data from the individuals in question directly, or obtain it via third parties or other sources?

Information was obtained from publicly available reports from third parties, notably the Norman, Oklahoma Police Department, and enriched using external APIs for weather forecasting and geocoding.

### Q) Were the individuals in question notified about the data collection?

Not Applicable

### Q) Did the individuals in question consent to the collection and use of their data?

Not aware about this.

### Q) If consent was obtained, were the consenting individuals provided with a mechanism to revoke their consent in the future or for certain uses?

Not Applicable

### Q) Has an analysis of the potential impact of the dataset and its use on data subjects (e.g., a data protection impact analysis) been conducted?

Not aware about this.

### Q) Any other comments?

NO

## Preprocessing/cleaning/labeling

### Q) Was any preprocessing/cleaning/labeling of the data done?

Yes, a lot of preprocessing, cleaning and labeling steps were done.

PDF Parsing: The "raw" data, in the form of a PDF report, was parsed to extract information. This involved identifying and removing restricted items related to the event, such as date, time, location, nature of the event, and so on.

Geocoding: Using the Google Maps API, locations mentioned in the events were converted to latitude and longitude coordinates, enabling geographic analysis

Augmentation of weather data: Historical weather data based on timestamps and event locations were introduced in order to augment the data with weather conditions at the time and place of each event

Using date and time: Time stamps were formatted in reports and used to access additional features such as day of week and time of day

Notation and Classification: Events were named based on their type, and similar cases were grouped or categorized for analysis.

Control for missing values: Models with missing or incomplete data were processed to determine whether conclusions could be drawn or needed to be excluded from an analysis.

### Q) Was the “raw” data saved in addition to the preprocessed/cleaned/labeled data?

The "raw" PDF report is publicly available on the Norman, Oklahoma Police Department website. These act as raw data sources. The preprocessing and enhancement processes transform this data into a program for analysis, but the original PDF remains accessible for future reference or use.

### Q) Is the software used to preprocess/clean/label the instances available?

The software or scripts commonly used to preprocess, clean and label data are mainly publicly available tools and libraries, such as Python, PyMuPDF (for PDF parsing), and APIs such as Google Maps and Historical Weather api for geocoding and weather data.

### Q) Any other comments?

NO.

## Distribution

### Q) Has the dataset been used for any tasks already?

The augmented dataset obtained from the police department reports in Norman, Oklahoma has been mainly utilised for analytical and research objectives. Its goals include analysing crime trends, determining how weather affects crime rates, and assessing the distribution of law enforcement resources. Time-series analysis may be used to spot patterns over time; geospatial analysis can be used to comprehend how crimes are distributed throughout various regions; and correlation analysis can be used to look at the connection between crime rates and weather.

### Q) Is there a repository that links to any or all papers or systems that use the dataset?

I was not able to find any repository or links of papers which have utilized this dataset.

### Q)What (other) tasks could the dataset be used for?

With the combination of original dataset and augmented dataset a Machine learning model can be made to predict crime occurrences or hotspots based on historical data and external factors like weather.

### Q) Is there anything about the composition of the dataset or the way it was collected and preprocessed/cleaned/labeled that might impact future uses?

Methods of data collection and preprocessing, particularly geocoding and weather data enhancement, are dependent on external APIs and services that may introduce biases or inaccuracies:

There are errors or inaccuracies in geocoding, especially in areas with complex geographic information or insufficient map data.
Incorrect weather data for historical dates or times, or weather data of a granularity that does not match the exact location and time of events
Future implementations should consider these potential limitations and ensure the validity of critical data points for sensitive analysis. In order to minimize the risks of inappropriate behavior or speculation, users should exercise strict ethical considerations and integrity when analyzing data or drawing conclusions, especially in cases affecting individuals or communities.

### Q) Are there tasks for which the dataset should not be used?

Given its nature, the dataset should not be used for the following.
targeting or identifying a specific individual while maintaining confidentiality and legal restrictions.
Judicial, legislative, or policy-making relies solely on human observation despite the possibility of
bias-related errors.

### Q) Any other comments?

Users must approach studies with caution and responsibility, considering the possible sensitivity and ethical implications surrounding crime data and its usage. This will help to ensure that their work does not unintentionally cause harm to persons or communities. Risks related to using the dataset can be reduced with the support of openness to criticism and correction, ethical evaluation of planned uses, and transparency in methodology.

## Maintenance:-

### Q) Who will be supporting/hosting/maintaining the dataset?

I will be responsible for the hosting and maintaining augmented dataset if required.

### Q) How can the owner/curator/manager of the dataset be contacted?

For original dataset the curator can be contacted with the help of desired email id or phone number and for the augmented part i can be the contact person with email (sharmapratham@ufl.edu)

### Q) Is there an erratum?

NA

### Q) Will the dataset be updated?

Dataset may be updated to correct any errors, incorporate new instances, or reflect changes in the data collection environment.

### Q) Are there applicable limits on the retention of the data associated with the instances?

Data retention policies will affect the nature of the data, especially if it includes personal or sensitive information. The business must comply with any legal requirements and ethical guidelines regarding data retention and privacy.In the augmented data no such personal or sensitive information is used.

### Q) Will older versions of the dataset continue to be supported/hosted/maintained?

Yes if we are using version control tools like GitHub, Zenodo or etc These platforms allow users to access specific versions of the dataset cited in academic publications or used in analyses, ensuring that the data remains available and usable for future research.

### Q) If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?

Yes, definitely if people want to extend/augment/build on/contribute to the dataset they can do so, the dataset is hosted on GitHub and collaborations are welcomed.

### Q) Any other comments?

NO.
