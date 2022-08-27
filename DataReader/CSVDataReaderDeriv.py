import csv
import logging
import sys
from typing import List

import pandas as pd

from DataReader.DataReaderBase import DataReader


class CSVDataReader(DataReader):

    # Xcolumn: indice a columna con datos para el eje X
    # Ycolumn: indice o lista de indices a las columnas dependientes
    def __init__(self, filepath: str, separator: str = ','):
        super().__init__()
        self.path2data = filepath
        self.separator = separator
        self.xcolumn = None
        self.ycolumn = None
        self.xoperation = None
        self.yoperation = None
        self.xunits = None
        self.yunits = None
        self.data2get: str = "Signal"
        self.fields: List[str] = []

    '''
    Data reading method. Acces the file and returns the solicited data which indexes where
    passed to the Construcctor
    DataFrame: Array bidimensional ordenado por inidices multitipo. Ej:
               x    y  y2
        0  1.256  1.3   1
        1  1.580  5.0   2
        2  1.630  6.0   3
        3  2.000  9.0   4
        4  3.000  7.0   5
    '''

    def read(self) -> pd.DataFrame:

        try:
            resultDF = pd.read_csv(self.path2data, engine='python', skiprows=[1], header=0,
                                   usecols=[self.xcolumn, self.ycolumn], sep=self.separator)
            resultDF[self.xcolumn] = resultDF[self.xcolumn].apply(self.xoperation)
            resultDF[self.ycolumn] = resultDF[self.ycolumn].apply(self.yoperation)
            return resultDF

        except Exception:
            types, value, traceback = sys.exc_info()
            logging.error("Problema en la lectura del CSV:" + value.strerror)

        return pd.DataFrame()

    def get_traces_names(self) -> List[str]:

        if not len(self.fields):
            csvreader = csv.reader(open(self.path2data, 'r'))
            self.fields = next(csvreader)

        return self.fields

    def get_selected_traces(self) -> List[str]:
        return [self.xcolumn, self.ycolumn]

    def config(self, data2get: str, xtrace: str, ytrace: str, xop, yop):
        self.data2get = data2get
        self.xcolumn = xtrace
        self.ycolumn = ytrace
        self.xoperation = xop
        self.yoperation = yop


if __name__ == "__main__":
    reader = CSVDataReader("/home/gullino18/PycharmProjects/TC-GrupoX/TP1/ParteLabo/Parte-A/Scope_A.csv")

    reader.config("Signal", "x-axis", "1", lambda x: x, lambda x: x)
    print(reader.read())
