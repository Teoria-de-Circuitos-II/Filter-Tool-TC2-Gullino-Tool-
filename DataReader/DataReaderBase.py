from abc import abstractmethod


class DataReader:

    def __init__(self):
        pass

    @abstractmethod
    def read(self):
        pass
