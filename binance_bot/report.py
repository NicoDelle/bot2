class Report:

    def __init__(self, dataframe) -> None:

        try:
            dataframe.closed_equity.iloc[-1] / 1
        except:
            raise TypeError("DataFrame must have a closed_equity column with numerical values")
        
        self.profit = dataframe.closed_equity.iloc[-1]