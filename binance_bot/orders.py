"""
defines the diferent kinds of order
"""

def stop_order(db, direction):
    """
    define a stop order:
    a stop order is opened whenever a certain level is reached
    """
    #third-part imports
    #import pandas as pd

    #personal imports
    import specific_tools as st

    #builds enter and exit rules, depending on DIRECTION
    if direction == 'long':
        
        enter_rules = db.close > 0
        enter_level = db.hhv20.shift(1)
        exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

    else:

        enter_rules = db.close > 0
        enter_level = db.llv20.shift(1)
        exit_rules = st.crossover(db.close, db.hhv5.shift(1))
    
    return enter_rules, exit_rules, enter_level

#--------------------------------------------------------------------------

def trend_following_order(db, ema_short_period, ema_long_period, direction,):
    """
    define a market order in a trend following system
    """

    #third-party imports
    import pandas as pd
    
    #personal imports
    import specific_tools as st

    db['trend'] = st.long_or_short(db[f'EMA{ema_short_period}'], db[f'EMA{ema_long_period}'], direction, ema_long_period)
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

    return enter_rules, exit_rules

#--------------------------------------------------------------------------

def market_order(db, direction):
    """
    define a market order. A market order is applied when some arbitrary but determined
    rules verify
    """

    #personal imports
    import specific_tools as st
    
    #builds enter and exit rules, depending on DIRECTION
    if direction == 'long':
        
        enter_rules = st.crossover(db.close, db.hhv20.shift(1))
        exit_rules = st.crossunder(db.close, db.llv5.shift(1))  

    else:

        enter_rules = st.crossunder(db.close, db.llv20.shift(1))
        exit_rules = st.crossover(db.close, db.hhv5.shift(1))

    return enter_rules, exit_rules