#third-party imports
import numpy as np
import matplotlib.pyplot as plt

#personal imports
import specific_tools as st

class Report:
    """
    define report class
    """
    def __init__(self, dataframe, symbol, interval) -> None:
        """
        Report constructor:
            - It takes as arguments a dataframe with a closed_equity, an open_equity and an operations 
              column, filled with numerical values, the symbol we're trading and the interval
            - profit property: the final profit of the given trading system
            - operations property: a list of tuples with gain or loss as first element,
              and date as second element
            - avg_trade property: Average trade of the given trading system
            - max_dd and avg_dd attribute: Max and average drawdown
            - max and avg loss attributes: MAx and average loss. max_loss is a tuple,
              where the first element is the loss and the seond is the date it occourred
            - max and average gain attributes: works like avg and max loss
            - check thavg_delay = st.avg_delay_between_peaks(df['open_equity'])e suggestions for other attributes
        """

        try:
            dataframe.closed_equity.iloc[-1] / 1
        except:
            raise TypeError("DataFrame must have a closed_equity column with numerical values")
        try:
            dataframe.open_equity.iloc[-1] / 1
        except:
            raise TypeError("Dataframe must have open_equity column with numerical values")        
        try:
            dataframe.operations.dropna().iloc[0] / 1
        except:
            raise TypeError("Dataframe must have operations column with numerical values")
        
        self._profit = dataframe.closed_equity.iloc[-1]
        
        self._operations = []
        n = 0
        for operation in dataframe.operations.dropna():
            self._operations.append((operation, dataframe.operations.dropna().index[n]))
            n += 1
        
        self._avg_trade = round(dataframe.operations.dropna().mean(), 2)

        self.symbol = symbol
        self.interval = interval

        self.max_dd = round(st.drawdown(dataframe.open_equity).min(), 2)
        self.avg_dd = round(
            st.drawdown(dataframe.open_equity[dataframe.open_equity < 0]).mean(), 2
            )

        self.avg_loss = round(dataframe.operations[dataframe.operations < 0].mean(), 2)
        self.max_loss = (
            round(dataframe.operations.min(), 2), 
            dataframe['operations'].idxmin()
            )

        self.avg_gain = round(dataframe.operations[dataframe.operations > 0].mean(), 2)
        self.max_gain = (
            round(dataframe.operations.max(), 2), dataframe['operations'].idxmax()
            )

        self.gross_profit = round(dataframe.operations[dataframe.operations > 0].sum(), 2)
        self.gross_loss = round(dataframe.operations[dataframe.operations <= 0].sum(), 2)

        if self.gross_loss != 0:
            self.pf = round(abs(self.gross_profit / self.gross_loss), 2)
        else:
            self.pf = round(abs(self.gross_profit / 0.0000000000001), 2)

        self.percent_win = round(
            (dataframe.operations[dataframe.operations > 0].count() \
                / dataframe.operations.count()) * 100, 
            2
            )

        if self.avg_loss != 0:
            self.RR_ratio = round(self.avg_gain / abs(self.avg_loss), 2)
        else:
            self.RR_ratio = 'infinito'

        self.max_delay = st.delay_between_peaks(dataframe['open_equity']).max()
        self.avg_delay = st.avg_delay_between_peaks(dataframe['open_equity'])
    
    @property
    def profit(self) -> float:
        """
        Define profit property
        """
        return self._profit
    
    @property
    def operations(self):
        """
        Define operations property
        """
        return self._operations
    
    @property
    def avg_trade(self):
        """
        Define average trade property
        """
        return self._avg_trade
    
    def __repr__(self) -> str:
        return(f"""
Report {self.interval}-{self.symbol}:

    - Profit: {self.profit}€
    - Average trade: {self.avg_trade}€
    - Max and average DRAWDOWN: {self.max_dd}€, {self.avg_dd}€
    - Max, average and gross LOSS: {self.max_loss[0]}€ on {self.max_loss[1]}, {self.avg_loss}€, {self.gross_loss}€
    - Max, average and gross GAIN: {self.max_gain[0]}€ on {self.max_gain[1]}, {self.avg_gain}€, {self.gross_profit}€
    - Percent Win: {self.percent_win}%
    - Profit factor: {self.pf}
    - Risk/Reward ratio: {self.RR_ratio}
    - Max and average DELAY between peaks: {self.max_delay} bars, {self.avg_delay} bars
""")
