#third-party imports
import pandas as pd

#personal imports
import db_creator as dbc
import generic_tools as gt
import specific_tools as st

#SETTINGS------------------------------

MAKE_PLOT = 0 #0 -> non fare il grafico / 1 -> fai il grafico
TO_PLOT = 'open'
STATUS = 'online'

COSTS = 0
INSTRUMENT = 1 #1 -> equity/forex, 2 -> future
OPERATION_MONEY = 10000
DIRECTION = 'short'
ORDER_TYPE = 'market'

#--------------------------------------

#constructor of the database
if STATUS == 'offline':

    db = pd.read_csv('klinesBTCUSDT.csv')

else:
    
    db = dbc.db_constructor()
    db.to_csv('klinesBTCUSDT.csv')

#decide wether to make a plot or not
if MAKE_PLOT == 1:

    gt.mkplot(db[TO_PLOT])

#builds enter and exit rules, depending on DIRECTION
if DIRECTION == 'long':
    
    enter_rules = st.crossover(db.close, db.hhv20.shift(1))
    exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

else:

    enter_rules = st.crossunder(db.close, db.llv20.shift(1))
    exit_rules = st.crossover(db.close, db.hhv5.shift(1))

#backtest
trading_system = st.apply_trading_system(db, INSTRUMENT, COSTS, DIRECTION, ORDER_TYPE, OPERATION_MONEY, enter_rules, exit_rules)

