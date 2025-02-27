# db_connection.py

import pyodbc
from config import read_config
from utils.logger import app_logger as logger  # Import logger

def connect_to_database():
    """Connects to SQL Server using configuration from config.ini"""

    config = read_config()  # Load configuration
    database_configuration = config["database"]

    try:
        # Check if using SQL Authentication or Windows Authentication
        if "username" in database_configuration and "password" in database_configuration:
            # SQL Server Authentication
            connection_string = (
                f"DRIVER={{{database_configuration['driver']}}};"
                f"SERVER={database_configuration['server']};"
                f"DATABASE={database_configuration['database']};"
                f"UID={database_configuration['username']};"
                f"PWD={database_configuration['password']};"
            )
            auth_type = "SQL Authentication"
        else:
            # Windows Authentication
            connection_string = (
                f"DRIVER={{{database_configuration['driver']}}};"
                f"SERVER={database_configuration['server']};"
                f"DATABASE={database_configuration['database']};"
                f"Trusted_Connection=yes;"
            )
            auth_type = "Windows Authentication"

        # Establish Connection
        conn = pyodbc.connect(connection_string)
        logger.info(f"Successfully connected to SQL Server ({auth_type}) - {database_configuration['server']}/{database_configuration['database']}")
        return conn

    except Exception as e:
        logger.error(f"Database connection error: {e}")
        return None

# Test Connection when running this file directly
if __name__ == "__main__":
    connect_to_database()
