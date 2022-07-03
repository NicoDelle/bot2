import pandas as pd
import specific_tools as st

ema_period = 200

db = pd.read_csv('1mklines-BTCUSDT.csv', index_col = 'time')
ema = st.ema(db['close'], ema_period)
db[f'EMA{ema_period}'] = ema

print(db[f'EMA{ema_period}'])
