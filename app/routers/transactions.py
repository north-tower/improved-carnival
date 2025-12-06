from fastapi import FastAPI, APIRouter, HTTPException
from typing import Annotated
import pandas as pd
import re
from . import file_upload
from .state import shared_state
from .helpers import transactions_helper
from .helpers.data_loader import get_transactions_df

router = APIRouter(
    #router tags
    prefix="/transaction_module",
    #documentation tags
    tags=['Transaction Module']
)

def extract_names(details):
    """Extract names from Details column"""
    if pd.isna(details):
        return None
    match = re.search(r"\d[\d\*\#\&\-]*\s([a-zA-Z\s\-]+)", str(details))
    if match:
        name = match.group(1).strip()
        if len(name) > 3:
            return name
    return str(details) if details else None

def extract_numbers_from_details(data, details_col='Details'):
    """Extract numbers from Details column"""
    # Return early if DataFrame is empty or None
    if data is None or data.empty or len(data) == 0:
        return data
    
    # Check if the required column exists
    if details_col not in data.columns:
        return data
    
    pattern_to = r"to\s+(\d+)\s*-\s*"
    pattern_masked = r"[0-9]\*{6}\d{3}|[0-9]"
    
    def extract_number(row):
        text = str(row).strip()
        match = re.search(pattern_to, text)
        if match:
            return match.group(1)
        masked_match = re.findall(pattern_masked, text)
        return "".join(masked_match) if masked_match else None
    
    if len(data) > 0:
        data["numbers"] = data[details_col].apply(extract_number)
    return data

def ensure_names_and_numbers_columns(data):
    """Ensure names and numbers columns exist in the DataFrame"""
    # Return early if DataFrame is empty or None
    if data is None or data.empty or len(data) == 0:
        return data
    
    if 'names' not in data.columns and 'Details' in data.columns and len(data) > 0:
        data["names"] = data.apply(
            lambda row: extract_names(row["Details"]),
            axis=1
        )
    if 'numbers' not in data.columns and 'Details' in data.columns and len(data) > 0:
        data = extract_numbers_from_details(data, 'Details')
    return data

def ensure_time_columns(data):
    """Ensure time_day and day_name columns exist in the DataFrame"""
    # Return early if DataFrame is empty or None
    if data is None or data.empty or len(data) == 0:
        return data
    
    if 'Completion Time' in data.columns:
        # Ensure day_name exists
        if 'day_name' not in data.columns:
            data['day_name'] = data['Completion Time'].dt.day_name()
        
        # Ensure Hour exists
        if 'Hour' not in data.columns:
            data['Hour'] = data['Completion Time'].dt.hour
        
        # Create time_day from Hour (format as time period)
        if 'time_day' not in data.columns:
            def get_time_period(hour):
                """Convert hour to time period string"""
                if pd.isna(hour):
                    return None
                try:
                    hour = int(hour)
                except (ValueError, TypeError):
                    return None
                if 0 <= hour < 6:
                    return "Night (00-06)"
                elif 6 <= hour < 12:
                    return "Morning (06-12)"
                elif 12 <= hour < 17:
                    return "Afternoon (12-17)"
                elif 17 <= hour < 22:
                    return "Evening (17-22)"
                else:
                    return "Night (22-00)"
            
            # Only create column if we have data and Hour column exists
            if 'Hour' in data.columns and len(data) > 0:
                data['time_day'] = data['Hour'].apply(get_time_period)
    
    return data

@router.get("/")
def read_root():
    return {"Testing Setup": "Transaction Module Logic"}

# number of transactions per type per amount
@router.get("/trans_type/")
def trans_type():
    data = get_transactions_df()
    data = transactions_helper.add_total_amount_column(data)

    if data is None or data.empty:
        return {"message" : "No transaction data available"}

    # Group data by 'Transaction_Type', aggregate count and sum of 'Amount'
    types = data.groupby("Transaction_Type").agg(
        Count=("Transaction_Type", "count"),  # Count occurrences of each transaction type
        Total_Amount=("amount", "sum")      # Sum amounts for each transaction type
    )
    return types.to_dict(orient='records')

# total amount transacted

# total amount transacted - received
@router.get("/total_recieved/")
def total_received():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    total = data['Paid In'].sum()

    return {"total": total}


# total amount transacted - withdrawn
@router.get('/total_withdrawn/')
def total_withrdrawn():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    total = data['Withdrawn'].sum()
    return {"total":total}

# total withdrawn plus total received
@router.get('/total_transacted/')
def total_transacted():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    received = data['Paid In'].sum()
    withdrawn = data['Withdrawn'].sum()
    total = received + withdrawn
    return {"total":total}


# total number of transactions

# total withdrawals count
@router.get('/withdrawal_count/')
def number_of_withdrawals():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    withdrawal_df = data[data['Withdrawn'] != 0.00]
    num_of_withdrawals = len(withdrawal_df)
    return {"no_of_withdrawals":num_of_withdrawals}


# total deposits count
@router.get('/deposit_count/')
def number_of_deposits():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    deposits_df = data[data['Paid In'] != 0.00]
    num_of_deposits = len(deposits_df)
    return {"number_of_deposits":num_of_deposits}


# withdrawal count plus deposit count
@router.get('/total_transaction_count/')
def total_number_of_transactions():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    withdrawal_df = data[data['Withdrawn'] != 0.00]
    deposits_df = data[data['Paid In'] != 0.00]
    total = len(withdrawal_df) + len(deposits_df)
    return {"total_no_of_transactions":total}


# top deposit
@router.get('/top_deposit/')
def highest_received():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    highest_received_amount = data['Paid In'].max()
    return {"highest_receoved_amount":highest_received_amount}


# lowest deposit
@router.get('/lowest_deposit/')
def lowest_received():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # to prevent getting zero as the result
    received_df = data[data['Paid In'] != 0.00]
    lowest_received_amount = received_df['Paid In'].min()
    return {"lowest_amount_received":lowest_received_amount}


# top withdrawal
@router.get('/top_withdrawal/')
def highest_withdrawn():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    highest_withdrawn_amount = data['Withdrawn'].max()
    return {"highest_withdrawn_amount":highest_withdrawn_amount}


# lowest withdrawal
@router.get('/lowest_withdrawal/')
def lowest_withdrawn():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # to prevent getting zero as the result
    withdrawal_df = data[data['Withdrawn'] != 0.00]
    lowest_withdrawn_amount = withdrawal_df['Withdrawn'].min()
    return {"lowest_withdrawn_amount":lowest_withdrawn_amount}


# minimum amount transacted
@router.get('/minimum_amount_transacted/')
def min_amount_transacted():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    received_df = data[data['Paid In'] != 0.00]
    withdrawal_df = data[data['Withdrawn'] != 0.00]
    lowest_deposit_amount = received_df['Paid In'].min() if not received_df.empty else 0
    lowest_withdrawn_amount = withdrawal_df['Withdrawn'].min() if not withdrawal_df.empty else 0

    if lowest_withdrawn_amount > 0 and (lowest_deposit_amount == 0 or lowest_withdrawn_amount < lowest_deposit_amount):
        return {"lowest_amount_transacted": lowest_withdrawn_amount}
    else:
        return {"lowest_amount_transacted": lowest_deposit_amount}
    

# maximum amount transacted
@router.get('/maximum_amount_transacted/')
def max_amount_transacted():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    highest_deposit_amount = data['Paid In'].max()
    highest_withdrawn_amount = data['Withdrawn'].max()

    if highest_withdrawn_amount > highest_deposit_amount:
        return {"highest_amount_transacted": highest_withdrawn_amount}
    else:
        return {"highest_amount_transacted": highest_deposit_amount}


# top paybill transactions
@router.get('/top_paybill_transactions/')
def top_transactions():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    # Filter rows where Transaction_Type is "Pay Bill"
    data = data[data['Transaction_Type'] == "Pay Bill"]
    
    if data.empty:
        return {"data_final": []}
    
    # Group by 'names' and 'numbers' and aggregate
    data_grouped = data.groupby(['names', 'numbers']).agg(
        receipt_count=('Receipt No.', 'count'),
        max_amount=('amount', 'max')
    ).reset_index()
    
    # Get the top 10 rows based on receipt_count
    data_final = data_grouped.nlargest(10, 'receipt_count')
    
    return {"data_final": data_final.to_dict(orient='records')}


# top till transactions
@router.get('/top_till_transactions/')
def top_transactions_till ():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    data = data[data['Transaction_Type'] == "Till No"]
    
    if data.empty:
        return {"data": []}
    
    data = data.groupby(["names","numbers"])
    data =data.agg({'Receipt No.': 'count', 'amount': 'sum'})
    data = data.nlargest(10, 'Receipt No.').reset_index()

    return {"data": data.to_dict(orient='records')}


# top send money transactions
@router.get('/top_send_money_transactions/')
def top_transactions_send_money ():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    data = data[data['Transaction_Type'] == "Send Money"]
    
    if data.empty:
        return {"data": []}
    
    data = data.groupby(["names","numbers"])
    data =data.agg({'Receipt No.': 'count', 'amount': 'sum'})
    data = data.nlargest(10, 'Receipt No.').reset_index()

    return {"data": data.to_dict(orient='records')}


# top transaction customer
@router.get('/top_transactions_customer/')
def top_transactions_customer ():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    data = data[data['Transaction_Type'] == "Customer Deposit"]
    
    if data.empty:
        return {"data": []}
    
    data = data.groupby(["names","numbers"])
    data =data.agg({'Receipt No.': 'count', 'amount': 'sum'})
    data = data.reset_index()
    data = data.nlargest(10, 'Receipt No.')

    return {"data": data.to_dict(orient='records')}


## top 10 withdrawals
@router.get('/top_withdrawals/')
def top_transactions_withrawals ():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    data = data[data['Transaction_Type'] == "Cash Withdrawal"]
    
    if data.empty:
        return {"data_final": []}
    
    data_group= data.groupby(["names","numbers"])
    data_agg=data_group.agg({'Receipt No.': 'count', 'amount': 'sum'})
    data_res= data_agg.reset_index()
    data_final = data_res.nlargest(10, 'Receipt No.')

    return {"data_final": data_final.to_dict(orient='records')}


@router.get('/top_transactions_received/')
def top_transactions_recieved():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure amount column exists
    data = transactions_helper.add_total_amount_column(data)
    
    # Ensure names and numbers columns exist
    data = ensure_names_and_numbers_columns(data)
    
    data = data[data['Transaction_Type'] == "Received Money"]
    
    if data.empty:
        return {"data_final": []}
    
    data_group= data.groupby(["names","numbers"])
    data_agg=data_group.agg({'Receipt No.': 'count', 'amount': 'sum'})
    data_res= data_agg.reset_index()
    data_final = data_res.nlargest(10, 'Receipt No.')

    return {"data_final": data_final.to_dict(orient='records')}

	
## Getting the  number of transactions transacted per day (time of day)
@router.get('/top_transaction_hour/')
def top_transactions_hour():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure time columns exist
    data = ensure_time_columns(data)
    
    # Ensure amount column exists
    if 'amount' not in data.columns:
        data = transactions_helper.add_total_amount_column(data)
    
    if 'time_day' not in data.columns:
        return {"message": "Unable to create time_day column. Completion Time column may be missing."}
    
    data_group= data.groupby(["time_day"])
    data_agg=data_group.agg({'Receipt No.': 'count', 'amount': 'mean'})
    data_res= data_agg.reset_index()
    data_final = data_res.nlargest(10, 'Receipt No.')

    return {"data_final": data_final.to_dict(orient='records')}


# getting the transactions distributed per week
@router.get('/top_transaction_day/')
def top_transactions_day():
    data = get_transactions_df()

    if data is None or data.empty:
        return {"message" : "No transaction data available"}
    
    # Create a deep copy and reset index to ensure clean DataFrame structure
    data = data.copy(deep=True).reset_index(drop=True)
    
    # Ensure time columns exist
    data = ensure_time_columns(data)
    
    # Ensure amount column exists
    if 'amount' not in data.columns:
        data = transactions_helper.add_total_amount_column(data)
    
    if 'day_name' not in data.columns:
        return {"message": "Unable to create day_name column. Completion Time column may be missing."}
    
    data_group= data.groupby(["day_name"])
    data_agg=data_group.agg({'Receipt No.': 'count', 'amount': 'mean'})
    data_res= data_agg.reset_index()
    data_final = data_res.nlargest(10, 'Receipt No.')

    return {"data_final": data_final.to_dict(orient='records')}
