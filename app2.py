# app2.py

import streamlit as st
import os
import pandas as pd

from utils.pdf_extractor import extract_text_from_pdf, extract_images_from_pdf, extract_table_from_text
from utils.utils import save_figure

from sql_queries.save_table_to_db import save_table_to_db
from sql_queries.fetch_data_from_database import fetch_data_from_db

from utils.logger import app_logger as logger
from config import read_config

# Load config
config = read_config()
UPLOAD_DIR = config["paths"]["upload_dir"]
IMAGE_DIR = config["paths"]["image_dir"]
TABLE_NAME = config["database"]['table_name']

# Initialize Streamlit App
st.set_page_config(layout="wide")
st.title("📊 Biorad Variant Turbo II - Results")

# **Initialize Session State** for UI Refresh
if "refresh_data" not in st.session_state:
    st.session_state.refresh_data = False

# **File Upload Section**
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

# **Process Uploaded File**
if uploaded_file:
    try:
        # Save the uploaded PDF
        pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        logger.info(f"PDF saved: {pdf_path}")

        # # Extract first page image
        # image_path = extract_images_from_pdf(pdf_path)
        # figure_path = save_figure(os.path.basename(image_path)) if image_path else None

        # Extract the Image
        image_path = extract_images_from_pdf(pdf_path)

        # If an image path is successfully extracted, detect the image and save the figure
        if image_path is not None:
            figure_path = save_figure(os.path.basename(image_path))
        else:
            figure_path = None # Incase no figure is found


        # Extract Text & Table
        text = extract_text_from_pdf(pdf_path)
        df_extracted, sample_id, report_generated = extract_table_from_text(text)

        table_saved = False

        # Check if the extracted data is valid before saving to the database
        data_is_valid = (
            df_extracted is not None  # Ensure the extracted table is not empty
            and sample_id is not None  # Ensure a sample ID was found
            and report_generated is not None  # Ensure a report date was found
        )

        if data_is_valid:
            table_saved = save_table_to_db(sample_id, report_generated, df_extracted, TABLE_NAME)

            if table_saved:
                logger.info("Data successfully saved to the database.")
                st.session_state.refresh_data = True  # Trigger UI refresh
            else:
                logger.error("Failed to save data to the database.")
        else:
            logger.warning("⚠ Missing required data (table, sample ID, or report date).")


    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        st.error(f"An error occurred: {e}")


# **Fetch Data from Database**
db_data = fetch_data_from_db(TABLE_NAME)

if db_data:
    df_db = pd.DataFrame(db_data)  # Convert to DataFrame

    # **Date Range Selection**
    df_db["InRs_ReqDate"] = pd.to_datetime(df_db["InRs_ReqDate"], errors='coerce')
    df_db = df_db.dropna(subset=["InRs_ReqDate"])

    min_date = df_db["InRs_ReqDate"].min().date()
    max_date = df_db["InRs_ReqDate"].max().date()

    col1, col2 = st.columns([1, 1])
    with col1:
        start_date = st.date_input("From Date", min_date, format="DD/MM/YYYY")
    with col2:
        end_date = st.date_input("To Date", max_date, format="DD/MM/YYYY")

    # Validate Date Selection
    if start_date > end_date:
        st.error("'From Date' cannot be later than 'To Date'.")
    else:
        # **Filter Data by Date Range**
        df_filtered = df_db[
            (df_db["InRs_ReqDate"].dt.date >= start_date) &
            (df_db["InRs_ReqDate"].dt.date <= end_date)
        ]

        # **Sample ID Selection**
        sample_ids = df_filtered["InRs_ReqNo"].unique()
        selected_sample_id = st.selectbox("Select Sample ID", sample_ids)

        # **Filter Data by Sample ID**
        df_sample_details = df_filtered[df_filtered["InRs_ReqNo"] == selected_sample_id].copy()
        df_sample_results = df_sample_details[["InRs_Map_code", "InRs_Ret_Time"]].copy()

        # Rename columns for UI clarity
        df_sample_details.rename(columns={"InRs_ReqNo": "Sample ID", "InRs_ReqDate": "Result Date"}, inplace=True)
        df_sample_results.rename(columns={"InRs_Map_code": "Peak Name", "InRs_Ret_Time": "Retention Time (min)"}, inplace=True)

        # **Display Results**
        col1, col2, col3 = st.columns([1,1,1])

        with col1:
            st.subheader("📋 Sample Details")
            st.dataframe(df_sample_details[["Sample ID", "Result Date", "InRs_Machine", "InRs_Result"]])

        with col2:
            st.subheader("🧪 Sample Results")
            st.dataframe(df_sample_results)

        with col3:
            st.subheader("📈 Chromatogram")
            chromatogram_path = f"{IMAGE_DIR}/{selected_sample_id}_graph.jpg"
            if os.path.exists(chromatogram_path):
                st.image(chromatogram_path, caption="Extracted Figure", use_container_width =True)
            else:
                st.warning("⚠ No chromatogram available.")

else:
    st.warning("⚠ No data available in the database. Please upload a PDF.")

# **Success Message if Data is Saved**
if "refresh_data" in st.session_state and st.session_state.refresh_data:
    st.success("Data saved successfully! Refresh to see updated results.")
    st.session_state.refresh_data = False  # Reset UI trigger
