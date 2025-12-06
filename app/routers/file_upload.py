from fastapi import FastAPI, APIRouter, File, UploadFile, HTTPException, Form
from typing import Annotated
import PyPDF2 as py
import io
import tabula
import pandas as pd
from .state import shared_state
from .helpers import get_name_helper
import os

# Create output directory if it doesn't exist
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# Save with timestamp to avoid overwriting
from datetime import datetime
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
output_file_path = os.path.join(output_dir, f"mpesa_transactions_{timestamp}.csv")


router = APIRouter(
    #router tags
    prefix="/file",
    #documentation tags
    tags=['File Upload']
)

# convert to a df
def dict_to_dataframe(data: dict) -> pd.DataFrame:
    if data is None:
        return {"message": "No data available"}
    try:
        dataframe = pd.DataFrame(data["dataframe"])
        return dataframe
    except KeyError:
        raise ValueError("The provided dictionary does not contain the key 'dataframe'")

mpesa_statement_dictionary = None
mpesa_statement_dataframe = dict_to_dataframe(mpesa_statement_dictionary)

@router.get("/")
def read_root():
    return {"Testing Setup": "File Upload Logic"}


@router.post("/uploadfileandclean/")
async def upload_file(file: UploadFile, password:Annotated[str, Form()]):

    # check if file is pdf
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=404, detail="Invalid file type, only PDFs are accepted")
    
    # read pdf file
    pdf_content = await file.read()
    pdf_file = io.BytesIO(pdf_content)

    # open the pdf file from the BytesIO object (not file.file which is exhausted)
    pdf_reader = py.PdfReader(pdf_file)

    # check if the pdf is encrypted
    if pdf_reader.is_encrypted:
        # decrypt with password
        if pdf_reader.decrypt(password):
            print("pdf successfully decrypted")
        else:
            raise HTTPException(status_code=401, detail="Failed to decrypt PDF. Please confirm password and try again")
    else:
        print("pdf has no password")

     # Create a new BytesIO object for the decrypted content
    decrypted_pdf = io.BytesIO()
    pdf_writer = py.PdfWriter()

    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    pdf_writer.write(decrypted_pdf)
    decrypted_pdf.seek(0)

    client_details = get_name_helper.extract_client_name(decrypted_pdf)

    # Extract tables from the decrypted PDF using tabula
    try:
        dfs = tabula.read_pdf(decrypted_pdf, pages='all')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read PDF: {str(e)}")

    # Check if any tables were extracted
    if not dfs or len(dfs) == 0:
        raise HTTPException(status_code=400, detail="No tables found in PDF. Please ensure the PDF contains transaction data.")

    # Concatenate all the tables in the list into one dataframe
    mpesa_df = pd.concat(dfs, axis=0, ignore_index=True)
    
    # Check if DataFrame is empty
    if mpesa_df.empty:
        raise HTTPException(status_code=400, detail="No transaction data found in PDF.")
    
    # Check if required columns exist
    if 'Transaction Status' not in mpesa_df.columns:
        raise HTTPException(status_code=400, detail="PDF format not recognized. Missing 'Transaction Status' column.")
    
    # Filtering for only the completed transactions
    mpesa_df = mpesa_df[mpesa_df['Transaction Status'] == 'Completed']
    
    # Check if any completed transactions remain
    if mpesa_df.empty:
        raise HTTPException(status_code=400, detail="No completed transactions found in PDF.")

    # Check for required columns before processing
    required_columns = ['Paid In', 'Withdrawn', 'Balance', 'Details', 'Completion Time']
    missing_columns = [col for col in required_columns if col not in mpesa_df.columns]
    if missing_columns:
        raise HTTPException(status_code=400, detail=f"PDF format not recognized. Missing required columns: {', '.join(missing_columns)}")

    # Assign the objects to string values 
    try:
        mpesa_df["Paid In"] = mpesa_df['Paid In'].astype(str)
        mpesa_df["Withdrawn"] = mpesa_df['Withdrawn'].astype(str)
        mpesa_df["Balance"] = mpesa_df['Balance'].astype(str)
        mpesa_df["Details"] = mpesa_df["Details"].astype(str)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting columns to string: {str(e)}")

    # Remove commas from the 'Paid In', 'Withdrawn', and 'Balance' columns before conversion
    try:
        mpesa_df["Paid In"] = pd.to_numeric(mpesa_df['Paid In'].str.replace(',', '', regex=False), errors='coerce').fillna(0)
        mpesa_df["Withdrawn"] = pd.to_numeric(mpesa_df['Withdrawn'].str.replace(',', '', regex=False), errors='coerce').fillna(0)
        mpesa_df["Balance"] = pd.to_numeric(mpesa_df['Balance'].str.replace(',', '', regex=False), errors='coerce').fillna(0)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting amount columns to numeric: {str(e)}")
    
    # Remove '\r' from the 'Details' column
    try:
        mpesa_df['Details'] = mpesa_df['Details'].str.replace('\r',' ',regex=False)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning Details column: {str(e)}")

    # converting the completion to datetime mpesa_df type 
    try:
        mpesa_df['Completion Time'] = pd.to_datetime(mpesa_df['Completion Time'], errors='coerce')
        # Drop rows where Completion Time couldn't be parsed
        mpesa_df = mpesa_df.dropna(subset=['Completion Time'])
        if mpesa_df.empty:
            raise HTTPException(status_code=400, detail="No valid transaction dates found in PDF.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error converting Completion Time to datetime: {str(e)}")

    # Dropping columns that have more than 50% missing values
    if len(mpesa_df) > 0:
        for column in mpesa_df.columns.copy():  # Use .copy() to avoid modification during iteration
            missing_ratio = mpesa_df[column].isna().sum() / len(mpesa_df)
            if missing_ratio > 0.5:
                mpesa_df.drop(column, axis=1, inplace=True)
            else:
                # Filling remaining missing values with the column mean (for numeric columns only)
                if pd.api.types.is_numeric_dtype(mpesa_df[column]):
                    mean_value = mpesa_df[column].mean()
                    if pd.notna(mean_value):  # Only fill if mean is not NaN
                        mpesa_df[column].fillna(mean_value, inplace=True)
                    else:
                        mpesa_df[column].fillna(0, inplace=True)  # Fallback to 0 if all values are NaN

    # Dropping duplicates
    mpesa_df.drop_duplicates(inplace=True)
    
    # Clean column names by removing any line breaks or unusual characters
    mpesa_df.columns = mpesa_df.columns.str.replace(r'[\r\n]', '', regex=True)

    # Now, drop the column (if it exists)
    if 'Transaction Status' in mpesa_df.columns:
        mpesa_df.drop(['Transaction Status'], axis=1, inplace=True)

    # converting the withdrawn mpesa_df into  an abs value 
    if 'Withdrawn' in mpesa_df.columns:
        mpesa_df["Withdrawn"] = mpesa_df["Withdrawn"].abs()

    # getting the month from the completion time column
    if 'Completion Time' in mpesa_df.columns:
        mpesa_df['month_name'] = mpesa_df['Completion Time'].dt.month_name()
        
        # Getting the day name
        mpesa_df['day_name'] = mpesa_df['Completion Time'].dt.day_name()
        # getting the hour the transaction was created
        mpesa_df['Hour']= mpesa_df['Completion Time'].dt.hour


    # Define the mapping dictionary
    mapped_categories = {
        'Customer Transfer to': 'Send Money',
        'Pay Bill Fuliza M-Pesa to' : 'Fuliza Loan',
        'Customer Transfer Fuliza MPesa': 'Send Money',
        'Pay Bill Online': 'Pay Bill',
        'Pay Bill to': 'Pay Bill',
        'Customer Transfer of Funds Charge': 'Mpesa Charges',
        'Pay Bill Charge': 'Mpesa Charges',
        'Merchant Payment Online': 'Till No',
        'Customer Send Money to Micro': 'Pochi',
        'M-Shwari Withdraw': 'Mshwari Withdraw',
        'Business Payment from': 'Bank Transfer',
        'Airtime Purchase': 'Airtime Purchase',
        'Airtime Purchase For Other': 'Airtime Purchase',
        'Recharge for Customer': 'safaricom bundles',
        'Customer Bundle Purchase with Fuliza': 'safaricom bundles',
        'Funds received from': 'Received Money',
        'Merchant Payment': 'Till No',
        'Customer Withdrawal': 'Cash Withdrawal',
        'Withdrawal Charge': 'Mpesa Charges',
        'Pay Merchant Charge': 'Mpesa Charges',
        'M-Shwari Deposit': 'Mshwari Deposit',
        'M-Shwari Loan': 'M-Shwari Loan',
        'M-Shwari Loan Repayment':'M-Shwari Repayment',
        'Deposit of Funds at Agent': 'Customer Deposit',
        'OD Loan Repayment to': 'Fuliza Loan Repayment',
        'OverDraft of Credit Party': 'Fuliza Loan',
        'Customer Transfer Fuliza M-Pesa to':'Send Money',
        'Customer Transfer of Funds Charge':'Mpesa Charges',
        'KCB M-PESA Withdraw': 'KCB M-PESA Withdraw',
        'KCB M-PESA Deposit': 'KCB M-PESA Deposit',
        'KCB M-PESA Target Deposit': 'KCB M-PESA Deposit',	
        'Recharge for Customer With Fuliza': 'Fuliza Airtime',
        'Promotion Payment':'Received Money',
        'KCB M-PESA Target First Deposit':'KCB M-PESA Deposit',
        'Customer Payment to Small Business':'Pochi',
        'Merchant Customer Payment from': 'Till No',
        'Reversal':'Reversal',
        'Merchant Payment Fuliza M-Pesa':'Till No',
        'Other': 'Other'}
    
    # Initialize the 'Category' column with a default value of 'Other'
    mpesa_df['Category'] = 'Other'

    # Loop through each phrase in mapped_categories and assign the appropriate category
    if 'Details' in mpesa_df.columns:
        for phrase, category in mapped_categories.items():
            mpesa_df.loc[mpesa_df['Details'].str.contains(phrase, case=False, na=False), 'Category'] = phrase

        # Map 'Category' to user-friendly names in 'Transaction_Type' column
        mpesa_df['Transaction_Type'] = mpesa_df['Category'].map(mapped_categories)
    else:
        raise HTTPException(status_code=400, detail="PDF format not recognized. Missing 'Details' column.")


    mpesa_df.drop(['Category'], axis=1, inplace=True)  
    # Remove rows where 'Transaction_Type' is "Mpesa Charges" (if column exists)
    if 'Transaction_Type' in mpesa_df.columns:
        mpesa_df = mpesa_df.drop(mpesa_df[mpesa_df['Transaction_Type'] == "Mpesa Charges"].index)
    
    # Ensure DataFrame is not empty after filtering
    if mpesa_df.empty:
        raise HTTPException(status_code=400, detail="No valid transactions remaining after filtering.")

    # Reset index to ensure clean DataFrame structure
    mpesa_df = mpesa_df.reset_index(drop=True)

    # Save the DataFrame to a CSV file
    output_file_path = "mpesa_transactions.csv"
    absolute_csv_path = os.path.abspath(output_file_path)
    mpesa_df.to_csv(output_file_path, index=False)

    print(f"✅ CSV SAVED TO: {absolute_csv_path}")
    print(f"📊 Total rows saved: {len(mpesa_df)}")

    # Store the CSV file path in shared state (preferred method)
    shared_state.mpesa_csv_path = absolute_csv_path
    
    # Also store DataFrame for backward compatibility (will be deprecated)
    shared_state.mpesa_statement_df = mpesa_df.copy(deep=True)

    # Limit the number of records returned to avoid timeout/memory issues
    # Frontend can fetch detailed data via other endpoints if needed
    max_records_to_return = 1000
    dataframe_for_response = mpesa_df.head(max_records_to_return)
    
    return {
            "client_name": client_details.get('customer_name', ''),
            "mobile_number": client_details.get('mobile_number', ''),
            "filename": file.filename, 
            "contenttype": file.content_type,
            "total_records": len(mpesa_df),
            "records_returned": len(dataframe_for_response),
            "dataframe": dataframe_for_response.to_dict(orient="records")
            }