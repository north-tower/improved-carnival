# import various libraries
import pandas as pd
import calendar

df = pd.read_csv('mpesa_transactions.csv')
 
def end_month_balance(df):
    # Sort by Completion Time
    df = df.sort_values('Completion Time')
    # Take last balance per month
    end_of_month_balance = df.groupby('month_name').last()[['Balance']].reset_index()
    avg_end_of_month_balance = end_of_month_balance['Balance'].mean()

    return avg_end_of_month_balance


def low_balance_frequency(df):
    # Ensure datetime
    df['Completion Time'] = pd.to_datetime(df['Completion Time'], errors='coerce')

    # Extract date
    df['date_only'] = df['Completion Time'].dt.date

    # Get last balance per day
    daily_balance = df.groupby('date_only')['Balance'].last().reset_index()

    # Compute average balance
    avg_balance = daily_balance['Balance'].mean()

    # Count days with balance < average
    low_balance_days = (daily_balance['Balance'] < avg_balance).sum()

    # Total days in all months represented in dataset
    df['month'] = df['Completion Time'].dt.month
    unique_months = df['month'].unique()
    year = df['Completion Time'].dt.year.min()  # assumes single year
    total_days = sum(calendar.monthrange(year, m)[1] for m in unique_months)

    # Low-balance frequency
    frequency = low_balance_days / total_days

    return frequency

end_of_month_balance = end_month_balance(df)
low_balance = low_balance_frequency(df)

print(f"end of month balance {end_of_month_balance}")
print(f"low balancef frequency {low_balance}")