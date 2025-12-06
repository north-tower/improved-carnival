from fastapi import FastAPI, APIRouter, HTTPException
from typing import Annotated
import pandas as pd
from .helpers import utility_helper
from .state import shared_state
from .helpers.data_loader import get_transactions_df
import re
import logging

router = APIRouter(
    #router tags
    prefix="/utility_module",
    #documentation tags
    tags=['Utility Module']
)

@router.get('/data_bills/')
def data_bills():
    try:
        data = get_transactions_df()

        # Check if Transaction_Type column exists
        if 'Transaction_Type' not in data.columns:
            # Try to get it from helpers if needed
            from .helpers import transactions_helper
            data = transactions_helper.ensure_transaction_type_column(data)
        
        if 'Transaction_Type' not in data.columns:
            return {"message": "No transaction type data available"}

        # get paybills and tills from statement
        data_utility = data[data["Transaction_Type"].isin(["Pay Bill", "Till No"])]

        if data_utility.empty:
            return {"message": "No data bills data"}

        data_utility = utility_helper.add_total_amount_column(data_utility)

        # Apply the function conditionally
        if 'Details' in data_utility.columns:
            data_utility["names"] = data_utility.apply(
                lambda row: utility_helper.get_names(row["Details"]),
                axis=1
            )

        if data_utility is None or data_utility.empty:
            return {"message": "No data bills data"}
    
        return data_utility.to_dict(orient='records')
    except Exception as e:
        logging.error(f"Error in data_bills: {e}")
        return {"message": "Error processing data bills", "error": str(e)}


@router.get('/kplc/')
# getting the kplc transactions 
def kplc ():
    try:
        bills_data = data_bills()
        
        # Check if data_bills returned an error
        if isinstance(bills_data, dict) and ("message" in bills_data or "error" in bills_data):
            return bills_data
        
        data_bills_df = pd.DataFrame(bills_data)
        
        if data_bills_df.empty or 'Details' not in data_bills_df.columns:
            return {"message": "No client KPLC data"}
        
        till_numbers_and_paybill = utility_helper.get_paybill_and_till_numbers(data_bills_df, 'Details')
        
        if till_numbers_and_paybill.empty or 'numbers' not in till_numbers_and_paybill.columns:
            return {"message": "No client KPLC data"}
        
        data_kplc = till_numbers_and_paybill[till_numbers_and_paybill["numbers"].isin(["888888", "888880"])]

        if data_kplc is None or data_kplc.empty:
            return {"message": "No client KPLC data"}
  
        return data_kplc.to_dict(orient='records')
    except Exception as e:
        import logging
        logging.error(f"Error in kplc: {e}")
        return {"message": "Error processing KPLC data", "error": str(e)}


@router.get('/kplc_metrics/')
def kplc_metrics():
    try:
        # calculating the metrics 
        data_kplc = kplc()

        # check for error message
        if isinstance(data_kplc, dict) and ("message" in data_kplc or "error" in data_kplc):
            return data_kplc
    
        data_kplc = pd.DataFrame(data_kplc)
        
        if data_kplc.empty:
            return {"message": "No client KPLC data"}
        
        # Ensure required columns exist
        if 'month_name' not in data_kplc.columns:
            return {"message": "No client KPLC data - missing month data"}
        
        if 'amount' not in data_kplc.columns:
            return {"message": "No client KPLC data - missing amount data"}
        
        transactions_per_month = data_kplc.groupby('month_name').size()
        
        # Calculate the average number of transactions per month
        avg_no_transactions_per_month = float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0
        transactions_count = int(data_kplc.shape[0])
        transactions_amount = float(data_kplc["amount"].sum())
        max_transacted = float(data_kplc["amount"].max())
        min_transacted = float(data_kplc["amount"].min())
        avg_transacted = float(data_kplc["amount"].mean())

        return {
            "total_transactions": transactions_count,
            "average_transactions_per_month": avg_no_transactions_per_month,
            "total_tranasacted_amount": transactions_amount,
            "highest_transacted_amount": max_transacted,
            "minimum_transacted_amount": min_transacted,
            "average_transacted_amount": avg_transacted
        }
    except Exception as e:
        import logging
        logging.error(f"Error in kplc_metrics: {e}")
        return {"message": "Error processing KPLC metrics", "error": str(e)}


@router.get('/safaricom_wifi/')
# getting the safaricom wifi transactions 
def safaricom_wifi():
    try:
        bills_data = data_bills()
        
        # Check if data_bills returned an error
        if isinstance(bills_data, dict) and ("message" in bills_data or "error" in bills_data):
            return bills_data
        
        data_bills_df = pd.DataFrame(bills_data)
        
        if data_bills_df.empty or 'Details' not in data_bills_df.columns:
            return {"message": "No client Safaricom wifi data"}
        
        till_numbers_and_paybill = utility_helper.get_paybill_and_till_numbers(data_bills_df, 'Details')
        
        if till_numbers_and_paybill.empty or 'numbers' not in till_numbers_and_paybill.columns:
            return {"message": "No client Safaricom wifi data"}
        
        data_safaricom_wifi = till_numbers_and_paybill[till_numbers_and_paybill["numbers"].isin(["150501"])]

        if data_safaricom_wifi is None or data_safaricom_wifi.empty:
            return {"message": "No client Safaricom wifi data"}
    
        return data_safaricom_wifi.to_dict(orient='records')
    except Exception as e:
        import logging
        logging.error(f"Error in safaricom_wifi: {e}")
        return {"message": "Error processing Safaricom WiFi data", "error": str(e)}


@router.get('/safaricom_wifi_metrics/')
def safaricom_wifi_metrics():
    try:
        # calculating the metrics 
        data_safaricom_wifi = safaricom_wifi()

        # check for error message
        if isinstance(data_safaricom_wifi, dict) and ("message" in data_safaricom_wifi or "error" in data_safaricom_wifi):
            return data_safaricom_wifi   

        data_safaricom_wifi = pd.DataFrame(data_safaricom_wifi)
        
        if data_safaricom_wifi.empty:
            return {"message": "No client Safaricom wifi data"}
        
        # Ensure required columns exist
        if 'month_name' not in data_safaricom_wifi.columns:
            return {"message": "No client Safaricom wifi data - missing month data"}
        
        if 'amount' not in data_safaricom_wifi.columns:
            return {"message": "No client Safaricom wifi data - missing amount data"}
        
        transactions_per_month = data_safaricom_wifi.groupby('month_name').size()
        
        # Calculate the average number of transactions per month
        avg_no_transactions_per_month = float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0
        transactions_count = int(data_safaricom_wifi.shape[0])
        transactions_amount = float(data_safaricom_wifi["amount"].sum())
        max_transacted = float(data_safaricom_wifi["amount"].max())
        min_transacted = float(data_safaricom_wifi["amount"].min())
        avg_transacted = float(data_safaricom_wifi["amount"].mean())

        return {
            "total_transactions": transactions_count,
            "average_transactions_per_month": avg_no_transactions_per_month,
            "total_tranasacted_amount": transactions_amount,
            "highest_transacted_amount": max_transacted,
            "minimum_transacted_amount": min_transacted,
            "average_transacted_amount": avg_transacted
        }
    except Exception as e:
        import logging
        logging.error(f"Error in safaricom_wifi_metrics: {e}")
        return {"message": "Error processing Safaricom WiFi metrics", "error": str(e)}


@router.get('/zuku_wifi/')
def zuku ():
    try:
        bills_data = data_bills()
        
        # Check if data_bills returned an error
        if isinstance(bills_data, dict) and ("message" in bills_data or "error" in bills_data):
            return bills_data
        
        data_bills_df = pd.DataFrame(bills_data)
        
        if data_bills_df.empty or 'Details' not in data_bills_df.columns:
            return {"message": "No client Zuku data"}
        
        till_numbers_and_paybill = utility_helper.get_paybill_and_till_numbers(data_bills_df, 'Details')
        
        if till_numbers_and_paybill.empty or 'numbers' not in till_numbers_and_paybill.columns:
            return {"message": "No client Zuku data"}
        
        data_zuku = till_numbers_and_paybill[till_numbers_and_paybill["numbers"].isin(["320320"])]

        if data_zuku is None or data_zuku.empty:
            return {"message": "No client Zuku data"}
    
        return data_zuku.to_dict(orient="records")
    except Exception as e:
        import logging
        logging.error(f"Error in zuku: {e}")
        return {"message": "Error processing Zuku data", "error": str(e)}


@router.get('/zuku_wifi_metrics/')
def zuku_wifi_metrics():
    try:
        # calculating the metrics 
        data_zuku_wifi = zuku()

        # check for error message
        if isinstance(data_zuku_wifi, dict) and ("message" in data_zuku_wifi or "error" in data_zuku_wifi):
            return data_zuku_wifi   

        data_zuku_wifi = pd.DataFrame(data_zuku_wifi)
        
        if data_zuku_wifi.empty:
            return {"message": "No client Zuku data"}
        
        # Ensure required columns exist
        if 'month_name' not in data_zuku_wifi.columns:
            return {"message": "No client Zuku data - missing month data"}
        
        if 'amount' not in data_zuku_wifi.columns:
            return {"message": "No client Zuku data - missing amount data"}
        
        transactions_per_month = data_zuku_wifi.groupby('month_name').size()
        
        # Calculate the average number of transactions per month
        avg_no_transactions_per_month = float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0
        transactions_count = int(data_zuku_wifi.shape[0])
        transactions_amount = float(data_zuku_wifi["amount"].sum())
        max_transacted = float(data_zuku_wifi["amount"].max())
        min_transacted = float(data_zuku_wifi["amount"].min())
        avg_transacted = float(data_zuku_wifi["amount"].mean())

        return {
            "total_transactions": transactions_count,
            "average_transactions_per_month": avg_no_transactions_per_month,
            "total_tranasacted_amount": transactions_amount,
            "highest_transacted_amount": max_transacted,
            "minimum_transacted_amount": min_transacted,
            "average_transacted_amount": avg_transacted
        }
    except Exception as e:
        import logging
        logging.error(f"Error in zuku_wifi_metrics: {e}")
        return {"message": "Error processing Zuku WiFi metrics", "error": str(e)}

@router.get('/fuel/')
def fuel():
    try:
        # Use regular expression to filter rows that contain any of the specified names
        data_fuel = data_bills()

        if isinstance(data_fuel, dict) and ("message" in data_fuel or "error" in data_fuel):
            return data_fuel
        
        data_fuel = pd.DataFrame(data_fuel)
        
        if data_fuel.empty:
            return {"message": "No fuel data available"}
        
        # Check if names column exists
        if 'names' not in data_fuel.columns:
            return {"message": "No fuel data available - missing names column"}
        
        # Filter fuel transactions
        fuel_mask = data_fuel["names"].str.contains(
                "Rubis|Shell|Total|Astrol", 
                case=False, 
                na=False
        )
        data_fuel = data_fuel[fuel_mask]

        if data_fuel is None or data_fuel.empty:
            return {"message": "No fuel data available"}

        return data_fuel.to_dict(orient="records")
    except Exception as e:
        import logging
        logging.error(f"Error in fuel: {e}")
        return {"message": "Error processing fuel data", "error": str(e)}


@router.get('/fuel_metrics/')
def fuel_metrics():
    try:
        # calculating the metrics 
        data_fuel = fuel()

        # check for error message
        if isinstance(data_fuel, dict) and ("message" in data_fuel or "error" in data_fuel):
            return data_fuel
      
        data_fuel = pd.DataFrame(data_fuel)
        
        if data_fuel.empty:
            return {"message": "No fuel data available"}
        
        # Ensure required columns exist
        if 'month_name' not in data_fuel.columns:
            return {"message": "No fuel data available - missing month data"}
        
        if 'amount' not in data_fuel.columns:
            return {"message": "No fuel data available - missing amount data"}
        
        transactions_per_month = data_fuel.groupby('month_name').size()
        
        # Calculate the average number of transactions per month
        avg_no_transactions_per_month = float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0
        transactions_count = int(data_fuel.shape[0])
        transactions_amount = float(data_fuel["amount"].sum())
        max_transacted = float(data_fuel["amount"].max())
        min_transacted = float(data_fuel["amount"].min())
        avg_transacted = float(data_fuel["amount"].mean())

        return {
            "total_transactions": transactions_count,
            "average_transactions_per_month": avg_no_transactions_per_month,
            "total_tranasacted_amount": transactions_amount,
            "highest_transacted_amount": max_transacted,
            "minimum_transacted_amount": min_transacted,
            "average_transacted_amount": avg_transacted
        }
    except Exception as e:
        import logging
        logging.error(f"Error in fuel_metrics: {e}")
        return {"message": "Error processing fuel metrics", "error": str(e)}