#file per funzioni e moduli vari

def todate(timestamp_series):
    """
    changes timestamps in dates
    """
    
    import datetime
    import pandas as pd
    
    ticks = []

    for timestamp in timestamp_series:
        ticks.append(datetime.datetime.fromtimestamp(int(timestamp)/1000))
    
    return(pd.Series(data = ticks))

def tonumerical(Series):
    """
    changes any element of a list-like object into float
    """

    import numpy as np

    temporary_series = []

    for element in Series:
        temporary_series.append(float(element))
    
    return(np.array(temporary_series))

def mkplot(timeSeries):

    """
    creates a lineplot of the given time series
    """

    import matplotlib.pyplot as plt
    import seaborn as sns

    sns.set_theme(style = 'whitegrid')
    sns.lineplot(data = timeSeries, palette = 'tab10')
    plt.show()

    return()