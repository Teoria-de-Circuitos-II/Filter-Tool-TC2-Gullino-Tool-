import logging
from typing import Tuple

from PyQt6 import QtWidgets

from DataReader.TFDataReaderDeriv import TFDataReader
from Utils.Trace import Trace
from UI import UI_LoadTransferFunctionPopUp
import sympy as sp


class LoadTransferFunctionPopUp(QtWidgets.QDialog, UI_LoadTransferFunctionPopUp.Ui_LoadTransferFunctionPopUp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.reader: TFDataReader = None
        self.traces: Tuple[Trace, Trace] = None

    def exec(self) -> Tuple[Trace, Trace]:
        super().exec()
        return self.traces

    def accept(self) -> None:

        #TFDataReader(tranfFunc)
        self.done(0)
        pass

    def reject(self) -> None:
        self.done(0)
        pass

    def updateTransferFunction(self):
        self.reader = TFDataReader(self.TransferFunctionTextBox.toPlainText())
        expr = self.reader.getExpression()
        latexExpr = sp.latex(expr)
        logging.debug(latexExpr)
        sp.preview(latexExpr, output='png', viewer='gimp')

if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    app = QtWidgets.QApplication(sys.argv)
    popUp = LoadTransferFunctionPopUp()
    transferFunc = popUp.exec()
    plt.show()
    popUp.close()
    sys.exit()
