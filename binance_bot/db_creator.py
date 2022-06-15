def set_type(db):
    import pandas as pd
    import functions as f

    df = pd.DataFrame()

    for column in db.columns:
        if column != 'time':
            df[column] = f.tonumerical(db[column])
        
        else:
            df[column] = db[column]
            df.set_index('time', inplace = True)

    return(df)


def db_constructor():

    #third-party imports
    from binance.spot import Spot as Client
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    #personal modules
    import functions as f

    #settings
    SYMBOL = 'BTCUSDT'
    INTERVAL = '15m'
    LIMIT = '1000'
    STARTTIME = '1654819200000'
    PARAMETER = 'open'
    COLUMNS = [
        'open',
        'high',
        'low',
        'close',
        'volume',
        'trades'
        ]

    client = Client(base_url='https://testnet.binance.vision')

    #creates an array with all the infos
    klines = np.array(client.klines(symbol = SYMBOL, interval = INTERVAL, limit = LIMIT, startTime = STARTTIME))

    klines_columns = [
        'open time', 
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
    db['time'] = f.todate(db['open time'])
  
    #cleans the dataframe
    labels = [
        'open time',
        'close time',
        'quote asset volume',
        'Taker buy base asset volume',
        'Taker buy quote asset volume',
        'ignore'
        ]

    db.drop(labels = labels, axis = 1, inplace = True)

    #sets all datas to floats and sets new index
    df = set_type(db)

    return(df)
