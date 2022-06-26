"""
to analyse the statistics of the tading system
"""
#third-party imports
import pandas as pd

#personal imports
import specific_tools as st

df = pd.read_csv('trading_system.csv', index_col = 'time')

#st.plot_equity(df.open_equity, 'red')
st.plot_drawdown(df.open_equity)