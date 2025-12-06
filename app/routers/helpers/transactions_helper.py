import pandas as pd
import numpy as np

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