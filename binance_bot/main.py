#third-party imports
from turtle import position
from numpy import float64
import pandas as pd

#personal imports
import db_creator as dbc
import specific_tools as st
import orders

#SETTINGS------------------------------

status = 'online'
ORDER_TYPE = 'market'
direction = 'short'
TREND_FOLLOWING = 'off'
SYMBOL = 'BTCEUR'
INTERVAL = '1d'
LIMIT = '1000'
INSTRUMENT = 1 #1 -> equity/forex, 2 -> future
OPERATION_MONEY = 1000
TICK = 0.01
EMA_LONG_PERIOD = 60
EMA_SHORT_PERIOD = 20
DEFAULT_TIME = '1609459200000'
PARAMETER = 'open'
COLUMNS = [
    'open',
    'high',
    'low',
    'close',
    'volume',
    'trades'
    ]
#------------------------------------------------
parameters = [
    INTERVAL, SYMBOL, LIMIT, status, DEFAULT_TIME, 
    EMA_LONG_PERIOD, EMA_SHORT_PERIOD, TREND_FOLLOWING
]

#constructor of the database
db = dbc.make_db(*parameters)

#orders
if ORDER_TYPE == 'stop':

    enter_rules, exit_rules, enter_level = orders.stop_order(db, direction)
    
    #args
    system_args = [
        enter_level
        ]

if ORDER_TYPE == 'market':

    if TREND_FOLLOWING == 'on':
        
        enter_rules, exit_rules = orders.trend_following_order(db, EMA_SHORT_PERIOD, 
        EMA_LONG_PERIOD, direction)

    else:
    
       enter_rules, exit_rules = orders.market_order(db, direction)

    #args
    system_args = [
        ]


#backtest
trading_system = st.apply_trading_system(
    db, INSTRUMENT, direction, ORDER_TYPE, 
    OPERATION_MONEY, enter_rules, exit_rules, TICK, 
    *system_args)
