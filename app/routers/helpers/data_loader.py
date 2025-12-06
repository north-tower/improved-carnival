"""
Data Loader Utility
Loads M-Pesa transaction data from CSV file
"""
import pandas as pd
import os
from typing import Optional
from fastapi import HTTPException

# Default CSV file path
DEFAULT_CSV_PATH = "mpesa_transactions.csv"


def load_transactions_data(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Load M-Pesa transactions from CSV file.
    
    Args:
        csv_path: Path to the CSV file. If None, uses DEFAULT_CSV_PATH.
        
    Returns:
        DataFrame with transaction data
        
    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV file is empty or invalid
    """
    # Use default path if not provided
    if csv_path is None:
        csv_path = DEFAULT_CSV_PATH
    
    # Check if file exists
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Transaction CSV file not found: {csv_path}. Please upload a file first.")
    
    # Load CSV
    try:
        df = pd.read_csv(csv_path)
    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file is empty: {csv_path}")
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {str(e)}")
    
    # Validate DataFrame
    if df.empty:
        raise ValueError("CSV file contains no transaction data")
    
    # Ensure clean structure
    df = df.reset_index(drop=True)
    
    # Convert Completion Time to datetime if it exists
    if 'Completion Time' in df.columns:
        df['Completion Time'] = pd.to_datetime(df['Completion Time'], errors='coerce')
    
    return df


def get_transactions_data(csv_path: Optional[str] = None) -> Optional[pd.DataFrame]:
    """
    Safely load transactions data, returning None if file doesn't exist.
    
    Args:
        csv_path: Path to the CSV file. If None, uses DEFAULT_CSV_PATH.
        
    Returns:
        DataFrame with transaction data, or None if file doesn't exist
    """
    try:
        return load_transactions_data(csv_path)
    except (FileNotFoundError, ValueError):
        return None


def validate_transactions_data(df: pd.DataFrame) -> bool:
    """
    Validate that DataFrame has required columns for transaction processing.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        True if valid, False otherwise
    """
    if df is None or df.empty:
        return False
    
    # Check for at least some basic columns (customize based on your needs)
    required_columns = ['Completion Time', 'Details']
    return all(col in df.columns for col in required_columns)


def get_transactions_df() -> pd.DataFrame:
    """
    Get transactions DataFrame from CSV file.
    Falls back to shared_state for backward compatibility.
    
    This is the main function that should be used by all endpoints.
    
    Returns:
        DataFrame with transaction data
        
    Raises:
        HTTPException: If no data is available
    """
    # Import shared_state here to avoid circular imports
    from ..state import shared_state
    
    # Try to load from CSV first (preferred method)
    csv_path = shared_state.mpesa_csv_path if shared_state else None
    df = get_transactions_data(csv_path)
    
    # Fallback to shared_state for backward compatibility
    if df is None or df.empty:
        if shared_state and shared_state.mpesa_statement_df is not None and not shared_state.mpesa_statement_df.empty:
            df = shared_state.mpesa_statement_df.copy(deep=True).reset_index(drop=True)
        else:
            raise HTTPException(status_code=400, detail="No transaction data available. Please upload a file first.")
    
    return df

