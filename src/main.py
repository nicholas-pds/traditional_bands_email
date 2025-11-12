# src/main.py
from pathlib import Path
from .db_handler import execute_sql_to_dataframe
from .py_handler import location_sum_row  # Matches function name

def main():
    """Main function to orchestrate the daily process."""
    
    # --- Dynamically determine the SQL file path ---
    BASE_DIR = Path(__file__).parent
    SQL_FILE_PATH = BASE_DIR.parent / "sql_query" / "traditional_bands_shipDate_group.sql"
    
    # --- Configuration ---
    SHEET_NAME = "Import"  # The tab name in your Google Sheet
    # ---------------------------------------------------
    
    print(f"Attempting to load SQL file from: {SQL_FILE_PATH}")

    # Step 1: Connect to DB, run query, and get DataFrame
    print("Starting database operation...")
    
    try:
        data_df = execute_sql_to_dataframe(str(SQL_FILE_PATH))
    except FileNotFoundError:
        print(f"ERROR: SQL file not found at the expected path: {SQL_FILE_PATH}")
        return
    except Exception as e:
        print(f"ERROR during database operation: {e}")
        return

    if data_df.empty:
        print("No data returned from query.")
        return

    print("\n--- DataFrame Head ---")
    print(data_df.head())
    print(f"\nTotal rows retrieved: {len(data_df)}")
    
    # Step 2: Process with py_handler
    print("\n--- Processing with py_handler ---")
    try:
        locations_count_df = location_sum_row(data_df)
        print("\n--- Locations Count DataFrame ---")
        print(locations_count_df)
    except Exception as e:
        print(f"ERROR in location_sum_row: {e}")
        return

    # Next: Email dataframes
    print("\nstop here")

if __name__ == "__main__":
    main()