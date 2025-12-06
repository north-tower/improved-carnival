from fastapi import FastAPI, APIRouter, HTTPException
from typing import Annotated
import pandas as pd
from .state import shared_state
from .helpers.data_loader import get_transactions_df

router = APIRouter(
    #router tags
    prefix="/financial_institutions_module",
    #documentation tags
    tags=['Financial Institutions Module']
)

banks_in_kenya = [
    "Kenya Commercial Bank", "KCB", "KCB Bank",
    "Equity Bank Kenya", "Equity Bank", "Equity",
    "Cooperative Bank of Kenya", "Co-op Bank", "Coop Bank",
    "Absa Bank Kenya", "Absa", 
    "Standard Chartered Bank Kenya", "Standard Chartered", "StanChart",
    "NCBA Bank Kenya", "NCBA", 
    "Diamond Trust Bank Kenya", "Diamond Trust Bank", "DTB",
    "I&M Bank Kenya", "I&M Bank", "I&M",
    "Stanbic Bank Kenya", "Stanbic",
    "Family Bank Kenya", "Family Bank", 
    "National Bank of Kenya", "National Bank", "NBK",
    "Bank of Africa Kenya", "Bank of Africa", "BOA",
    "CitiBank Kenya", "CitiBank", "Citi",
    "Housing Finance Group Kenya", "HF Group", "HF",
    "Prime Bank Kenya", "Prime Bank",
    "Spire Bank Kenya", "Spire Bank",
    "Gulf African Bank", "Gulf Bank", 
    "Credit Bank Kenya", "Credit Bank",
    "First Community Bank", "FCB",
    "Victoria Commercial Bank", "Victoria Bank",
    "Consolidated Bank of Kenya", "Consolidated Bank",
    "SBM Bank Kenya", "SBM",
    "Ecobank Kenya", "Ecobank",
    "Guaranty Trust Bank Kenya", "GT Bank", "GTB",
    "Sidian Bank Kenya", "Sidian Bank",
    "Mayfair CIB Bank Kenya", "Mayfair Bank",
    "UBA Kenya Bank", "United Bank for Africa", "UBA",
    "ABC Bank Kenya", "ABC Bank",
    "Transnational Bank Kenya", "Transnational Bank"
]

banks_in_kenya_grouped = {
    "Kenya Commercial Bank": "KCB",
    "KCB": "KCB", 
    "KCB Bank": "KCB",
    "Equity Bank Kenya": "Equity", 
    "Equity Bank": "Equity", 
    "Equity": "Equity",
    "Cooperative Bank of Kenya": "Co-op Bank", 
    "Co-op Bank":  "Co-op Bank", 
    "Coop Bank":  "Co-op Bank",
    "Absa Bank Kenya":  "Absa", 
    "Absa":  "Absa", 
    "Standard Chartered Bank Kenya": "StanChart", 
    "Standard Chartered": "StanChart", 
    "StanChart": "StanChart",
    "NCBA Bank Kenya":   "NCBA", 
    "NCBA":   "NCBA", 
    "Diamond Trust Bank Kenya": "DTB", 
    "Diamond Trust Bank": "DTB", 
    "DTB": "DTB",
    "I&M Bank Kenya":  "I&M", 
    "I&M Bank":  "I&M", 
    "I&M":  "I&M",
    "Stanbic Bank Kenya": "Stanbic", 
    "Stanbic": "Stanbic",
    "Family Bank Kenya": "Family Bank", 
    "Family Bank": "Family Bank", 
    "National Bank of Kenya":  "National Bank", 
    "National Bank":  "National Bank", 
    "NBK":  "National Bank",
    "Bank of Africa Kenya": "Bank of Africa", 
    "Bank of Africa": "Bank of Africa", 
    "BOA": "Bank of Africa",
    "CitiBank Kenya": "CitiBank", 
    "CitiBank": "CitiBank", 
    "Citi": "CitiBank",
    "Housing Finance Group Kenya": "HF Group", 
    "HF Group": "HF Group", 
    "HF": "HF Group",
    "Prime Bank Kenya":  "Prime Bank", 
    "Prime Bank":  "Prime Bank",
    "Spire Bank Kenya": "Spire Bank", 
    "Spire Bank": "Spire Bank",
    "Gulf African Bank":  "Gulf Bank", 
    "Gulf Bank":  "Gulf Bank", 
    "Credit Bank Kenya":  "Credit Bank", 
    "Credit Bank":  "Credit Bank",
    "First Community Bank":   "First Community Bank", 
    "FCB":   "First Community Bank",
    "Victoria Commercial Bank": "Victoria Bank", 
    "Victoria Bank": "Victoria Bank",
    "Consolidated Bank of Kenya": "Consolidated Bank", 
    "Consolidated Bank": "Consolidated Bank",
    "SBM Bank Kenya": "SBM Bank Kenya", 
    "SBM": "SBM Bank Kenya",
    "Ecobank Kenya": "Ecobank", 
    "Ecobank": "Ecobank",
    "Guaranty Trust Bank Kenya": "GT Bank", 
    "GT Bank": "GT Bank", 
    "GTB" : "GT Bank",
    "Sidian Bank Kenya": "Sidian Bank", 
    "Sidian Bank": "Sidian Bank",
    "Mayfair CIB Bank Kenya": "Mayfair Bank", 
    "Mayfair Bank": "Mayfair Bank",
    "UBA Kenya Bank": "UBA Kenya Bank", 
    "United Bank for Africa": "UBA Kenya Bank", 
    "UBA": "UBA Kenya Bank",
    "ABC Bank Kenya": "ABC Bank", 
    "ABC Bank": "ABC Bank",
    "Transnational Bank Kenya": "Transnational Bank", 
    "Transnational Bank": "Transnational Bank"
}

safaricom_financial_services = {
    "M-Shwari":"MShwari", 
    "KCB M-Pesa":"KCB Mpesa",
    "Fuliza" :"M-Pesa Fuliza", 
    "M-Pesa Global" :"Global M-Pesa",
    "H- Fund":"HustlerFund"
}

@router.get("/")
def read_root():
    return {"Testing Setup": "Financial Institutions Logic"}


# Identify Banks Customer Transacts to/from
@router.get('/client_banks/')
def identify_banks():

    data = get_transactions_df()

    if data is None:
        return [], {"message": "No data available"}
    
    try:
        #create a new column 'Bank' initialized with None
        data['Bank'] = None

        #populate 'Bank' column
        for keyword in banks_in_kenya:
            data.loc[data['Details'].str.contains(keyword, case=False, na=False), 'Bank'] = keyword
    
        #filter rows where 'Bank' is not None
        bank_transactions = data[data['Bank'].notna()]

        unique_banks = bank_transactions['Bank'].unique().tolist()

        return unique_banks, {
            "transactions": bank_transactions.to_dict(orient='records'),
            "count": len(bank_transactions)
        }
    
    except Exception as e:
        print(f"Error identifying banks: {e}")
        return { "error":str(e) }


# lowest amount received through bank
@router.get('/lowest_amount_received_through_bank/')
def lowest_amount_received_through_bank():

    _, client_bank_transactions = identify_banks()
    client_bank_transactions = client_bank_transactions['transactions']
    data_df = pd.DataFrame(client_bank_transactions)

    if data_df is None:
        return {"error":"No data available"}
    
    try:
        # to prevent getting zero as the result
        received_df = data_df[data_df['Paid In'] != 0.00]
        lowest_received_amount = received_df['Paid In'].min()
        return {"lowest_received_amount": lowest_received_amount}
    
    except Exception as e:
        print(f"Error getting lowest amount: {e}")
        return { "error": str(e)}


def lowest_amount_received_through_bank(data):

    if data is None:
        return {"error":"No data available"}
    
    try:
        # to prevent getting zero as the result
        received_df = data[data['Paid In'] != 0.00]
        lowest_received_amount = received_df['Paid In'].min()
        return lowest_received_amount
    
    except Exception as e:
        print(f"Error getting lowest amount: {e}")
        return { "error": str(e)}


# bank summary metrics for recieved
@router.get('/bank_received_summary_metrics/')
def bank_received_summary_metrics():

    _, client_bank_transactions = identify_banks()

    #print(client_bank_transactions)
    client_bank_transactions = client_bank_transactions['transactions']
    client_bank_transactions_df = pd.DataFrame(client_bank_transactions)

    # debugging
    # print("===============================================")
    # print(f"{client_bank_transactions_df.columns.tolist()}")
    # print("===============================================")

    total_amount_received = client_bank_transactions_df['Paid In'].sum()
    highest_amount_received = client_bank_transactions_df['Paid In'].max()
    lowest_amount_received = lowest_amount_received_through_bank(client_bank_transactions_df)

    highest_amount_bank = client_bank_transactions_df.loc[client_bank_transactions_df['Paid In'].idxmax(), 'Bank']
    lowest_amount_bank = client_bank_transactions_df.loc[client_bank_transactions_df['Paid In'].idxmin(), 'Bank']

    return {
        "total_amount_received": total_amount_received,
        "highest_amount_received": highest_amount_received,
        "lowest_amount_received": lowest_amount_received,
        "highest_amount_bank": highest_amount_bank,
        "lowest_amount_bank":  lowest_amount_bank
    }


# lowest amount sent through bank
@router.get('/lowest_amount_sent_through_bank/')
def lowest_amount_sent_through_bank():

    _, client_bank_transactions = identify_banks()
    client_bank_transactions = client_bank_transactions['transactions']
    data_df = pd.DataFrame(client_bank_transactions)

    if data_df is None:
        return {"message": "No data available"}
    
    try:
        # to prevent getting zero as the result
        sent_df = data_df[data_df['Withdrawn'] != 0.00]
        lowest_sent_amount = sent_df['Withdrawn'].min()
        return lowest_sent_amount
    except Exception as e:
        print(f"Error getting lowest amount sent through bank: {e}")
        return {"error": str(e)}
    

def lowest_amount_sent_through_bank(data):

    if data is None:
        return {"error": "No data available"}
    
    try:
        # to prevent getting zero as the result
        sent_df = data[data['Withdrawn'] != 0.00]
        lowest_sent_amount = sent_df['Withdrawn'].min()
        return {"lowest_sent_amount":  lowest_sent_amount}
    except Exception as e:
        print(f"Error getting lowest amount sent through bank: {e}")
        return {"error": str(e)}


# bank summary metrics for recieved
@router.get('/bank_sent_summary_metrics/')
def bank_sent_summary_metrics():
    _, client_bank_transactions = identify_banks()

    client_bank_transactions = client_bank_transactions['transactions']
    client_bank_transactions_df = pd.DataFrame(client_bank_transactions)

    total_amount_sent = client_bank_transactions_df['Withdrawn'].sum()
    highest_amount_sent = client_bank_transactions_df['Withdrawn'].max()
    lowest_amount_sent = lowest_amount_sent_through_bank(client_bank_transactions_df)

    highest_amount_bank = client_bank_transactions_df.loc[client_bank_transactions_df['Withdrawn'].idxmax(), 'Bank']
    lowest_amount_bank = client_bank_transactions_df.loc[client_bank_transactions_df['Withdrawn'].idxmin(), 'Bank']

    return {
        "total_amount_sent": total_amount_sent,
        "highest_amount_sent": highest_amount_sent,
        "lowest_amount_sent": lowest_amount_sent,
        "highest_amount_bank": highest_amount_bank,
        "lowest_amount_bank":  lowest_amount_bank
    }

# Identify Saf Financial Services/Transactions
@router.get('/identify_safaricom_financial_services/')
def identify_safaricom_financial_services():

    data_df = get_transactions_df()

    #create a new column 'Bank' initialized with None
    data_df['Financial_Service'] = None

    #populate 'Financial_Service' column
    for keyword in safaricom_financial_services:
        data_df.loc[data_df['Details'].str.contains(keyword, case=False, na=False), 'Financial_Service'] = keyword
    
    #filter rows where 'Financial_Service' is not None
    bank_transactions = data_df[data_df['Financial_Service'].notna()]

    return {"transactions": bank_transactions.to_dict(orient='records')}


# M-Shwari
# identify mshwari financial transactions
@router.get('/identify_mshwari_financial_transactions/')
def identify_mshwari_financial_transactions():

    mshwari_financial_services = ["M-Shwari", "MShwari"]
    data_df = get_transactions_df()

    data_df['Mshwari_Service'] = None

    for keyword in mshwari_financial_services:
        data_df.loc[data_df['Details'].str.contains(keyword, case=False, na=False), 'Mshwari_Service'] = keyword
    
    mshwari_transactions = data_df[data_df['Mshwari_Service'].notna()]

    return {"mshwari_transactions": mshwari_transactions.to_dict(orient='records'),
            "count": len(mshwari_transactions)}


def identify_mshwari_financial_transactions_2():

    mshwari_financial_services = ["M-Shwari", "MShwari"]
    data_df = get_transactions_df()

    data_df['Mshwari_Service'] = None

    for keyword in mshwari_financial_services:
        data_df.loc[data_df['Details'].str.contains(keyword, case=False, na=False), 'Mshwari_Service'] = keyword
    
    mshwari_transactions = data_df[data_df['Mshwari_Service'].notna()]

    return {"transactions": mshwari_transactions.to_dict(orient='records')}


# mshwari loan summary
@router.get('/mshwari_loan_summary/')
def mshwari_loan_summary():
    # Identify M-Shwari financial transactions
    mshwari_transactions = identify_mshwari_financial_transactions_2()
    mshwari_transactions = mshwari_transactions['transactions']
    mshwari_transactions_df = pd.DataFrame(mshwari_transactions)

    if mshwari_transactions_df.empty:
        return {"message": "Empty DataFrame"}
    
    # Filter for loan disbursements and repayments
    loan_disbursements = mshwari_transactions_df[mshwari_transactions_df['Transaction_Type'] == 'M-Shwari Loan']
    loan_repayments = mshwari_transactions_df[mshwari_transactions_df['Transaction_Type'] == 'Mshwari Loan Repayment']
    
    # Calculate the required metrics
    total_loan_count = loan_disbursements.shape[0]
    highest_loan_disbursed = loan_disbursements['Paid In'].max() if not loan_disbursements.empty else 0
    highest_loan_paid_back = loan_repayments['Withdrawn'].max() if not loan_repayments.empty else 0
    date_of_last_loan_disbursement = loan_disbursements['Completion Time'].max() if not loan_disbursements.empty else None
    date_of_last_loan_repayment = loan_repayments['Completion Time'].max() if not loan_repayments.empty else None
    last_amount_borrowed = loan_disbursements.loc[loan_disbursements['Completion Time'].idxmax(), 'Paid In'] if not loan_disbursements.empty else 0
    last_amount_paid_back = loan_repayments.loc[loan_repayments['Completion Time'].idxmax(), 'Withdrawn'] if not loan_repayments.empty else 0
    total_loan_disbursed_amount = loan_disbursements['Paid In'].sum() if not loan_disbursements.empty else 0
    total_loan_paid_back_amount = loan_repayments['Withdrawn'].sum() if not loan_repayments.empty else 0
    
    return {
        "total_loan_count": total_loan_count,
        "highest_loan_disbursed": highest_loan_disbursed,
        "highest_loan_paid_back": highest_loan_paid_back,
        "date_of_last_loan_disbursement": date_of_last_loan_disbursement,
        "date_of_last_loan_repayment": date_of_last_loan_repayment,
        "last_amount_borrowed": last_amount_borrowed,
        "last_amount_paid_back": last_amount_paid_back,
        "total_loan_disbursed_amount": total_loan_disbursed_amount,
        "total_loan_paid_back_amount": total_loan_paid_back_amount
    }


def group_bank_mappings(data, mapping):
    # Create a new column 'Grouped_Bank' initialized with None
    data['Grouped_Bank'] = None

    # Populate 'Grouped_Bank' column using the mapping
    for key, value in mapping.items():
        data.loc[data['Details'].str.contains(key, case=False, na=False), 'Grouped_Bank'] = value
    
    # remove rows where 'Grouped_Bank' is None
    data = data.dropna(subset=['Grouped_Bank'])
    
    return data

# top five received (from bank) count
@router.get('/top_five_received_count/')
def top_five_received_count():

    data_df = get_transactions_df()

    df_grouped = group_bank_mappings(data_df, banks_in_kenya_grouped)

    if df_grouped is None:
        return {"message":"No amount received through the bank"}
    
    # filter transactions with Paid In values
    paid_in_bank_transactions = df_grouped[df_grouped['Paid In'] != 0.0]

    # group by 'Grouped Bank' and count number of transactions
    bank_transaction_counts = paid_in_bank_transactions.groupby('Grouped_Bank').size()

    # sort the counts in descending order & select top 5
    top_five_banks = bank_transaction_counts.sort_values(ascending=False).head(5)

    # Convert to dictionary with bank names as keys
    result = {
            "top_five_banks": [
                {"bank": bank, "count": count} 
                for bank, count in top_five_banks.items()
            ]
    }

    return result


# top five sent (from bank) count
@router.get('/top_five_sent_count/')
def top_five_sent_count():

    data_df = get_transactions_df()

    df_grouped = group_bank_mappings(data_df, banks_in_kenya_grouped)

    if df_grouped is None:
        return {"message":"No amount received through the bank"}    
    
    # filter transactions with Paid In values
    paid_in_bank_transactions = df_grouped[df_grouped['Withdrawn'] != 0.0]

    # group by 'Grouped Bank' and count number of transactions
    bank_transaction_counts = paid_in_bank_transactions.groupby('Grouped_Bank').size()

    # sort the counts in descending order & select top 5
    top_five_banks = bank_transaction_counts.sort_values(ascending=False).head(5)

    # Convert to dictionary with bank names as keys
    result = {
            "top_five_banks": [
                {"bank": bank, "count": count} 
                for bank, count in top_five_banks.items()
            ]
    }

    return result


def identify_safaricom_financial_services_2():
    # Get DataFrame
    data_df = get_transactions_df()
    
    if data_df is None or data_df.empty:
        return {"transactions": [], "message": "No data available"}
    
    try:
        # Work with copy
        df = data_df.copy()
        
        # Initialize service column
        df['Financial_Service'] = None
        
        # Map services
        for keyword in safaricom_financial_services:
            mask = df['Details'].str.contains(keyword, case=False, na=False)
            df.loc[mask, 'Financial_Service'] = keyword
        
        # Filter services
        services_df = df[df['Financial_Service'].notna()]
        
        # Return with column info
        return {
            "transactions": services_df.to_dict(orient='records'),
            "columns": services_df.columns.tolist()
        }
    except Exception as e:
        print(f"Error in identify_safaricom_financial_services_2: {e}")
        return {"transactions": [], "error": str(e)}


# fuliza transaction ( How are customers using fuliza)
#How our users are using fuliza 
@router.get('/fuliza_usage/')
def fuliza_usage():
    #returns banks client uses, and all the bank transactions
    client_saf_transactions = identify_safaricom_financial_services_2()

    if client_saf_transactions is None:
        return {"message": "Client does not use Fuliza"}

    data_df = pd.DataFrame(client_saf_transactions['transactions'])
    fuliza_data = data_df[data_df["Financial_Service"] == 'Fuliza']

    if fuliza_data.empty:
        return {"message": "No Fuliza usage found"}
    
    return {"fuliza_usage": fuliza_data.to_dict(orient='records')}


# fuliza loan summary
@router.get('/fuliza_loan_summary/')
def fuliza_loan_summary():

    data_df = get_transactions_df()
    # Identify M-Shwari financial transactions
    
    # Filter for loan disbursements and repayments
    loan_disbursements = data_df[data_df['Transaction_Type'] == 'Fuliza Loan']
    loan_repayments = data_df[data_df['Transaction_Type'] == 'Fuliza Loan Repayment']
    
    # Calculate the required metrics
    loan_count = len(loan_disbursements)
    highest_amount_paid= loan_repayments["Withdrawn"].max()
    highest_amount_disbured = loan_disbursements["Paid In"].max()
    date_of_last_loan_disbursement = loan_disbursements['Completion Time'].max()
    date_of_last_loan_repayment = loan_repayments['Completion Time'].max()
    last_amount_borrowed = loan_disbursements.loc[loan_disbursements['Completion Time'].idxmax(), 'Paid In'] if not loan_disbursements.empty else 0
    last_amount_paid_back = loan_repayments.loc[loan_repayments['Completion Time'].idxmax(), 'Withdrawn'] 
    total_disbursed = loan_disbursements["Paid In"].sum()
    total_paid = loan_repayments["Withdrawn"].sum()
    Total_balance = total_disbursed - total_paid
    
    return {
        "total_loan_count": loan_count,
        "highest_loan_disbursed": highest_amount_disbured,
        "highest_loan_paid_back": highest_amount_paid,
        "date_of_last_loan_disbursement": date_of_last_loan_disbursement,
        "date_of_last_loan_repayment": date_of_last_loan_repayment,
        "last_amount_borrowed": last_amount_borrowed,
        "last_amount_paid_back": last_amount_paid_back,
        "total_loan_disbursed_amount": total_disbursed,
        "total_loan_paid_back_amount": total_paid,
        "total_loan_balance":Total_balance
    }
