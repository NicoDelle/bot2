import report as rp
import pandas as pd

df = pd.read_csv('trading_system.csv')

report = rp.Report(df)
profit = report.profit
print(profit)
