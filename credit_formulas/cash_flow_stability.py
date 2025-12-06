import pandas as pd

df = pd.read_csv('mpesa_transactions.csv')
print(df.columns)

def net_flow_income(df):
    send_money_df = df[df['Transaction_Type'] == 'Send Money']
    total_sent = sum(send_money_df['Withdrawn'])
    total_recieved =sum(df['Paid In'])
    net_flow = total_recieved - total_sent 
    return net_flow

def income_regularity(df): 
    monthly_income = df.groupby('month_name')['Paid In'].sum()
    income_reg =monthly_income.std()
    return income_reg

def average_monthly_income(df): 
    monthly_income = df.groupby('month_name')['Paid In'].sum()
    average_monthly_income =monthly_income.mean()
    return average_monthly_income

net_flow = net_flow_income(df)
monthly_income_regularity = income_regularity(df)
avg_monthly_income = average_monthly_income(df)

print(f"Net flow {net_flow}")
print(f"Income regularity {monthly_income_regularity}")
print(f"Average monthly income{ avg_monthly_income}")