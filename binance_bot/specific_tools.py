"""
specific tools for algorithmical trading
"""

from logging import raiseExceptions
from numpy import array

from sqlalchemy import true


def hhv20(prices):
    """
    selects the max value in a timeframe of 20 periods    import pandas as pd

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

def ema(prices, period):
    """
    calculates the exponential moving average in a given timeframe. 
    le posizioni fuori dal periodo sono inizializzate a nan
    """

    import pandas as pd
    import numpy as np

    smoother = 2 / (period + 1)

    if len(prices) > period:
        
        ema = pd.Series(np.zeros(len(prices)))
        ema.iloc[period] = prices[:period].sum() / period

        for n in range(period + 1, len(ema)):

            close = prices.iloc[n]
            ema[n] = close * smoother + ema.iloc[n - 1] * (1 - smoother)

        ema.index = prices.index

        return(ema)
    
    else:

        raise ValueError(f'period was longer than data (length data: {len(prices)})')

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

def stop_check(data, rules, level, direction):
    """
    validates the rules with a stop setup
    """

    import pandas as pd
    import numpy as np

    df = pd.DataFrame(index = data.index)
    df['rules'] = rules
    df['level'] = level
    df['low'] = data.low
    df['high'] = data.high

    if direction == 'long':
        df['new_rules'] = np.where((df.rules == True) & (df.high.shift(-1) >= df.level.shift(-1)), True, False)
    
    if direction == 'short':
        df['new_rules'] = np.where((df.rules == True) & (df.low.shift(-1) <= df.level.shift(-1)), True, False)
    
    return df.new_rules

def limit_check(data, rules, level, direction):
    """
    validates a limit setup with rules
    """

    import pandas as pd
    import numpy as np

    df = pd.DataFrame()
    df['rules'] = rules
    df['level'] = level
    df['low'] = data.low
    df['high'] = data.high

    if direction == 'long':
        df['new_rules'] = np.where((df.rules == True) & (df.low.shift(-1) <= df.level.shift(-1)), True, False)
    
    if direction == 'short':
        df['new_rules'] = np.where((df.rules == True) & (df.high.shift(-1) >= df.level.shift(-1)))

    return df.new_rules

def tick_correction_up(level, tick):
    """
    corrects the price upward
    """

    import math

    if level != level:
        level = 0
    multiplier = math.ceil(level/tick)

    return multiplier * tick

def tick_correction_down(level, tick):
    """
    corrects the price downward
    """

    import math

    if level != level:
        level = 0
    multiplier = math.floor(level/tick)
    
    return multiplier * tick

#-------------------------------------------------------
def long_or_short(short_ema, long_ema, direction, long_period):
    """
    to analyse trends
    """

    import numpy as np
    import pandas as pd

    #1 if the actual trend is bullish, -1 if it's bearish
    position = np.where(short_ema > long_ema, 1, -1)

    if direction == 'long':
        
        position = pd.Series(position)
        position[:long_period].apply(lambda x: 1)
        position.index = long_ema.index
        
        return position
    
    else:
        
        position = pd.Series(position)
        position[:long_period].apply(lambda x: -1)
        position.index = long_ema.index

        return position    

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

def apply_trading_system(dataframe, instrument, direction, order_type, operation_money, enter_rules, exit_rules, tick, *args):
    
    """
    core of the trading system
    """

    import numpy as np

    dataframe = dataframe.copy()

    if order_type == 'stop':
        enter_level = args[0]
        enter_rules = stop_check(dataframe, enter_rules, enter_level, direction)
        dataframe['enter_level'] = enter_level

    if order_type == 'limit':
        enter_level = args[0]
        enter_rules == limit_check(dataframe, enter_rules, enter_level, direction)
        dataframe['enter_level'] = enter_level
    

    dataframe['enter_rules'] = enter_rules.apply(lambda x: 1 if x == True else 0)
    dataframe['exit_rules'] = exit_rules.apply(lambda x: -1 if x == True else 0)
    dataframe['mp'] = marketposition_generator(dataframe.enter_rules, dataframe.exit_rules)

    #marks entry price
    if order_type == 'market':
        dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), dataframe.open, np.nan)
    
    #marks the number of stocks
        if instrument == 1:
            dataframe['number_of_stocks'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), operation_money / dataframe.entry_price, np.nan)
    
    if order_type == 'stop':
        
        #corrects the price end checks wether the stop conditions are respected or not
        if direction == 'long':
            dataframe.enter_level = dataframe.enter_level.apply(lambda x: tick_correction_up(x, tick))
            real_entry = np.where(dataframe.open > dataframe.enter_level, dataframe.open, dataframe.enter_level)
            dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), real_entry, np.nan)

        if direction == 'short':
            dataframe.enter_level = dataframe.enter_level.apply(lambda x: tick_correction_down(x, tick))
            real_entry = np.where(dataframe.open < dataframe.enter_level, dataframe.open, dataframe.enter_level)
            dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), real_entry, np.nan)

        if instrument == 1:
            dataframe['number_of_stocks'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1) & (real_entry), operation_money / real_entry, np.nan)
    
    if order_type == 'limit':
        
        if direction == 'long':
            dataframe.enter_level = dataframe.enter_level.apply(lambda x: tick_correction_up(x, tick))
            real_entry = np.where(dataframe.open < dataframe.enter_level, dataframe.open, dataframe.enter_level)
            dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), real_entry, np.nan)

        if direction == 'short':
            dataframe.enter_level = dataframe.enter_level.apply(lambda x: tick_correction_up(x, tick))
            real_entry = np.where(dataframe.open > dataframe.enter_level, dataframe.open, dataframe.enter_level)
            dataframe['entry_price'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1) & (real_entry != 0), real_entry, np.nan)

        if instrument == 1:
            dataframe['number_of_stocks'] = np.where((dataframe.mp.shift(1) == 0) & (dataframe.mp == 1), operation_money / real_entry, np.nan)
    
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
    dataframe['events_out'] = np.where((dataframe.mp == 1) & (dataframe.exit_rules == -1), 'exit', '')
    dataframe['operations'] = np.where((dataframe.exit_rules == -1) & (dataframe.mp == 1), round(dataframe.open_operations, 2), np.nan)
    dataframe['closed_equity'] = round(dataframe.operations.fillna(0).cumsum(), 3)
    dataframe['open_equity'] = round(dataframe.closed_equity + dataframe.open_operations - dataframe.operations.fillna(0), 3)

    dataframe.to_csv('trading_system.csv')

    return dataframe

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

def plot_multiple(title, *lines):
    """
    plots the two equity lines at the same time
    """

    import matplotlib.pyplot as plt

    plt.figure(figsize = (14, 8), dpi = 300)

    for line in lines:
        plt.plot(line)

    plt.xlabel('timestamp')
    plt.title(title)
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