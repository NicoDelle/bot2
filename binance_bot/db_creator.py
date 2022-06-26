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
            df[column] = db[column]
            df.set_index('time', inplace = True)

    return(df)


def db_constructor(symbol, interval, limit, timestamp):

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

    #creates an array with all the infos
    klines = np.array(client.klines(symbol = symbol, interval = interval, limit = limit, startTime = timestamp))

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

    #sets all datas to floats and sets new index
    df = set_type(db)

    df.to_csv(f'{interval}klines-{symbol}.csv')

    return(df)

#------------------------------------------------------------------

def db_from_csv(symbol, interval, limit, status = 'online'):

    import pandas as pd

    db1 = pd.read_csv(f'{interval}klines-{symbol}.csv', index_col = 'time')
    timestamp = int(db1.timestamp.iloc[-1] + 900000)

    if status == 'online':

        db2 = db_constructor(symbol, interval, limit, timestamp)
        
        if len(db2) != 1000:
            repeat = False
        
        else:
            repeat = True
        
        db = pd.concat([db1, db2])
        db.to_csv(f'{interval}klines-{symbol}.csv')
        print('succesfully updated the database')

        return db, repeat
    
    else:

        repeat = False
        print("failed to retrieve new data, the database won't be updated")
        print(f'please check your connection or modify your settings. STATUS: {status}')
        
        return db1, repeat
