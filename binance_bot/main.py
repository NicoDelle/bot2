#third-party imports
from graphql import do_types_overlap
import pandas as pd

#personal imports
import db_creator as dbc
import generic_tools as gt
import specific_tools as st

#SETTINGS------------------------------

SYMBOL = 'BTCUSDT'
INTERVAL = '15m'
LIMIT = '1000'
DEFAULT_TIME = '1654819200000'
PARAMETER = 'open'
COLUMNS = [
    'open',
    'high',
    'low',
    'close',
    'volume',
    'trades'
    ]

#--------------------------------------

MAKE_PLOT = 1 #0 -> non fare il grafico / 1 -> fai il grafico
TO_PLOT = 'close'
STATUS = 'online'

#--------------------------------------

COSTS = 0
INSTRUMENT = 1 #1 -> equity/forex, 2 -> future
OPERATION_MONEY = 10000
DIRECTION = 'short'
ORDER_TYPE = 'market'

#--------------------------------------

#constructor of the database

try:
    
    repeat = True
    while repeat:

        db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT)
        print('da csv:\n')

except:

    db = dbc.db_constructor(SYMBOL, INTERVAL, LIMIT, DEFAULT_TIME)
    print('da API\n')

    if len(db) == 1000:
        
        repeat = True
        while repeat:

            db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT)
            print('da csv\n')

db['hhv20'] = st.hhv20(db['high'])
db['llv20'] = st.llv20(db['low'])
db['hhv5'] = st.hhv5(db['high'])
db['llv5'] = st.llv5(db['low'])

#builds enter and exit rules, depending on DIRECTION
if DIRECTION == 'long':
    
    enter_rules = st.crossover(db.close, db.hhv20.shift(1))
    exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

else:

    enter_rules = st.crossunder(db.close, db.llv20.shift(1))
    exit_rules = st.crossover(db.close, db.hhv5.shift(1))

#backtest
trading_system = st.apply_trading_system(db, INSTRUMENT, COSTS, DIRECTION, ORDER_TYPE, OPERATION_MONEY, enter_rules, exit_rules)

#decide wether to make a plot or not
if MAKE_PLOT == 1:

    gt.mkplot(db[TO_PLOT])
