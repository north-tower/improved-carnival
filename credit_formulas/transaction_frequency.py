
# import various libraries
import pandas as pd
import calendar

df = pd.read_csv('mpesa_transactions.csv')
print(df.columns)


# transaction count per month function
def transaction_count(df):

    transactions_per_month = df.groupby('month_name').size().reset_index(name='transaction_count')
    # transaction_count
    transactions_per_month = df.groupby('month_name').size().reset_index(name='transaction_count')

    #average transaction per month 
    avg_transaction_per_month = transactions_per_month['transaction_count'].mean()
    
    return avg_transaction_per_month


def active_days(df):
    # Ensure datetime
    df['Completion Time'] = pd.to_datetime(df['Completion Time'], errors='coerce')
    df = df.dropna(subset=['Completion Time'])

    # Extract just the date and month
    df['date_only'] = df['Completion Time'].dt.date
    df['month'] = df['Completion Time'].dt.month

    # 1️Active days — distinct dates with at least one transaction
    active_days = df['date_only'].nunique()

    # 2️Total days — sum of total calendar days in all distinct months in dataset
    unique_months = df['month'].unique()
    total_days = sum(calendar.monthrange(2025, m)[1] for m in unique_months)

    activity_ratio = round(active_days / total_days,2)
    return activity_ratio


transaction_count_per_month = transaction_count(df)
active_days_ratio = active_days(df)

print(f"Transaction count per month {transaction_count_per_month}")
print(f"Overall activity ratio:{active_days_ratio}")
