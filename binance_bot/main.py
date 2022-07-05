#third-party imports
from turtle import position
from numpy import float64
import pandas as pd

#personal imports
import db_creator as dbc
import generic_tools as gt
import specific_tools as st

#SETTINGS------------------------------

status = 'online'
ORDER_TYPE = 'market'
direction = 'long'
TREND_FOLLOWING = 'on'
SYMBOL = 'BTCUSDT'
INTERVAL = '1m'
LIMIT = '1000'
INSTRUMENT = 1 #1 -> equity/forex, 2 -> future
OPERATION_MONEY = 1000
TICK = 0.01
EMA_LONG_PERIOD = 200
EMA_SHORT_PERIOD = 60
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
#------------------------------------------------

#constructor of the database
#checks wether the csv spreadsheet exists or not
try:
    
    csv = open(f'{INTERVAL}klines-{SYMBOL}.csv')
    file_status = 'file already exists'
    csv.close()


except:

    file_status = 'file does not exist'

#if the spreadsheed exists, reads the file from the csv
if file_status == 'file already exists':

    print('retrieving data from an existing database...\n')

    repeat = True
    while repeat:

        db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT, status)

#if the spreadsheet does not exist but internet connection is available, creates it through API
elif status == 'online':
    db = dbc.db_from_Binance(SYMBOL, INTERVAL, LIMIT, DEFAULT_TIME)
    db.to_csv(f'{INTERVAL}klines-{SYMBOL}.csv')
    print('retrieving new data from the API...\n')

    if len(db) == 1000:
        
        repeat = True
        while repeat:

            db, repeat = dbc.db_from_csv(SYMBOL, INTERVAL, LIMIT)
            print('seems like lots of data uh?\n')
    
    print('database succesfully created')
    db.to_csv(f'{INTERVAL}klines-{SYMBOL}.csv')

else:
    print('could not reade nor create a database.')
    print(f'STATUS: {status}')



db['hhv20'] = st.hhv20(db['high'])
db['llv20'] = st.llv20(db['low'])
db['hhv5'] = st.hhv5(db['high'])
db['llv5'] = st.llv5(db['low'])
db[f'EMA{EMA_LONG_PERIOD}'] = st.ema(db['close'], EMA_LONG_PERIOD)
db[f'EMA{EMA_SHORT_PERIOD}'] = st.ema(db['close'], EMA_SHORT_PERIOD)


if ORDER_TYPE == 'stop':

    #builds enter and exit rules, depending on DIRECTION
    if direction == 'long':
        
        enter_rules = db.close > 0
        enter_level = db.hhv20.shift(1)
        exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

    else:

        enter_rules = db.close > 0
        enter_level = db.llv20.shift(1)
        exit_rules = st.crossover(db.close, db.hhv5.shift(1))
    
    #args
    system_args = [
        enter_level
        ]

if ORDER_TYPE == 'market':

    if TREND_FOLLOWING == 'on':
        
        db['trend'] = st.long_or_short(db[f'EMA{EMA_SHORT_PERIOD}'], db[f'EMA{EMA_LONG_PERIOD}'], direction, EMA_LONG_PERIOD)
        groups = db.groupby(db.trend).groups
        db.reset_index(drop = True, inplace = True)
        enter_rules = 'empty'

        temporary_index = [0]
        for n in db.index.delete(0):
            
            #decides wether the trend changed or not
            if db.trend.iloc[n] == db.trend.iloc[n - 1]:

                temporary_index.append(n)
            #if the trend changed, it generates enter and exit rules for that portion of 
            #the prices, and then combine them with the previous rules    
            else:

                if db.trend.iloc[n - 1] == 1:
                    prov_enter_rules = st.crossover(db.close.iloc[temporary_index[0]:temporary_index[-1]], db.hhv20.iloc[temporary_index[0]:temporary_index[-1]].shift(1))
                    prov_exit_rules = st.crossunder(db.close.iloc[temporary_index[0]:temporary_index[-1]], db.llv5.iloc[temporary_index[0]:temporary_index[-1]].shift(1))

                else:
                    prov_enter_rules = st.crossunder(db.close.iloc[temporary_index[0]:temporary_index[-1]], db.llv20.iloc[temporary_index[0]:temporary_index[-1]].shift(1))
                    prov_exit_rules = st.crossover(db.close.iloc[temporary_index[0]:temporary_index[-1]], db.hhv5.iloc[temporary_index[0]:temporary_index[-1]].shift(1))

                #to make sure we have not any open operation while a trend is changing 
                prov_enter_rules.iloc[-1] = False
                prov_exit_rules.iloc[-1] = True    

                if type(enter_rules) == type('str'):
                    enter_rules = pd.Series(prov_enter_rules)
                    exit_rules = pd.Series(prov_exit_rules)
                
                else:
                    enter_rules = pd.concat([enter_rules, prov_enter_rules])
                    exit_rules = pd.concat([exit_rules, prov_exit_rules])

                temporary_index = [n]

    else:
    
        #builds enter and exit rules, depending on DIRECTION
        if direction == 'long':
        
            enter_rules = st.crossover(db.close, db.hhv20.shift(1))
            exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

        else:

            enter_rules = st.crossunder(db.close, db.llv20.shift(1))
            exit_rules = st.crossover(db.close, db.hhv5.shift(1))

    #args
    system_args = [
        ]


#backtest
trading_system = st.apply_trading_system(db, INSTRUMENT, direction, ORDER_TYPE, OPERATION_MONEY, enter_rules, exit_rules, TICK, *system_args)
