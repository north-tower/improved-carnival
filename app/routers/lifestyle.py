from fastapi import FastAPI, APIRouter, HTTPException
from typing import Annotated
import pandas as pd
from . import file_upload
import re
from .state import shared_state
import numpy as np
from .helpers import lifestyle_helper
from .helpers.data_loader import get_transactions_df
import logging

router = APIRouter(
    #router tags
    prefix="/lifestyle_module",
    #documentation tags
    tags=['Lifestyle Module']
)


#A function to get the betting summary statistics
@router.get('/betting_summary_stats/')
def betting_summary_stats():
    try:
        data_df = get_transactions_df()
        
        # calculating the metrics
        gambling_data = lifestyle_helper.get_gambling_df(data_df)

        # Check if get_gambling_df returned an error dict instead of DataFrame
        if isinstance(gambling_data, dict):
            if "error" in gambling_data:
                return {"message": "No gambling data available", "error": gambling_data.get("error")}
            # If it's a dict but not an error, might be empty result
            return {"message": "No gambling data available"}
        
        # Check if it's a DataFrame
        if not isinstance(gambling_data, pd.DataFrame):
            return {"message": "No gambling data available"}
        
        data = gambling_data

        if data is None or data.empty:
            return {"message": "No gambling data available"}
        
        # Ensure required columns exist
        if 'month_name' not in data.columns:
            return {"message": "No gambling data available - missing month data"}
        
        if 'amount' not in data.columns:
            return {"message": "No gambling data available - missing amount data"}
        
        transactions_per_month = data.groupby('month_name').size()

        # Calculate the average number of transactions per month
        avg_no_transactions_per_month = float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0
        transactions_count = int(data.shape[0])
        transactions_amount = float(data["amount"].sum())
        max_transacted = float(data["amount"].max())
        min_transacted = float(data["amount"].min())
        avg_transacted = float(data["amount"].mean())

        return {
            "total_transactions": transactions_count,
            "average_transactions_per_month": avg_no_transactions_per_month,
            "total_tranasacted_amount": transactions_amount,
            "highest_transacted_amount": max_transacted,
            "minimum_transacted_amount": min_transacted,
            "average_transacted_amount": avg_transacted
        }
    
    except Exception as e:
        logging.error(f"Error in betting_summary_stats: {e}")
        return {"message": "Error processing betting data", "error": str(e)}


#A function to get the saving summary statistics
@router.get('/saving_summary_stats/')
def savings_analysis():
    try:
        # Get savings data
        data = lifestyle_helper.get_saving_df()
        
        if data is None or data.empty:
            return {"message": "No savings transactions found"}
        
        # Ensure required columns exist
        if 'month_name' not in data.columns:
            return {"message": "No savings data available - missing month data"}
        
        if 'amount' not in data.columns:
            # Try to add amount column if missing
            from .helpers import transactions_helper
            data = transactions_helper.add_total_amount_column(data)
            if 'amount' not in data.columns:
                return {"message": "No savings data available - missing amount data"}
            
        # Calculate metrics
        transactions_per_month = data.groupby('month_name').size()
        
        return {
            "total_transactions": int(data.shape[0]),
            "average_transactions_per_month": float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0,
            "total_tranasacted_amount": float(data["amount"].sum()),
            "highest_transacted_amount": float(data["amount"].max()),
            "minimum_transacted_amount": float(data["amount"].min()),
            "average_transacted_amount": float(data["amount"].mean())
        }
        
    except Exception as e:
        logging.error(f"Error analyzing savings: {e}")
        return {"message": "Error processing savings data", "error": str(e)}


#A function to get the shopping summary statistics
@router.get('/shopping_summary_stats/')
def shopping_summary_analysis():
    try:
        # Get shopping/supermarket data
        data = lifestyle_helper.get_supermarket_df()
        
        if data is None or data.empty:
            return {"message": "No shopping transactions found"}
        
        # Handle case where get_supermarket_df returns error dict
        if isinstance(data, dict) and "message" in data:
            return data
        
        # Ensure required columns exist
        if 'month_name' not in data.columns:
            return {"message": "No shopping data available - missing month data"}
        
        if 'amount' not in data.columns:
            # Try to add amount column if missing
            from .helpers import transactions_helper
            data = transactions_helper.add_total_amount_column(data)
            if 'amount' not in data.columns:
                return {"message": "No shopping data available - missing amount data"}
            
        # Calculate metrics
        transactions_per_month = data.groupby('month_name').size()
        
        return {
            "total_transactions": int(data.shape[0]),
            "average_transactions_per_month": float(transactions_per_month.mean()) if not transactions_per_month.empty else 0.0,
            "total_tranasacted_amount": float(data["amount"].sum()),
            "highest_transacted_amount": float(data["amount"].max()),
            "minimum_transacted_amount": float(data["amount"].min()),
            "average_transacted_amount": float(data["amount"].mean())
        }
        
    except Exception as e:
        logging.error(f"Error analyzing shopping: {e}")
        return {"message": "Error processing shopping data", "error": str(e)}