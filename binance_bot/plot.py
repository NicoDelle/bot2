#from db_creator import db_from_csv
import pandas as pd
from generic_tools import mkplot 

symbol = 'BTCUSDT'
interval = '15m'
limit = 1000

#db = db_from_csv(symbol, interval, limit)
db = pd.read_csv('15mklines-BTCUSDT.csv', index_col = 'time')

mkplot(db['close'])
