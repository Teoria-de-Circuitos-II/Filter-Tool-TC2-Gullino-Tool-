import sys
import logging
from typing import Tuple
from PyQt6 import QtWidgets, QtGui
from Utils.MPLTexTextClass import MPLTexText
import sympy as sp
from DataReader.TFDataReaderDeriv import TFDataReader, multipliers_dict
from Utils.Trace import Trace, linestyle_dict, TraceType, markers_dict
from UI import UI_LoadTransferFunctionPopUp
import matplotlib
import matplotlib.scale
import matplotlib.pyplot as plt

alphabet = "abcdfghjklmnoqrtuvwxyz"


class LoadTransferFunctionPopUp(QtWidgets.QDialog, UI_LoadTransferFunctionPopUp.Ui_LoadTransferFunctionPopUp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.StartFreqMultCB.addItems(multipliers_dict.keys())
        self.StopFreqMultCB.addItems(multipliers_dict.keys())
        self.StartFreqMultCB.setCurrentText('Hz')
        self.StopFreqMultCB.setCurrentText('MHz')
        self.StartDSB.setValue(10)
        self.StopDSB.setValue(1)
        self.color = QtGui.QColor("#FF8C00")
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)
        self.LineTypeCB.addItems(linestyle_dict.keys())
        self.lastText = ''
        self.checked = False
        self.TexBox = MPLTexText(self.TexGroupBox)
        self.reader: TFDataReader = None
        self.traces: Tuple[Trace, Trace] = (None, None)

    def exec(self) -> Tuple[Trace, Trace]:
        super().exec()
        return self.traces

    def accept(self) -> None:
        if not self.checked:
            QtWidgets.QMessageBox.warning(self, "Advertencia", f"Por favor darle al boton Check")
            return
        try:
            ModReader = TFDataReader(self.lastText)
            PhaseReader = TFDataReader(self.lastText)
            ModReader.initTransferFunction('Mod')
            PhaseReader.initTransferFunction('Phase')
            ModReader.setMaxMinRange(self.StartDSB.value()*multipliers_dict[self.StartFreqMultCB.currentText()],
                                     self.StopDSB.value()*multipliers_dict[self.StopFreqMultCB.currentText()])
            PhaseReader.setMaxMinRange(self.StartDSB.value()*multipliers_dict[self.StartFreqMultCB.currentText()],
                                       self.StopDSB.value()*multipliers_dict[self.StopFreqMultCB.currentText()])
            self.traces = (Trace(self.TraceNameLE.text(), ModReader, self.color.name(),
                                 self.LineTypeCB.currentText(), 'nothing', TraceType.Module),
                           Trace(self.TraceNameLE.text(), PhaseReader, self.color.name(),
                                 self.LineTypeCB.currentText(), 'nothing', TraceType.Phase))
        except:
            QtWidgets.QMessageBox.critical(self, "Error", f"Hubo un problema al intentar generar la curva.")
            self.traces = None
        self.done(0)
        pass

    def reject(self) -> None:
        self.done(0)
        pass

    def updateTransferFunction(self):
        try:
            self.reader = TFDataReader(self.lastText)
            expr = self.reader.getExpression()
            latexExpr = f"${sp.latex(expr)}$"
            if len(latexExpr) > 0:
                self.TexBox.updateTex(latexExpr)

            self.checked = True
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.warning(self, "Advertencia", f"Problema al parsear la funcion. \n {values}")

    def textChange(self, text: str):
        self.checked = False
        for letter in text.lower():
            if letter in alphabet:
                self.TransferFunctionLineEdit.setText(self.lastText)
                return
        self.lastText = text

        try:
            self.reader = TFDataReader(self.lastText)
            expr = self.reader.getExpression()
            latexExpr = f"${sp.latex(expr)}$"
            if len(latexExpr) > 0:
                self.TexBox.updateTex(latexExpr)
        except:
            pass

    def ChooseColor(self):
        self.color = QtWidgets.QColorDialog.getColor(self.color)
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    app = QtWidgets.QApplication(sys.argv)
    popUp = LoadTransferFunctionPopUp()
    transferFunc = popUp.exec()
    plt.show()
    popUp.close()
    sys.exit()
