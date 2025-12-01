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

# Data directory and file path for persistent storage
DATA_DIR = os.path.join(os.path.dirname(__file__), '..', 'data')
DATA_FILE = os.path.join(DATA_DIR, 'incident_history.csv')

def get_available_pdfs():
    """List all PDF files in the data directory."""
    if not os.path.exists(DATA_DIR):
        return []
    return sorted([f for f in os.listdir(DATA_DIR) if f.endswith('.pdf')])

def get_available_dates():
    """Extract available dates from PDF filenames in the data directory."""
    pdf_files = get_available_pdfs()
    dates = []
    for filename in pdf_files:
        # Expected format: YYYY-MM-DD_daily_incident_summary.pdf
        try:
            date_str = filename.split('_')[0]  # Get YYYY-MM-DD part
            date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
            dates.append(date_obj)
        except (ValueError, IndexError):
            continue
    return sorted(dates)

def get_pdf_for_date(selected_date):
    """Get the PDF filename for a given date."""
    date_str = selected_date.strftime('%Y-%m-%d')
    return f"{date_str}_daily_incident_summary.pdf"

def load_existing_data():
    """Load historical data from the CSV file."""
    if os.path.exists(DATA_FILE):
        try:
            return pd.read_csv(DATA_FILE)
        except Exception as e:
            st.error(f"Error loading history: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(df):
    """Save the dataframe to the persistent CSV file."""
    try:
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

# Configure caching for better performance
@st.cache_data(ttl=3600)  # Cache data for 1 hour
def fetch_data_from_urls(urls):
    all_incidents_df = pd.DataFrame()

    for url in urls:
        try:
            # Derive a filename from the URL so each day is stored uniquely
            filename = url.split('/')[-1]
            local_path = os.path.join(CACHE_DIR, filename)
            
            # Only download if we don't already have it
            if not os.path.exists(local_path):
                download_pdf(url, save_path=local_path)
                pdf_path = local_path
            else:
                pdf_path = local_path

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

    st.title("🚓 Norman Police Incident Data Analyzer")
    st.markdown("Analyze and visualize incident data from the Norman Police Department")
    st.markdown("---")

    # Add information cards at the top
    available_dates = get_available_dates()
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if available_dates:
                date_range = f"{available_dates[0].strftime('%b %d, %Y')} to {available_dates[-1].strftime('%b %d, %Y')}"
                st.info(f"📅 **Available Data**\n\n{date_range}\n\n**{len(available_dates)} days** of data available")
            else:
                st.info("📅 **Available Data**\n\nNo data files found")
        
        with col2:
            if 'all_incidents_df' in st.session_state and not st.session_state.all_incidents_df.empty:
                df = st.session_state.all_incidents_df
                total_incidents = len(df)
                unique_natures = df['Nature'].nunique()
                st.success(f"📊 **Loaded Data**\n\n**{total_incidents:,}** incidents\n\n**{unique_natures}** unique types")
            else:
                st.info("📊 **Loaded Data**\n\nNo data loaded yet\n\nSelect dates and click 'Load Data'")
        
        with col3:
            if 'augmented_df' in st.session_state and not st.session_state.augmented_df.empty:
                df = st.session_state.augmented_df
                most_common = df['Nature'].mode()[0] if not df['Nature'].mode().empty else "N/A"
                st.success(f"✨ **Data Status**\n\n**Augmented** ✓\n\nMost common: *{most_common}*")
            else:
                if 'all_incidents_df' in st.session_state and not st.session_state.all_incidents_df.empty:
                    st.warning("✨ **Data Status**\n\n**Raw Data**\n\nClick 'Augment Data' for enhanced analysis")
                else:
                    st.info("✨ **Data Status**\n\nNo data to augment")
    
    st.markdown("---")

    with st.sidebar:
        st.header("Settings ⚙️")
        
        # Get available dates from the data directory
        available_dates = get_available_dates()
        
        if not available_dates:
            st.error("No PDF files found in the 'data' folder.")
            selected_dates = []
        else:
            st.info(f"📅 Available dates: {len(available_dates)}")
            
            # Option to select all dates
            select_all = st.checkbox("Select All Dates", value=False)
            
            if select_all:
                selected_dates = available_dates
                st.success(f"✓ All {len(available_dates)} dates selected")
            else:
                # Date range picker (default to first date only)
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input(
                        "From Date",
                        value=available_dates[0],
                        min_value=available_dates[0],
                        max_value=available_dates[-1]
                    )
                with col2:
                    end_date = st.date_input(
                        "To Date",
                        value=available_dates[0],  # Default to first date only
                        min_value=available_dates[0],
                        max_value=available_dates[-1]
                    )
                
                # Filter dates based on range
                selected_dates = [d for d in available_dates if start_date <= d <= end_date]
                
                if selected_dates:
                    st.info(f"📊 {len(selected_dates)} date(s) selected")
                else:
                    st.warning("No dates in selected range")
            
            # Show warning if multiple dates are selected
            if len(selected_dates) >= 3:
                st.warning("⚠️ Processing multiple dates may take significant time, especially during data augmentation.")

    if 'all_incidents_df' not in st.session_state:
        st.session_state.all_incidents_df = pd.DataFrame()

    if st.sidebar.button("Load Selected Data 🗂️"):
        if not selected_dates:
            st.sidebar.error("Please select at least one date.")
        else:
            with st.spinner('Processing selected dates...'):
                combined_df = pd.DataFrame()
                
                for selected_date in selected_dates:
                    filename = get_pdf_for_date(selected_date)
                    file_path = os.path.join(DATA_DIR, filename)
                    
                    if os.path.exists(file_path):
                        try:
                            # Extract data from each selected PDF
                            incidents_df = extract_incidents_from_pdf(file_path)
                            combined_df = pd.concat([combined_df, incidents_df], ignore_index=True)
                        except Exception as e:
                            st.error(f"Failed to process {filename}: {e}")
                    else:
                        st.warning(f"File not found: {filename}")
                
                if not combined_df.empty:
                    # Remove duplicates
                    combined_df = combined_df.drop_duplicates(subset=['Date/Time', 'Incident Number', 'Location'])
                    
                    st.session_state.all_incidents_df = combined_df
                    st.success(f"Successfully loaded {len(combined_df)} incidents from {len(selected_dates)} date(s)!")
                    
                    # Reset augmented data since raw data changed
                    if 'augmented_df' in st.session_state:
                        del st.session_state.augmented_df
                else:
                    st.error('No data found for the selected dates.')

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
