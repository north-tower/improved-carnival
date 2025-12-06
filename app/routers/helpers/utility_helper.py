import re
import pandas as pd
import numpy as np

def get_names(details:str | None):
    "A function to extract individual names from the details column"

    if not details:
        return None
    # Regex to capture names after a number and/or special characters, followed by a space
    match = re.search(r"\d[\d\*\#\&\-]*\s([a-zA-Z\s\-]+)", details)
    if match:
        name = match.group(1).strip()
        # Condition: Add only if the name has more than 3 characters
        if len(name) > 3:
            return name
    return None  # Return None if no valid name is found


def get_paybill_and_till_numbers(data: pd.DataFrame, details_col: str):
    
    if data is None or data.empty:
        return 
    
    # Define regex pattern to extract the number that appears after 'to' and before '-'
    pattern = r'to (\d+) -'

    # Apply regex to extract numbers from the specified column
    data["numbers"] = data[details_col].apply(
        lambda x: re.search(pattern, str(x).strip()).group(1) if re.search(pattern, str(x).strip()) else None
    )

    return data

def add_total_amount_column(data: pd.DataFrame) -> pd.DataFrame:
    """Add total amount column"""
    if 'Withdrawn' not in data.columns or 'Paid In' not in data.columns:
        raise ValueError("Required columns 'Withdrawn' and 'Paid In' not found")
    
    # Handle missing values
    data['Withdrawn'] = data['Withdrawn'].fillna(0)
    data['Paid In'] = data['Paid In'].fillna(0)
    
    # Add total amount column
    data['amount'] = data['Withdrawn'] + data['Paid In']
    
    # Replace NaN and infinite values with None
    data.replace([np.inf, -np.inf, np.nan], None, inplace=True)
    
    return data