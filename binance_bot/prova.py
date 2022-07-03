import pandas as pd
import specific_tools as st

ema_period = 200

db = pd.read_csv('1mklines-BTCUSDT.csv', index_col = 'time')
db['EMA200'] = st.ema(db['close'], 200)
db['EMA60'] = st.ema(db['close'], 60)
db['trend'] = st.long_or_short(db.EMA60, db.EMA200, 'short', 200)

groups = db.groupby(db.trend).groups

