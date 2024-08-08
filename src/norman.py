import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
from sklearn.cluster import KMeans
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import your existing functions from assignment2.py
from assignment2 import extract_incidents_from_pdf, download_pdf, ensure_geocoding, side_of_town, calculate_time_of_day, create_augmented_dataframe

def generate_urls(start_date, end_date):
    base_url = "https://www.normanok.gov/sites/default/files/documents/"
    current_date = start_date
    urls = []
    while current_date <= end_date:
        url = base_url + current_date.strftime("%Y-%m") + "/" + current_date.strftime("%Y-%m-%d") + "_daily_incident_summary.pdf"
        urls.append(url)
        current_date += timedelta(days=1)
    return urls

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
    fig = px.scatter_mapbox(df, lat='Latitude', lon='Longitude', color='Cluster', mapbox_style="carto-positron", title='Incident Clusters')
    st.plotly_chart(fig)

def main():
    st.set_page_config(page_title="Norman Police Incident Data", page_icon="🚓", layout="wide")

    st.title("🚓 Norman Police Incident Data Fetcher")
    st.markdown("## Fetch and visualize incident data from the Norman Police Department.")

    with st.sidebar:
        st.header("Settings ⚙️")
        st.warning("The date range should be between 07/01/2024 and 07/31/2024 only.")
        st.warning("Fetching data for multiple dates may take more time. For a better experience, please use a single date.")

        # Input date range
        start_date = st.date_input("Start Date", datetime(2024, 7, 1))
        end_date = st.date_input("End Date", datetime(2024, 7, 1))

    if 'all_incidents_df' not in st.session_state:
        st.session_state.all_incidents_df = pd.DataFrame()

    if st.sidebar.button("Fetch Data 🗂️"):
        if start_date > end_date:
            st.sidebar.error("End Date must be after Start Date")
        elif (end_date - start_date).days > 3:
            st.sidebar.error("The selected date range is too large and may cause delays in data augmentation. Please select a range less than 3 days.")
        else:
            urls = generate_urls(start_date, end_date)
            all_incidents_df = fetch_data_from_urls(urls)
            st.session_state.all_incidents_df = all_incidents_df

    if not st.session_state.all_incidents_df.empty:
        st.subheader("Extracted Data 📄")
        st.dataframe(st.session_state.all_incidents_df)

        # Button to augment data
        if st.sidebar.button("Augment Data 🔧"):
            with st.spinner('Augmenting data... This might take a few minutes, please stay tight.'):
                api_key = st.secrets["api"]["key"]  # Replace with your actual API key
                all_incidents_df = ensure_geocoding(st.session_state.all_incidents_df, api_key)
                all_incidents_df = side_of_town(all_incidents_df)
                all_incidents_df = calculate_time_of_day(all_incidents_df)
                create_augmented_dataframe(all_incidents_df)
                
                st.session_state.augmented_df = all_incidents_df
                st.success('Data augmented successfully!')

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

        # 3. Geographic Distribution of Incidents
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

        #  Search and Highlight
        search_and_highlight(st.session_state.augmented_df)

        # Incident Clustering
        incident_clustering(st.session_state.augmented_df)

if __name__ == "__main__":
    main()
