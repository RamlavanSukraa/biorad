# config.py


import configparser
import os
from utils.logger import app_logger as logger

def read_config():
    # Initialize the config parser
    configuration = configparser.ConfigParser()
    configuration_path = os.path.join(os.path.dirname(__file__), 'config.ini')

    # Validate if config.ini exists
    if not os.path.exists(configuration_path):
        logger.error("config.ini file not found!")
        raise FileNotFoundError("config.ini file not found!")

    # Read the configuration file
    configuration.read(configuration_path)

    try:
        # Get paths from config
        UPLOAD_DIR = configuration["PATHS"]["UPLOAD_DIR"]
        IMAGE_DIR = configuration["PATHS"]["IMAGE_DIR"]
        MODEL_PATH = configuration["PATHS"]["MODEL_PATH"]

        # Ensure directories exist
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        os.makedirs(IMAGE_DIR, exist_ok=True)
        logger.info("Directories validated and created if not existing.")

        # Extract database configurations
        database_configuration = {
            "server": configuration["database"]["server"],
            "database": configuration["database"]["database"],
            "driver": configuration["database"]["driver"],
            "table_name": configuration["database"]["table_name"],
        }

        # Check if username and password exist (SQL Authentication)
        if "username" in configuration["database"] and "password" in configuration["database"]:
            database_configuration["username"] = configuration["database"]["username"]
            database_configuration["password"] = configuration["database"]["password"]
        else:
            database_configuration["trusted_connection"] = configuration["database"].get("trusted_connection", "yes")

        logger.info("Configuration successfully loaded.")
        return {
            "paths": {
                "upload_dir": UPLOAD_DIR,
                "image_dir": IMAGE_DIR,
                "model_path": MODEL_PATH,
            },
            "database": database_configuration,
        }
    
    except KeyError as e:
        logger.error(f"Missing key in config.ini: {e}")
        raise ValueError(f"Missing key in config.ini: {e}")
