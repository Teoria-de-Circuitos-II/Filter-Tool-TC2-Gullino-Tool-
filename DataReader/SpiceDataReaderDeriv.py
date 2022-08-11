import logging
import logging.config
from typing import List

import matplotlib.pyplot as plt
import numpy as np
from PyLTSpice.LTSpice_RawRead import RawRead
from pandas import DataFrame

from DataReader.DataReaderBase import DataReader


class SpiceDataReader(DataReader):
    logger: logging.Logger

    def __init__(self, filepath: str, isMonteCarlo: bool = False):
        super().__init__()
        self.logger = logging.getLogger('root')
        self.path2data = filepath
        self.isMC = isMonteCarlo
        self.step2read = 10
        self.xcolumn = ""
        self.ycolumn = ""
        self.xoperation = None
        self.yoperation = None
        self.data2get: str = "Signal"
        self.RawData = RawRead(filepath)

    def config(self, data2get: str, xtrace: str, ytrace: str, xop, yop, stepQuant: int = 10):
        self.data2get = data2get
        self.xcolumn = xtrace
        self.ycolumn = ytrace
        self.xoperation = xop
        self.yoperation = yop
        self.step2read = stepQuant

    def get_traces_names(self) -> List[str]:
        return self.RawData.get_trace_names()

    def get_selected_traces(self) -> List[str]:
        return [self.xcolumn, self.ycolumn]

    def get_steps(self) -> List[int]:
        return self.RawData.get_steps()

    def isMonteCarlo(self):
        return self.isMC

    def read(self) -> DataFrame:

        self.logger.debug("Reading trace " + self.ycolumn)

        if self.isMC:
            match self.data2get:
                case "Mod":
                    frequ = self.RawData.get_trace(self.xcolumn).get_wave(0)
                    dictData = {self.xcolumn: np.real(frequ)}
                    for i in range(self.step2read):
                        dictData[self.ycolumn + " step %d" % i] = self.yoperation((np.abs(
                            self.RawData.get_trace(self.ycolumn).get_wave(i))))
                case "Phase":
                    frequ = self.RawData.get_trace(self.xcolumn).get_wave(0)
                    dictData = {self.xcolumn: np.real(frequ)}
                    for i in range(self.step2read):
                        dictData[self.ycolumn + " step %d" % i] = self.yoperation(np.angle(
                            self.RawData.get_trace(self.ycolumn).get_wave(i)))
                case "Signal":
                    time = np.abs(self.RawData.get_trace(self.xcolumn).get_wave(0))
                    dictData = {self.xcolumn: self.xoperation(time)}
                    for i in range(self.step2read):
                        dictData[self.ycolumn + " step %d" % i] = self.yoperation(
                            self.RawData.get_trace(self.ycolumn).get_wave(i))

            resultDF = DataFrame(dictData)

        else:
            match self.data2get:
                case "Mod":
                    frequ = self.RawData.get_trace('frequency').get_wave()
                    dictData = {'Frequency': self.xoperation(np.real(frequ)), self.ycolumn: self.yoperation((np.abs(
                        self.RawData.get_trace(self.ycolumn).get_wave())))}
                case "Phase":
                    frequ = self.RawData.get_trace('frequency').get_wave()
                    dictData = {'Frequency': self.xoperation(np.real(frequ)), self.ycolumn: self.yoperation(np.angle(
                        self.RawData.get_trace(self.ycolumn).get_wave()))}
                case "Signal":
                    time = self.RawData.get_trace('time').get_wave()
                    dictData = {'Time': np.abs(self.xoperation(time)),
                                self.ycolumn: self.yoperation(self.RawData.get_trace(self.ycolumn).get_wave())}

            resultDF = DataFrame(dictData)

        self.logger.debug(resultDF)
        return resultDF


if __name__ == "__main__":
    # logging.config.fileConfig("logging.ini")

    LTR = SpiceDataReader("./TestData/Test.raw")  # Reads the RAW file contents from file
    print(LTR.get_traces_names())
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex='all')

    LTR.config(['V(n002)'])

    data = LTR.read()

    print(data)

    ax1.semilogx(data['Frequency'], np.abs(data['V(n002) step 0']))
    ax2.semilogx(data['Frequency'], np.angle(data['V(n002) step 0']))

    plt.show()
