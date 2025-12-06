## generate the income_stability 

# import various libraries
import pandas as pd

df = pd.read_csv('mpesa_transactions.csv')

def income_stability (df,month,paid_in):
    # monthly income 
    monthly_income = df.groupby(month)[paid_in].sum()
    # standard deviation OF monthly_income
    std_dev = monthly_income.std()

        # mean OF monthly_income
    mean = monthly_income.mean()
    # Ensure score stays between 0 and 1
    stability_score = max(0, 1 - (std_dev / mean))

    print(stability_score)

income_stability(df,'month_name','Paid In')