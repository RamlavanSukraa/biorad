# sql_queries/save_table_to_db.py

import numpy as np
from db_connection import connect_to_database  
import pandas as pd
from utils.logger import app_logger as logger

import warnings
warnings.filterwarnings("ignore")  # Suppress all warnings

def save_table_to_db(df, table_name):

    conn = connect_to_database()
    if conn is None:
        logger.error("Database connection failed. Cannot save table.")
        return False

    try:
        cursor = conn.cursor()
        
        # Rename extracted columns to match SQL Server schema
        df = df.rename(columns={
            "Peak Name": "InRs_Map_code",        
            "NGSP %": "NGSP",                    
            "Area %": "InRs_Result",             
            "Retention Time (min)": "InRs_Ret_Time", 
            "Peak Area": "Peak_Area"             
        })

        # Replace '---' and empty strings with NULL
        df.replace({"---": None, "": None}, inplace=True)

        # Convert numeric columns to FLOAT
        numeric_columns = ["NGSP", "InRs_Result", "InRs_Ret_Time", "Peak_Area"]
        for col in numeric_columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)

        # Ensure NULL values remain NULL for SQL insertion
        df = df.replace({np.nan: None})

        # Insert Only Extracted Columns into SQL Server
        for _, row in df.iterrows():
            cursor.execute(
                f"""
                INSERT INTO {table_name} 
                (InRs_Map_code, NGSP, InRs_Result, InRs_Ret_Time, Peak_Area)
                VALUES (?, ?, ?, ?, ?)
                """, 
                row["InRs_Map_code"],  
                row["NGSP"],           
                row["InRs_Result"],    
                row["InRs_Ret_Time"],  
                row["Peak_Area"]       
            )

        conn.commit()
        logger.info(f"Data successfully inserted into {table_name}")
        return True

    except Exception as e:
        logger.error(f"Error saving table to database: {e}")
        return False

    finally:
        conn.close()
