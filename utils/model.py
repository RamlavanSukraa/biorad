# Utils/model.py

import torch
from utils.logger import app_logger as logger
from config import read_config
import streamlit as st

# Load configuration
config = read_config()
MODEL_PATH = config["paths"]["model_path"]

@st.cache_resource
def load_model():
    """Loads the Detectron2 model"""
    try:
        model = torch.load(MODEL_PATH, map_location=torch.device("cpu"))
        logger.info(f"Model loaded successfully from: {MODEL_PATH}")
        return model
    except Exception as e:
        logger.error(f"Error loading model: {e}")
        return None

model = load_model()

