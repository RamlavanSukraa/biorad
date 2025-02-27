# Utils/ PDF extractor

import fitz  # PyMuPDF
import re
import pandas as pd
from pdf2image import convert_from_path
from config import read_config
import os

# Load configuration
config = read_config()
UPLOAD_DIR = config["paths"]["upload_dir"]
IMAGE_DIR = config["paths"]["image_dir"]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file"""
    doc = fitz.open(pdf_path)
    page = doc.load_page(0)
    return page.get_text("text")

def extract_table_from_text(text):
    """Extracts tabular data from text"""
    pattern = re.compile(r"(A1a|A1b|LA1c|A1c|P3|P4|Ao)\s+(---|\d+\.\d+)\s+(---|\d+\.\d+)\s+(\d+\.\d+)\s+(\d+)")
    matches = pattern.findall(text)
    
    if matches:
        return pd.DataFrame(matches, columns=["Peak Name", "NGSP %", "Area %", "Retention Time (min)", "Peak Area"])
    return None

def extract_images_from_pdf(pdf_path):
    """Converts PDF to image"""
    image = convert_from_path(pdf_path)[0]
    filename = os.path.splitext(os.path.basename(pdf_path))[0]
    image_path = os.path.join(IMAGE_DIR, f"{filename}.jpg")
    image.save(image_path, "JPEG")
    return image_path
