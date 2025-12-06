import pandas as pd


# A function to determine whether  a user spends or save 
def save_or_spend(row):
    # Identify the keywords
    keywords = ["M-Shwari Lock Deposit", "Saving", "savings", "mmf", "M-shwari Deposit", "Sanlam"]
    
    # Get the Details value and convert to string
    details = str(row['Details']) if pd.notna(row['Details']) else ''
    
    # Check if the current row's 'Details' contains any of the keywords (case-insensitive)
    if any(keyword.lower() in details.lower() for keyword in keywords):
        return 'save'
    else:
        return 'spend'
    

# total amount transacted - received
def total_received(data):
    total = data['Paid In'].sum()
    return total


# total amount transacted - withdrawn
def total_withdrawn(data):
    total = data['Withdrawn'].sum()
    return total


def calculate_mpesa_fico_score(data):
    """
    Calculate a FICO-like credit score using M-Pesa transactions.
    """
    # Filtering transactions
    data_spent = data[data["save/spend"] == "spend"]
    data_save = data[data["save/spend"] == "save"]
    data_loans = data[data["Transaction_Type"].str.contains("Fuliza Loan|Hustler", case=False, na=False)]
    data_fuliza_loans = data[data["Transaction_Type"].str.contains("Fuliza Loan Repayment|Hustler Repayment", case=False, na=False)]

    # Summing financial data
    total_loans = total_received(data_loans)
    total_repayments = total_withdrawn(data_fuliza_loans)
    loan_requests = len(data_loans)
    total_income = total_received(data)
    total_expense = total_withdrawn(data_spent)
    total_saved = total_withdrawn(data_save)
    total_loan_income = total_received(data_loans)

    # Prevent division by zero
    total_income = max(total_income, 1)

    # **1. Payment History (25%)** → More repayments = higher score
    payment_history_score = min(1, total_repayments / (total_loan_income * 0.3))

    # **2. Income Spending Ratio (20%)** → Less spending = better score
    income_spending_ratio = max(0, (total_income - total_expense) / total_income)

    loan_usage_ratio = loan_requests / max(1, len(data))  # Adjust for frequent usage
    credit_score = max(0, 1 - loan_usage_ratio) 
    # **4. Savings Ratio (10%)** → Higher savings = better score
    saving_ratio = min(1, total_saved / total_income)

    # **5. Debt-to-Income Ratio (10%)** → More debt = lower score
    debt_to_income_ratio = min(1, total_loans / total_income)
    debt_score = max(0, 1 - debt_to_income_ratio)

    # **Final FICO-Like Score Calculation**
    final_score = (
        (payment_history_score * 0.25) +
        (income_spending_ratio * 0.20) +
        (credit_score * 0.10) +
        (saving_ratio * 0.10) +
        (debt_score * 0.10)
    )

    # Scale to FICO range (300-850)
    credit_score_final = int(300 + final_score * 550)

    return  credit_score_final


def credit_score_status(final_score):
    if final_score >= 800:
        return "Excellent"
    elif final_score >= 740:
        return "Very Good"
    elif final_score >= 670:
        return "Good"
    elif final_score >= 580:
        return "Fair"
    else:
        return "Poor"