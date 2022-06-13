#file per funzioni e moduli vari

def todate(timestamp_series):
    
    import datetime
    import pandas as pd
    
    ticks = []

    for timestamp in timestamp_series:
        ticks.append(datetime.datetime.fromtimestamp(int(timestamp)/1000))
    
    return(pd.Series(data = ticks))

def tonumerical(Series):

    import numpy as np

    temporary_series = []

    for element in Series:
        temporary_series.append(float(element))
    
    return(np.array(temporary_series))