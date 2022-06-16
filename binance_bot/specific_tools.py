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