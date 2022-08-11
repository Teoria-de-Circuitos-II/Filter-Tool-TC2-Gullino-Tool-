from pandas import DataFrame


class DataReader:

    def __init__(self):
        self.data: DataFrame = None
        pass

    def read(self):
        return self.data

    def setData(self, x, y):
        self.data = DataFrame.from_dict({'X': x, 'Y': y})