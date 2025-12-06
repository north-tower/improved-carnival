# pesabu-backend

Let:
- I = normalized income stability score
- E = expense discipline score
- F = frequency & activity score
- B = balance health score
- S = social trust score

Then:

Credit Score=300+(I×0.30+E×0.20+F×0.20+B×0.20+S×0.10)×550 <br>
This scales scores between 300–850 (similar to traditional credit bureaus).


### Derive Formula Variables
| Subscore                   | Example Formula (0–1 range)                          |
| -------------------------- | ---------------------------------------------------- |
| Income Stability (I)  | `1 - (std_dev(monthly_income)/mean(monthly_income))` |
| Expense Discipline (E) | `1 - (Σ(sent)/Σ(received))` clipped to [0,1]         |
| Activity (F)           | `min(1, txn_count / 150)`                            |
| Balance Health (B)     | `min(1, avg_end_balance / 20000)`                    |
| Social Trust (S)       | `min(1, repeat_contacts / total_contacts)`           |

### Example Output

| Metric             | Value      | Interpretation             |
| ------------------ | ---------- | -------------------------- |
| Score              | **724**    | Low-risk borrower          |
| Avg Monthly Income | KSh 48,000 | Stable inflows             |
| Expense Ratio      | 0.63       | Moderate spender           |
| Days Active        | 82%        | Very active user           |
| Suggested Limit    | KSh 25,000 | Recommended safe loan size |
