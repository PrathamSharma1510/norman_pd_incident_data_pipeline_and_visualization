import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import sys
import os
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your existing functions from assignment2.py
from assignment2 import extract_incidents_from_pdf, download_pdf, ensure_geocoding, side_of_town, calculate_time_of_day, create_augmented_dataframe

# Create a cache directory for temporary files
CACHE_DIR = os.path.join(os.path.dirname(__file__), '..', 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

# Configure caching for better performance
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_data_from_urls(urls):
    all_incidents_df = pd.DataFrame()

    for url in urls:
        try:
            pdf_path = download_pdf(url)
            incidents_df = extract_incidents_from_pdf(pdf_path)
            all_incidents_df = pd.concat([all_incidents_df, incidents_df], ignore_index=True)
        except Exception as e:
            st.warning(f"Failed to process {url}: {e}")

    return all_incidents_df

@st.cache_data(ttl=3600)  # Cache data for 1 hour
def generate_urls(start_date, end_date):
    base_url = "https://www.normanok.gov/sites/default/files/documents/"
    current_date = start_date
    urls = []
    while current_date <= end_date:
        url = base_url + current_date.strftime("%Y-%m") + "/" + current_date.strftime("%Y-%m-%d") + "_daily_incident_summary.pdf"
        urls.append(url)
        current_date += timedelta(days=1)
    return urls

def show_correlation_matrix(df):
    st.subheader("Correlation Matrix 📊")
    st.write("This heatmap shows the correlation between various numerical attributes in the incident data. Darker colors indicate higher correlation.")
    numeric_df = df.select_dtypes(include=['float64', 'int64'])
    corr = numeric_df.corr()
    fig, ax = plt.subplots()
    sns.heatmap(corr, ax=ax, annot=True, cmap='coolwarm')
    st.pyplot(fig)

def search_and_highlight(df):
    st.subheader("Search and Highlight 🔍")
    st.write("Use this tool to search for specific incidents based on a chosen attribute.")
    columns = df.columns.tolist()
    search_column = st.selectbox("Select column to search within", columns, index=0)
    search_term = st.text_input("Enter search term")
    if search_term:
        filtered_df = df[df[search_column].astype(str).str.contains(search_term, case=False, na=False)]
        st.write(f"### Search Results for '{search_term}' in column '{search_column}'")
        st.dataframe(filtered_df)
    else:
        st.dataframe(df)
    return search_term

def incident_clustering(df):
    st.subheader("Incident Clustering 🗺️")
    st.write("This scatter plot shows the clustering of incidents based on their geographical location. Different colors represent different clusters.")
    n_clusters = st.slider("Select number of clusters", 2, 10, 3)
    kmeans = KMeans(n_clusters=n_clusters)
    df = df.dropna(subset=['Latitude', 'Longitude'])
    df['Cluster'] = kmeans.fit_predict(df[['Latitude', 'Longitude']])
    fig = px.scatter_geo(df, lat='Latitude', lon='Longitude', color='Cluster', 
                        title='Incident Clusters',
                        scope='usa',
                        projection='albers usa')
    st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Norman Police Incident Data", page_icon="🚓", layout="wide")

    st.title("🚓 Norman Police Incident Data Fetcher")
    st.markdown("## Fetch and visualize incident data from the Norman Police Department.")

    # Add information card at the top
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info("📅 Available date range: March 1-31, 2025")
        with col2:
            if 'all_incidents_df' in st.session_state and not st.session_state.all_incidents_df.empty:
                df = st.session_state.all_incidents_df
                total_incidents = len(df)
                unique_natures = df['Nature'].nunique()
                most_common = df['Nature'].mode()[0]
                info_text = f"""📊 Data Statistics:
- Total Incidents: {total_incidents}
- Unique Incident Types: {unique_natures}
- Most Common: {most_common}"""
                st.info(info_text)
            else:
                st.info("📊 Total Incidents: No data loaded")
        with col3:
            if 'augmented_df' in st.session_state:
                df = st.session_state.augmented_df
                info_text = f"""✨ Augmented Data Details:
- Geocoded Locations
- Weather Data Added
- Time Analysis Added"""
                st.info(info_text)
            else:
                st.info("✨ Data Status: Raw")

    with st.sidebar:
        st.header("Settings ⚙️")
        st.warning("The date range should be between 03/01/2025 and 03/31/2025 only.")
        st.warning("Fetching data for multiple dates may take more time. For a better experience, please use a single date.")

        # Input date range with better UI
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Start Date", datetime(2025, 3, 1))
        with col2:
            end_date = st.date_input("End Date", datetime(2025, 3, 1))

    if 'all_incidents_df' not in st.session_state:
        st.session_state.all_incidents_df = pd.DataFrame()

    if st.sidebar.button("Fetch Data 🗂️"):
        if start_date > end_date:
            st.sidebar.error("End Date must be after Start Date")
        elif start_date < datetime(2025, 3, 1).date() or end_date > datetime(2025, 3, 31).date():
            st.sidebar.error("Please select dates between March 1, 2025 and March 31, 2025")
        elif (end_date - start_date).days > 3:
            st.sidebar.error("The selected date range is too large and may cause delays in data augmentation. Please select a range less than 3 days.")
        else:
            with st.spinner('Fetching data... This might take a few minutes.'):
                # Use cached function for better performance
                urls = generate_urls(start_date, end_date)
                all_incidents_df = fetch_data_from_urls(urls)
                if not all_incidents_df.empty:
                    st.session_state.all_incidents_df = all_incidents_df
                    st.success('Data fetched successfully!')
                else:
                    st.error('No data was fetched. Please check the date range and try again.')

    if not st.session_state.all_incidents_df.empty:
        st.subheader("Extracted Data 📄")
        st.dataframe(st.session_state.all_incidents_df)

        # Button to augment data
        if st.sidebar.button("Augment Data 🔧"):
            try:
                with st.spinner('Augmenting data... This might take a few minutes, please stay tight.'):
                    api_key = st.secrets["api"]["key"]
                    if not api_key:
                        st.error("API key not found. Please check your configuration.")
                        return
                    
                    # Use cached functions for better performance
                    all_incidents_df = ensure_geocoding(st.session_state.all_incidents_df, api_key)
                    all_incidents_df = side_of_town(all_incidents_df)
                    all_incidents_df = calculate_time_of_day(all_incidents_df)
                    create_augmented_dataframe(all_incidents_df)
                    
                    # Validate augmented data
                    required_columns = ['Latitude', 'Longitude', 'Time of Day', 'Day of Week', 'Side of Town', 'WMO Code']
                    missing_columns = [col for col in required_columns if col not in all_incidents_df.columns]
                    if missing_columns:
                        st.warning(f"Some augmented data is missing: {', '.join(missing_columns)}")
                    
                    st.session_state.augmented_df = all_incidents_df
                    st.success('Data augmented successfully!')
            except Exception as e:
                st.error(f"Error during data augmentation: {str(e)}")

    if 'augmented_df' in st.session_state:
        st.subheader("Augmented Data 📊")
        st.dataframe(st.session_state.augmented_df)

        st.markdown("## Visualizations 📊")
        if 'selected_types' not in st.session_state:
            # Select the top 4 most frequent incident types initially
            initial_types = st.session_state.augmented_df['Nature'].value_counts().head(4).index.tolist()
            st.session_state.selected_types = initial_types

        # Incident Frequency by Time of Day as a Heatmap
        st.subheader("Incident Frequency by Time of Day 🕒")
        st.write("This heatmap shows the frequency of incidents at different times of the day and days of the week.")
        time_of_day_heatmap = st.session_state.augmented_df.groupby(['Day of Week', 'Time of Day']).size().unstack().fillna(0)
        fig = px.imshow(time_of_day_heatmap, labels={'color':'Incident Count'}, x=time_of_day_heatmap.columns, y=time_of_day_heatmap.index)
        fig.update_layout(title='Incident Frequency by Time of Day', xaxis_title='Hour of the Day', yaxis_title='Day of the Week')
        st.plotly_chart(fig)

        # Incident Types and Their Frequencies
        st.subheader("Incident Types and Their Frequencies 📋")
        st.write("This bar chart shows the frequency of different types of incidents.")
        incident_types = st.session_state.augmented_df['Nature'].unique()
        selected_types = st.multiselect('Select Incident Types to Display', incident_types, default=st.session_state.selected_types)
        st.session_state.selected_types = selected_types

        if selected_types:
            filtered_df = st.session_state.augmented_df[st.session_state.augmented_df['Nature'].isin(selected_types)]
            incident_counts = filtered_df['Nature'].value_counts().reset_index()
            incident_counts.columns = ['Nature', 'count']
            fig = px.bar(incident_counts, x='Nature', y='count', labels={'Nature':'Incident Type', 'count':'Number of Incidents'})
            fig.update_layout(title='Incident Types and Their Frequencies', xaxis_title='Incident Type', yaxis_title='Number of Incidents')
            st.plotly_chart(fig)

        # Geographic Distribution of Incidents
        st.subheader("Geographic Distribution of Incidents 🗺️")
        st.write("This map shows the geographic distribution of incidents.")
        map_df = st.session_state.augmented_df[['Latitude', 'Longitude']].rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})
        if not map_df.empty:
            st.map(map_df)
        else:
            st.write("No geographic data available.")

        # Weather Conditions During Incidents
        st.subheader("Weather Conditions During Incidents 🌤️")
        st.write("This pie chart shows the distribution of weather conditions during the incidents.")
        weather_counts = st.session_state.augmented_df['WMO Code'].value_counts().reset_index()
        weather_counts.columns = ['WMO Code', 'count']
        fig = px.pie(weather_counts, values='count', names='WMO Code', title='Weather Conditions During Incidents')
        st.plotly_chart(fig)

        # Side of Town Analysis
        st.subheader("Side of Town Analysis 🏙️")
        st.write("This bar chart shows the number of incidents occurring on different sides of the town.")
        side_counts = st.session_state.augmented_df['Side of Town'].value_counts().reset_index()
        side_counts.columns = ['Side of Town', 'count']
        fig = px.bar(side_counts, x='Side of Town', y='count', labels={'Side of Town':'Side of Town', 'count':'Number of Incidents'})
        fig.update_layout(title='Side of Town Analysis', xaxis_title='Side of Town', yaxis_title='Number of Incidents')
        st.plotly_chart(fig)

        # Correlation Matrix
        show_correlation_matrix(st.session_state.augmented_df)

        # Search and Highlight
        search_and_highlight(st.session_state.augmented_df)

        # Incident Clustering
        incident_clustering(st.session_state.augmented_df)

if __name__ == "__main__":
    main()
