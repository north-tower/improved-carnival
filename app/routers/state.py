from pandas import DataFrame

class SharedState:
    """Shared state for the application"""
    mpesa_statement_df: DataFrame | None = None  # Deprecated: Use CSV file instead
    mpesa_csv_path: str | None = None  # Path to the CSV file with transaction data

shared_state = SharedState()