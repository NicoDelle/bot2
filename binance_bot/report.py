"""
to analyse the statistics of the tading system
"""
#third-party imports
import pandas as pd
import datetime

#personal imports
import specific_tools as st
from main import EMA_PERIOD

df = pd.read_csv('trading_system.csv', index_col = 'timestamp')

#st.plot_equity(df.open_equity, 'red')
#st.plot_drawdown(df.open_equity)

profit = round(df.closed_equity.iloc[-1], 2)
operations = df.operations.dropna()
avg_trade = round(df.operations.mean(), 2)
max_dd = round(st.drawdown(df.open_equity).min(), 2)
avg_dd_no0 = round(st.drawdown(df.open_equity[df.open_equity < 0]).mean(), 2)

avg_loss = round(df.operations[df.operations < 0].mean(), 2)
max_loss = round(df.operations.min(), 2)
max_loss_date = df['operations'].idxmin()

avg_gain = round(df.operations[df.operations > 0].mean(), 2)
max_gain = round(df.operations.max(), 2)
max_gain_date = df['operations'].idxmax()

gross_profit = round(df.operations[df.operations > 0].sum(), 2)
gross_loss = round(df.operations[df.operations <= 0].sum(), 2)
if gross_loss != 0:
    pf = round(abs(gross_profit / gross_loss), 2)
else:
    pf = round(abs(gross_profit / 0.0000000000001), 2)

percent_win = round((df.operations[df.operations > 0].count() / df.operations.count()) * 100, 2)
if avg_loss != 0:
    RR_ratio = round(avg_gain / abs(avg_loss), 2)
else:
    RR_ratio = 'infinito'

max_delay = st.delay_between_peaks(df['open_equity']).max()
avg_delay = st.avg_delay_between_peaks(df['open_equity'])

print(f'\naverage trade: {avg_trade}$')
print(f'profit: {profit}$\n')
print(f'max drawdown: {max_dd}$')
print(f'average drawdown: {avg_dd_no0}$\n')
print(f'average loss: {avg_loss}$')
print(f'max loss: {max_loss}$, {datetime.datetime.fromtimestamp(int(max_loss_date) / 1000)}')
print(f'average gain: {avg_gain}$')
print(f'max gain: {max_gain}$, {datetime.datetime.fromtimestamp(int(max_gain_date) / 1000)}\n')
print('*'*20)
print(f'\nProfit Factor: {pf}')
print(f'Percent win: {percent_win}%')
print(f'Reward/risk ratio: {RR_ratio}')
print(f'Max delay between peaks: {max_delay}')
print(f'Average delay between peaks: {avg_delay}')

lines = [df.close, df[f'EMA{EMA_PERIOD}']]
st.plot_multiple(*lines)
