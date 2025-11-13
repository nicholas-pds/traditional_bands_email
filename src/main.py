# src/main.py
from pathlib import Path
from .db_handler import execute_sql_to_dataframe
from .py_handler import location_sum_row
from .email_handler import email_dataframes

def main():
    """Main function to orchestrate the daily process."""
    
    # --- Dynamically determine the SQL file path ---
    BASE_DIR = Path(__file__).parent
    SQL_FILE_PATH = BASE_DIR.parent / "sql_query" / "traditional_bands_shipDate_group.sql"
    
    # --- Configuration ---
    SHEET_NAME = "Import"  # The tab name in your Google Sheet
    # ----- EMAIL RECIPIENTS -----
    RECIPIENTS = ["nick@partnersdentalstudio.com"]
    #RECIPIENTS = ["nick@partnersdentalstudio.com", "sarah@partnersdentalstudio.com"]
    #RECIPIENTS = ["nick@partnersdentalstudio.com", "emily@partnersdentalstudio.com"]
    #RECIPIENTS = ["nick@partnersdentalstudio.com","iryna@partnersdentalstudio.com","3ddesign@partnersdentalstudio.com"] # Add more recipients as needed
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
    
    # # Step 2: Process with py_handler
    # print("\n--- Processing with py_handler ---")
    # try:
    #     summary_df = location_sum_row(data_df)
    #     print("\n--- Summary DataFrame ---")
    #     print(summary_df)
    # except Exception as e:
    #     print(f"ERROR in location_sum_row: {e}")
    #     return
    # step 3: 
    summary_df = data_df.copy()

    # ----- EMAIL: Only send summary_df -----
    print("\nSending email with summary only...")
    try:
        email_dataframes(
            summary_df=summary_df,
            recipients=RECIPIENTS,
            subject="Daily Traditional Bands Summary",
            from_name="Partners Dental Report Bot",
        )
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    main()