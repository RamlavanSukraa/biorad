# app.py

import streamlit as st
import pandas as pd
from PIL import Image
from datetime import datetime
import requests
from io import BytesIO  

# Function to display the app
def display_app():
    # Initialize session state for clearing data
    if "clear_data" not in st.session_state:
        st.session_state.clear_data = False  # Default: False (show data)

    # Sample Details DataFrame
    sample_data = {
        'Sample ID': [
            '0100921500', '0100926500', '0100929300', 'ECG220001019', 'INVA2200281',
            'INVA2201894', 'INVA2201895', 'INVA2202275', 'INVA2216296', 'INVA2216298',
            'INVB2203835', 'INVB2238424', 'IPLR220000134', 'OPSC220000035', 'OPSC220000520',
            'PLDOIP22000001', 'PLECG2200004', 'PLINVB22000107', 'PLOPLA22000003', 'PLOPSC22000003'
        ],
        'Position': [2, 4, 3, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None],
        'Result Date': [
            '2024-01-10 12:00:00', '2024-01-10 12:00:00', '2024-01-10 12:00:00', '2022-05-01 12:00:00', '2022-04-04 12:00:00',
            '2022-04-30 12:00:00', '2022-04-30 12:00:00', '2022-05-05 12:00:00', '2022-12-23 12:00:00', '2022-12-23 12:00:00',
            '2022-04-30 12:00:00', '2022-12-23 12:00:00', '2022-04-30 12:00:00', '2022-04-02 12:00:00', '2022-04-30 12:00:00',
            '2022-04-02 12:00:00', '2022-04-02 12:00:00', '2022-04-05 12:00:00', '2022-04-02 12:00:00', '2022-04-02 12:00:00'
        ]
    }

    sample_df = pd.DataFrame(sample_data)
    
    # Convert 'Result Date' column to datetime
    sample_df['Result Date'] = pd.to_datetime(sample_df['Result Date'])

    # Biorad Variant Data DataFrame
    biorad_data = {
        'Peak Name': ['A1a', 'A1b', 'LA1c', 'A1c', 'P3', 'P4', 'Ao'],
        'NGSP %': [None, None, None, 5.6, None, None, None],  # Only A1c has an NGSP % value
        'Area%': [0.9, 1.7, 1.8, None, 3.7, 1.3, 86],  # A1c does not have an Area% value
        'Retention Time (min)': [0.17, 0.243, 0.424, 0.536, 0.804, 0.883, 1.013],
        'Peak Area': [14106, 26837, 27679, 72455, 57415, 20722, 1344884],
        'Comments': ['No Comments'] * 7  # Keeping default comments for all rows
    }

    biorad_df = pd.DataFrame(biorad_data)

    # Load the graph image (chromatogram)
    # chromatogram_image = Image.open(r"C:\Users\Admin\Desktop\chromatogram\chromatogram.png")  # Update the path

    # GitHub raw URL for the image
    github_raw_url = "https://raw.githubusercontent.com/RamlavanSukraa/biorad/main/chromatogram.png"
    
    # Fetch the image from GitHub
    response = requests.get(github_raw_url)
    if response.status_code == 200:
        chromatogram_image = Image.open(BytesIO(response.content))
    else:
        chromatogram_image = None  # Handle the case where the image isn't found



    # Date Filter Layout in the main screen
    st.subheader("Filter Data by Date")

    sample_detail, sample_results, upload, clear = st.columns([2,2,2,1])  # Equal columns for date filters

    min_date = sample_df["Result Date"].min().date()
    max_date = sample_df["Result Date"].max().date()

    with sample_detail:
        start_date = st.date_input("From Date", min_date)

    with sample_results:
        end_date = st.date_input("To Date", max_date)

    with clear:
        if st.button("Clear🧹"):
            st.session_state.clear_data = True  # Set flag to True

    with upload:
        st.file_uploader("Process✅")

    # Convert selected dates to datetime
    start_date = datetime.combine(start_date, datetime.min.time())
    end_date = datetime.combine(end_date, datetime.max.time())

    # Apply filter only if "Clear" is not clicked
    if st.session_state.clear_data:
        filtered_sample_df = pd.DataFrame()  # Empty DataFrame
        biorad_df = pd.DataFrame()  # Empty DataFrame
        st.warning("Data Cleared! 🧹")
    else:
        filtered_sample_df = sample_df[
            (sample_df["Result Date"] >= start_date) & (sample_df["Result Date"] <= end_date)
        ]

    # Layout for 3 columns below date filter
    col1, col2, col3 = st.columns([2, 3, 1.5])

    with col1:
        st.subheader("Sample Details")
        st.dataframe(filtered_sample_df)

    with col2:
        st.subheader("Sample Results")
        st.dataframe(biorad_df)

    with col3:
        st.subheader("Chromatogram")
        if chromatogram_image:
            st.image(chromatogram_image, caption="Chromatogram Graph", use_container_width=True)
        else:
            st.error("Error: Unable to load chromatogram image.")


# Main function to run the app
if __name__ == "__main__":
    st.set_page_config(layout="wide")
    st.title("Bioard Variant Turbo II - Results")
    display_app()
