# utils/utis.py

import os
import cv2
from utils.model import load_model
from config import read_config
from utils.logger import app_logger as logger

# Load configuration
config = read_config()
model = load_model()

IMAGE_DIR = config["paths"]["image_dir"]

def save_figure(image_name):
    """Detects and extracts the first figure from the image."""
    
    # Construct full image path using IMAGE_DIR
    image_path = os.path.join(IMAGE_DIR, image_name)

    if not os.path.exists(image_path):
        logger.error(f"Image not found at {image_path}")
        raise FileNotFoundError(f"Image not found at {image_path}")

    logger.info(f"Processing image: {image_path}")
    image = cv2.imread(image_path)

    if model is None:
        logger.error("Model is not loaded. Cannot process image.")
        return None

    try:
        layout = model.detect(image)
        first_figure = next((element for element in layout if element.type == "Figure"), None)

        if first_figure:
            x1, y1, x2, y2 = map(int, first_figure.coordinates)
            x1 = max(0, x1 - 50)  # Adjust x1

            cropped_figure = image[y1:y2, x1:x2]

            # Save cropped figure back to IMAGE_DIR
            figure_path = os.path.join(IMAGE_DIR, image_name.replace(".jpg", "_graph.jpg"))
            cv2.imwrite(figure_path, cropped_figure[..., ::-1])

            logger.info(f"Figure extracted and saved at {figure_path}")
            return figure_path
        else:
            logger.warning(f"No figure detected in image: {image_path}")

    except Exception as e:
        logger.error(f"Error processing image {image_name}: {e}")
    
    return None
