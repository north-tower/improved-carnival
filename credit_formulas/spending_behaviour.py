import pandas as pd

def load_data(filepath):
    """Load M-Pesa transaction data from CSV."""
    return pd.read_csv(filepath)


def calculate_expense_ratio(df):
    """
    Calculate expense ratio: total sent / total received.
    """
    send_money_df = df[df['Transaction_Type'] == 'Send Money']
    total_sent = send_money_df['Withdrawn'].sum()
    total_received = df['Paid In'].sum()
    
    if total_received == 0:
        return 0
    
    expense_ratio = total_sent / total_received
    return expense_ratio


def calculate_cash_withdrawal_ratio(df):
    """
    Calculate cash withdrawal ratio: total withdrawals / total sent.
    """
    withdraw_df = df[df['Transaction_Type'] == 'Cash Withdrawal']
    send_money_df = df[df['Transaction_Type'] == 'Send Money']
    
    total_withdrawals = withdraw_df['Withdrawn'].sum()
    total_sent = send_money_df['Withdrawn'].sum()
    
    if total_sent == 0:
        ratio = 0
    else:
        ratio = total_withdrawals / total_sent
    
    return {
        'total_withdrawals': total_withdrawals,
        'total_sent': total_sent,
        'ratio': ratio
    }


def calculate_merchant_diversity(df):
    """
    Calculate merchant diversity: unique merchants / total merchant transactions.
    """
    df_paybills = df[df['Transaction_Type'].isin(["Till No", "Pay Bill"])]
    unique_merchants = df_paybills['Details'].nunique()
    total_transactions = len(df_paybills)
    
    if total_transactions == 0:
        diversity_ratio = 0
    else:
        diversity_ratio = unique_merchants / total_transactions
    
    return {
        'unique_merchants': unique_merchants,
        'total_transactions': total_transactions,
        'diversity_ratio': diversity_ratio
    }



def print_metrics(df):
    """Calculate and print all metrics."""
    # Expense Ratio
    exp_ratio = calculate_expense_ratio(df)
    print(f"Expense Ratio: {exp_ratio:.4f}")
    print()
    
    # Cash Withdrawal Ratio
    withdrawal_data = calculate_cash_withdrawal_ratio(df)
    print(f"Cash Withdrawal Ratio: {withdrawal_data['ratio']:.4f}")
    print()
    
    # Merchant Diversity
    merchant_data = calculate_merchant_diversity(df)
    print(f"Merchant Diversity: {merchant_data['diversity_ratio']:.4f}")



def main():
    """Main function to run all calculations."""
    df = load_data('credit_formulas/mpesa_transactions.csv')
    print_metrics(df)

if __name__ == "__main__":
    main()