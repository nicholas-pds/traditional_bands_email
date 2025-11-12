# src/py_handler.py
import pandas as pd

def location_sum_row(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes a DataFrame, skips the first column ShipDate group by,
    sums all numeric columns, and returns a single-row summary.
    """
    if df.empty or len(df.columns) < 2:
        raise ValueError("DataFrame must have at least 2 columns.")

    df_copy = df.copy()
    columns_to_sum = df_copy.columns[1:]
    
    # Ensure only numeric columns are summed
    numeric_cols = df_copy[columns_to_sum].select_dtypes(include='number').columns
    if len(numeric_cols) == 0:
        raise ValueError("No numeric columns found to sum (excluding first column).")

    sum_values = df_copy[numeric_cols].sum()
    result_df = pd.DataFrame([sum_values], columns=numeric_cols)
    
    return result_df