#third-party imports
from turtle import position
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

#personal imports
import db_creator as dbc
import generic_tools as gt
import specific_tools as st

#SETTINGS------------------------------

SYMBOL = 'BTCUSDT'
INTERVAL = '1m'
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
status = 'online'
#--------------------------------------

COSTS = 0
INSTRUMENT = 1 #1 -> equity/forex, 2 -> future
OPERATION_MONEY = 1000
DIRECTION = 'short'
ORDER_TYPE = 'market'

#--------------------------------------

#constructor of the database

#checks wether the csv spreadsheet exists or not
try:
    
    csv = open(f'{INTERVAL}klines-{SYMBOL}.csv')
    file_status = 'file already exists'
    csv.close()


except:

    file_status = 'file do exist'

#if the spreadsheed exists, reads the file from the csv
if file_status == 'file already exists':

    print('retrieving data from an existing database...\n')

    repeat = True
    while repeat:

        db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT, status)

#if the spreadsheet does not exist but internet connection is available, creates it through API
elif status == 'online':
    db = dbc.db_constructor(SYMBOL, INTERVAL, LIMIT, DEFAULT_TIME)
    print('retrieving new data from the API...\n')

    if len(db) == 1000:
        
        repeat = True
        while repeat:

            db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT)
            print('seems like lots of data uh?\n')
    
    print('database succesfully created')

else:
    print('could not reade nor create a database.')
    print(f'STATUS: {status}')



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
