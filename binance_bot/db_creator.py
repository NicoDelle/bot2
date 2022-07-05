"""
tools to build a database
"""


def set_type(db):

    """
    trasforma tutti gli elementi del DataFrame in float, ad eccezione delle timestamps
    """

    import pandas as pd
    import generic_tools as gt

    df = pd.DataFrame()

    for column in db.columns:
        if column != 'time':
            df[column] = gt.tonumerical(db[column])
        
        else:
            df.set_index(db.time, inplace = True, drop = True)
        
    return(df)

#------------------------------------------------------------------

def db_from_Binance(symbol, interval, limit, timestamp):

    #third-party imports
    from binance.spot import Spot as Client
    import numpy as np
    import pandas as pd

    #personal modules
    import generic_tools as gt

    #INFOS-------------------------------------
    PARAMETER = 'open'
    COLUMNS = [
        'open',
        'high',
        'low',
        'close',
        'volume',
        'trades'
        ]
    #----------------------------------------------
    client = Client(base_url='https://testnet.binance.vision')

    try:
        #creates an array with all the infos
        klines = np.array(client.klines(symbol = symbol, interval = interval, limit = limit, startTime = timestamp))
        status = 'online'
    
    except:
        status = 'offline'

    klines_columns = [
        'timestamp', 
        'open', 
        'high', 
        'low',
        'close',
        'volume', 
        'close time', 
        'quote asset volume', 
        'trades', 
        'Taker buy base asset volume',
        'Taker buy quote asset volume',
        'ignore'
        ]

    if len(klines) != 0:
        db = pd.DataFrame(data = klines, columns = klines_columns)
        #from timestamps to date
        db['time'] = gt.todate(db['timestamp'])
        
        #cleans the dataframe
        labels = [
            'close time',
            'quote asset volume',
            'Taker buy base asset volume',
            'Taker buy quote asset volume',
            'ignore'
            ]
        db.drop(labels = labels, axis = 1, inplace = True)

        #sets all datatypes to floats and sets new index
        df = set_type(db)

        #saves the dataframe into a csv file


        return(df)

    elif status == 'offline':
        return status

    else:
        return 'updated'

#------------------------------------------------------------------

def db_from_csv(symbol, interval, limit, status = 'online'):
    """
    creates the database from an existing csv file, and tries to update it
    """

    import pandas as pd
    
    #reads the csv
    db1 = pd.read_csv(f'{interval}klines-{symbol}.csv', index_col = 'time')
    timestamp = int(db1.timestamp.iloc[-1] + (db1.timestamp.iloc[-1] - db1.timestamp.iloc[-2]))

    #if an internet connection is available, updates the csv
    if status == 'online':

        db2 = db_from_Binance(symbol, interval, limit, timestamp)
        
        if type(db2) != type('str'):

            if len(db2) != 1000:
                repeat = False
            
            else:
                repeat = True
                
            db = pd.concat([db1, db2])
            db.to_csv(f'{interval}klines-{symbol}.csv')
            print('succesfully updated the database')

            return db, repeat


        elif db2 == 'offline':

            repeat = False
            print("failed to retrieve new data, the database won't be updated")
            print('please check your connection or modify your settings (it may be an input error). STATUS: offline')
                
            return set_type(db1), repeat

        elif db2 == 'updated':

            repeat = False
            print('data were up-to-date')

            return set_type(db1), repeat

    else:

        repeat = False
        print('Connection lost: data will not be updated')
        return set_type(db1), repeat

#------------------------------------------------------------------

def make_db(*parameters):
    """
    to assemble the final product
    """

    #defining variables
    interval = parameters[0]
    symbol = parameters[1]
    limit = parameters[2]
    status = parameters[3]
    default_time = parameters[4]
    ema_long_period = parameters[5]
    ema_short_period = parameters[6]


    #third-party imports
    import pandas as pd
    import specific_tools as st

    #checks wether the csv file exists or not
    try:
    
        csv = open(f'{interval}klines-{symbol}.csv')
        file_status = 'file already exists'
        csv.close()


    except:

        file_status = 'file does not exist'

    #if the csv exists, reads data from there
    if file_status == 'file already exists':

        print('retrieving data from an existing database...\n')

        repeat = True
        while repeat:

            db, repeat = db_from_csv(symbol, interval, limit, status)

    #if the spreadsheet does not exist but internet connection is available, creates it through API
    elif status == 'online':

        db = db_from_Binance(symbol, interval, limit, default_time)
        
        db.to_csv(f'{interval}klines-{symbol}.csv')
        print('retrieving new data from the API...\n')

        if len(db) == 1000:
            
            repeat = True
            while repeat:

                db, repeat = db_from_csv(symbol, interval, limit)
                print('seems like lots of data uh?\n')
        
        print('database succesfully created')
        db.to_csv(f'{interval}klines-{symbol}.csv')

    else:
        #if any other try failed, returns an empty list as a sentinel value
        print('could not reade nor create a database.')
        print(f'STATUS: {status}')

        return []


    db['hhv20'] = st.hhv20(db['high'])
    db['llv20'] = st.llv20(db['low'])
    db['hhv5'] = st.hhv5(db['high'])
    db['llv5'] = st.llv5(db['low'])
    db[f'EMA{ema_long_period}'] = st.ema(db['close'], ema_long_period)
    db[f'EMA{ema_short_period}'] = st.ema(db['close'], ema_short_period)

    return db 
