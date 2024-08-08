import streamlit as st
import pandas as pd
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

def main():
    st.title("Norman Police Incident Data Fetcher")

    st.warning("Please note: The date range should be between 07/01/2024 and 07/31/2024 only.")
    st.warning("Fetching data for multiple dates may take more time. For a better experience, please use a single date.")

    # Input date range
    start_date = st.date_input("Start Date", datetime(2024, 7, 1))
    end_date = st.date_input("End Date", datetime(2024, 7, 1))

    if 'all_incidents_df' not in st.session_state:
        st.session_state.all_incidents_df = pd.DataFrame()

    if st.button("Fetch Data"):
        if start_date > end_date:
            st.error("End Date must be after Start Date")
        elif (end_date - start_date).days > 3:
            st.error("The selected date range is too large and may cause delays in data augmentation. Please select a range less than 3 days.")
        else:
            urls = generate_urls(start_date, end_date)
            all_incidents_df = fetch_data_from_urls(urls)
            st.session_state.all_incidents_df = all_incidents_df

    if not st.session_state.all_incidents_df.empty:
        st.write("### Extracted Data")
        st.dataframe(st.session_state.all_incidents_df)

        # Button to augment data
        if st.button("Augment Data"):
            with st.spinner('Augmenting data... This might take a few minutes, please stay tight.'):
                api_key = 'your_api_key_here'  # Replace with your actual API key
                all_incidents_df = ensure_geocoding(st.session_state.all_incidents_df, api_key)
                all_incidents_df = side_of_town(all_incidents_df)
                all_incidents_df = calculate_time_of_day(all_incidents_df)
                create_augmented_dataframe(all_incidents_df)
                
                st.session_state.augmented_df = all_incidents_df
                st.success('Data augmented successfully!')

    if 'augmented_df' in st.session_state:
        st.write("### Augmented Data")
        st.dataframe(st.session_state.augmented_df)

if __name__ == "__main__":
    main()
