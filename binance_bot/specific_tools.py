"""
specific tools for algorithmical trading
"""

def hhv20(prices):
    """
    selects the max value in a timeframe of 20 periods
    """
    return(prices.rolling(20).max())

def hhv5(prices):
    """
    selects the max value in a timeframe of 5 periods
    """
    return(prices.rolling(5).max())

def llv20(prices):
    """
    selects the min value in a timeframe of 20 periods
    """
    return(prices.rolling(20).min())

def llv5(prices):
    """
    selects the min value in a timeframe of 5 periods
    """
    return(prices.rolling(5).min())

#-------------------------------------------------------

def crossover(array1, array2):
    """
    returns a list of booleans: True if array1 crossed over array2 in that specific position, otherwise returns False
    """
    return (array1 > array2) & (array1.shift(1) < array2.shift(1))

def crossunder(array1, array2):
    """
    returns a list of booleans: True if array1 crossed under array2 in that specific position, otherwise returns False
    """
    return (array1 < array2) & (array1.shift(1) > array2.shift(1))

#-------------------------------------------------------

def marketposition_generator(enter_rules, exit_rules):
    """
    define the position we want to take in the market
    """

    import pandas as pd

    df = pd.DataFrame(index = enter_rules.index)
    df['enter rules'] = enter_rules
    df['exit rules'] = exit_rules

    status = 0
    mp = []
    for (i, j) in zip(enter_rules, exit_rules):
        if status == 0:
            if i == 1 and j != -1:
                status = 1
        else:
            if j == -1:
                status = 0
        mp.append(status)

    df['mp new'] = mp
    df['mp new'] = df['mp new'].shift(1)
    df.iloc[0,2] = 0

    return df['mp new']

#-----------------------------------------------

def apply_trading_system(dataframe, instrument, costs, direction, order_type, operation_money, enter_rules, exit_rules):
    
    """
    core of the trading system
    """

    import numpy as np

    dataframe = dataframe.copy()

    dataframe['enter_rules'] = enter_rules.apply(lambda x: 1 if x == True else 0)
    dataframe['exit_rules'] = exit_rules.apply(lambda x: -1 if x == True else 0)
    dataframe['mp'] = marketposition_generator(dataframe.enter_rules, dataframe.exit_rules)

    #marks entry price
    if order_type == 'market':
        dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), dataframe.open, np.nan)
    
    #marks the number of stocks
    if instrument == 1:
        dataframe['number_of_stocks'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), operation_money / dataframe.entry_price, np.nan)
    
    #extends the new columns where necessary
    dataframe['entry_price'] = dataframe['entry_price'].fillna(method = 'ffill')
    if instrument == 1:
        dataframe['number_of_stocks'] = dataframe['number_of_stocks'].fillna(method = 'ffill')


    #marks the entries
    dataframe['events_in'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), 'entry', '')
    
    if direction == 'long':
        if instrument == 1:
            dataframe['open_operations'] = (dataframe.close - dataframe.entry_price) * dataframe.number_of_stocks
            dataframe['open_operations'] = np.where((dataframe.mp == 1) & (dataframe.mp.shift(-1) == 0), ((dataframe.open.shift(-1) - dataframe.entry_price) * dataframe.number_of_stocks) - abs(((dataframe.open.shift(-1) - dataframe.entry_price) * dataframe.number_of_stocks) * .1), dataframe.open_operations)
    
    else:
        if instrument == 1:
            dataframe['open_operations'] = (dataframe.entry_price - dataframe.close) * dataframe.number_of_stocks
            dataframe['open_operations'] = np.where((dataframe.mp == 1) & (dataframe.mp.shift(-1) == 0), ((dataframe.entry_price - dataframe.open.shift(-1)) * dataframe.number_of_stocks) - abs(((dataframe.entry_price - dataframe.open.shift(-1)) * dataframe.number_of_stocks) * .1), dataframe.open_operations)

    dataframe['open_operations'] = np.where(dataframe.mp == 1, dataframe.open_operations, 0)
    dataframe['events_out'] = np.where((dataframe.mp == 0) & (dataframe.exit_rules == -1), 'exit', '')
    dataframe['operations'] = np.where((dataframe.exit_rules == -1) & (dataframe.mp == 1), dataframe.open_operations, np.nan)
    dataframe['closed_equity'] = dataframe.operations.fillna(0).cumsum()
    dataframe['open_equity'] = dataframe.closed_equity + dataframe.open_operations - dataframe.operations.fillna(0)

    dataframe.to_csv('trading_system.csv')

    return dataframe
    #premesso che è inutile ai fini della simulazione aggiungere tutto il profitto al budget, so potrebbe fare:
    #eliminando operations_money e basando l'acquisto delle azioni sull'equity, inizializzata al valore di budgett
    #dopo un operazione, si aggiunge o sottrae il suo valore all'equity. 

#ANALISYS TOOLS-------------------------------------------------------

def plot_equity(equity, color):
    """
    plots the equity line
    """
    import matplotlib.pyplot as plt

    plt.figure(figsize = (4,18), dpi = 300)
    plt.plot(equity, color)
    plt.xlabel('Time')
    plt.ylabel('Profit/Loss')
    plt.title('Equity line')
    plt.xticks(rotation = 'vertical')
    plt.grid(True)
    plt.show()

    return

def drawdown(equity):
    """
    calculates the drawdown
    """

    import pandas as pd

    maxvalue = equity.expanding(0).max()
    drawdown = equity - maxvalue
    drawdown_series = pd.Series(drawdown, index = equity.index)
    
    return drawdown_series

def plot_drawdown(equity):
    """
    plots the drawdown
    """

    import matplotlib.pyplot as plt

    dd = drawdown(equity)
    plt.plot(dd)
    plt.fill_between(dd.index, 0, dd)
    plt.xlabel('Time')
    plt.ylabel('Profit/Loss')
    plt.title('Drawdown')
    plt.grid(True)
    plt.show()

    return

def plot_double_equity(closed_equity, open_equity):
    """
    plots the two equity lines at the same time
    """

    import matplotlib.pyplot as plt

    plt.figure(figsize = (14, 8), dpi = 300)
    plt.plot(open_equity, color = 'red')
    plt.plot(closed_equity, color = 'green')
    plt.xlabel('timestamp')
    plt.ylabel('Profit/Loss')
    plt.title('Closed and Open Equity line')
    plt.xticks(rotation = 'vertical')
    plt.grid(True)
    plt.show()

    return

def delay_between_peaks(equity):
    """
    calculates the delay between a max and the next one
    """

    import pandas as pd
    import numpy as np

    df = pd.DataFrame(data = equity, index = equity.index)
    df['drawdown'] = drawdown(equity)
    df['delay_elements'] = df['drawdown'].apply(lambda x: 1 if x < 0 else 0)
    df['resets'] = np.where(df['drawdown'] == 0, 1, 0)
    df['cumsum'] = df['resets'].cumsum()
    
    return pd.Series(df['delay_elements'].groupby(df['cumsum']).cumsum())

def avg_delay_between_peaks(equity):
    """
    calculates the average delay between a max and the next one
    """

    import pandas as pd
    import numpy as np

    df = pd.DataFrame(data = equity, index = equity.index)
    df['drawdown'] = drawdown(equity)
    df['delay_elements'] = df['drawdown'].apply(lambda x: 1 if x < 0 else np.nan)
    df['resets'] = np.where(df['drawdown'] == 0, 1, 0)
    df['cumsum'] = df['resets'].cumsum()
    df.dropna(inplace = True)

    return round(df['delay_elements'].groupby(df['cumsum']).sum().mean(), 2)