# app.py

import streamlit as st
from utils.pdf_extractor import extract_text_from_pdf, extract_images_from_pdf, extract_table_from_text
from utils.utils import save_figure
from sql_queries.save_table_to_db import save_table_to_db
import os
from config import read_config
from utils.logger import app_logger as logger

# Load config
config = read_config()
UPLOAD_DIR = config["paths"]["upload_dir"]
IMAGE_DIR = config["paths"]["image_dir"]
TABLE_NAME = config["database"]['table_name']

st.title("📄 PDF Processor: Extract Images & Data")

# File Upload
uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file:
    try:
        # Save uploaded file
        pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())
        logger.info(f"PDF file saved: {pdf_path}")

        # Extract first page image
        image_path = extract_images_from_pdf(pdf_path)
        if image_path:
            logger.info(f"Image extracted: {image_path}")
        else:
            logger.warning("No images found in PDF.")

        # Detect and extract figure
        figure_path = save_figure(os.path.basename(image_path)) if image_path else None
        if figure_path:
            logger.info(f"Figure extracted: {figure_path}")
        else:
            logger.warning("No figure detected in the extracted image.")

        # Extract text and table
        text = extract_text_from_pdf(pdf_path)
        df = extract_table_from_text(text)
        table_saved = False


        if df is not None:
            
            logger.info("Table extracted successfully.")
            table_saved = save_table_to_db(df, table_name=TABLE_NAME)

            if table_saved:
                logger.info("Data saved to the Database")
                
            else:
                logger.error("Data not saved to Database")
                

        else:
            logger.warning("No tabular data detected in the PDF.")

        # Layout for Table (Left) & Image (Right)
        col1, col2 = st.columns([1, 1])

        with col1:  # Left: Table
            st.subheader("📊 Extracted Table Data")
            if df is not None:
                st.dataframe(df)

                if table_saved:
                    st.success("Data saved to the database")
                else:
                    st.error("⚠ Table data was extracted but could not be saved to the database.")

            else:
                st.warning("⚠ No tabular data detected.")

        with col2:  # Right: Figure
            st.subheader("📷 Extracted Figure")
            if figure_path:
                st.image(figure_path, caption="Extracted Figure", use_container_width =True)
            else:
                st.warning("⚠ No figure detected.")

    except Exception as e:
        logger.error(f"Error processing PDF: {e}")
        st.error(f"An error occurred: {e}")

