# Utils/ PDF extractor

import fitz  # PyMuPDF
import re
import pandas as pd
from pdf2image import convert_from_path
from config import read_config
import os

from utils.logger import app_logger as logger

# Load configuration
config = read_config()
UPLOAD_DIR = config["paths"]["upload_dir"]
IMAGE_DIR = config["paths"]["image_dir"]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF."""
    logger.info(f"Extracting text from PDF: {pdf_path}")
    
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    text = page.get_text("text")
    
    logger.info("Text extraction completed.")
    return text


# def extract_table_from_text(text):
#     """Extracts tabular data from text"""
#     pattern = re.compile(r"(A1a|A1b|LA1c|A1c|P3|P4|Ao)\s+(---|\d+\.\d+)\s+(---|\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)")
#     matches = pattern.findall(text)
    
#     if matches:
#         return pd.DataFrame(matches, columns=["Peak Name", "NGSP %", "Area %", "Retention Time (min)", "Peak Area"])
#     return None


def extract_table_from_text(text):
    """Extract table data from text using regex."""
    logger.info("Extracting table data from text using regex.")
    
    # Extract Sample ID
    sample_id_match = re.search(r"Sample\s*ID\s*:\s*(\d+)", text)
    if sample_id_match:
        sample_id = sample_id_match.group(1)
        logger.info(f"Sample ID found: {sample_id}")
    else:
        sample_id = "Not found"
        logger.warning("Sample ID not found.")

    # Extract Report Generated Date
    report_generated_match = re.search(r"Report\s*Generated\s*:\s*([\d/]+\s*[\d:]+)", text)
    if report_generated_match:
        report_generated = report_generated_match.group(1)
        logger.info(f"Report Generated Date found: {report_generated}")
    else:
        report_generated = "Not found"
        logger.warning("Report Generated Date not found.")

    # Extract Table Data Using Regex
    pattern = re.compile(r"(A1a|A1b|LA1c|A1c|P3|P4|Ao)\s+(---|\d+\.\d+)\s+(---|\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)")
    matches = pattern.findall(text)

    if matches:
        df = pd.DataFrame(matches, columns=["Peak Name", "NGSP %", "Area %", "Retention Time (min)", "Peak Area"])
        logger.info("Table data extracted successfully.")
    else:
        df = None
        logger.warning("No table data found.")

    return df, sample_id, report_generated



def extract_images_from_pdf(pdf_path):
    """Converts PDF to image"""
    image = convert_from_path(pdf_path)[0]
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    image_path = os.path.join(IMAGE_DIR, f"{filename}.jpg")
    image.save(image_path, "JPEG")
    return image_path
