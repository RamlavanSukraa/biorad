
# Import the database connection function
from db_connection import connect_to_database  



def fetch_data_from_db(table_name = "AI_InRs_Interface_Result_T" ):

    
    # Step 1: Connect to the database
    conn = connect_to_database()
    
    if conn is None:
        print(" Failed to connect to the database.")
        return None  # If connection fails, return None
    else:
        print("Database connection successful!")

    # Step 2: Try executing the query
    try:
        cursor = conn.cursor()  # Create a cursor object
        
        query = f"""
        SELECT 
            InRs_Machine, InRs_ReqDate, InRs_ReqNo, InRs_Map_code, 
            InRs_Test_Code, InRs_Test_Sub_Code, InRs_Result, 
            InRs_Act_Result, InRs_ResDate, InRs_ResTime, InRs_Status, 
            InRs_Status_DT, InRs_Accept_Status, InRs_Ret_Time, InRs_SlNo
        FROM {table_name}
        """
        
          # SQL query to fetch specific columns
        cursor.execute(query)  # Execute the query
        
        rows = cursor.fetchall()  # Fetch all rows
        
        # Step 3: Check if data is retrieved
        if rows is not None:
            # Step 4: Get column names
            
            # Here, cursor.description contains metadata about the columns, and the loop extracts each column's name.
            columns = [] 
            for col in cursor.description:
                columns.append(col[0])

            
            # Step 5: Convert rows into a list of dictionaries
            # result = [dict(zip(columns, row)) for row in rows]
            result = []
            for row in rows:
                result.append(dict(zip(columns, row)))
            
            # Close the connection before returning data
            cursor.close()
            conn.close()
            
            print(f"Successfully fetched {len(rows)} rows from table: {table_name}")
            return result  # Return the fetched data

        else:
            print(f"No data found in table: {table_name}")
            cursor.close()
            conn.close()
            return []  # Return an empty list if no data is found

    except Exception as e:
        print(f"Error executing query: {e}")
        return None  # Return None if an error occurs

# Run this script directly to test fetching data
if __name__ == "__main__":
    data = fetch_data_from_db()
    
    # Step 6: Handle the returned data properly
    if data is None:
        print("Query execution failed.")
    else:
        for row in data:
            print(row)  # Print each row as a dictionary
