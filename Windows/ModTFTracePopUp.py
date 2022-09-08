import sys

import sympy as sp
from PyQt6 import QtGui, QtWidgets

from DataReader.TFDataReaderDeriv import TFDataReader, multipliers_dict
from Utils.MPLTexTextClass import MPLTexText
from Utils.Trace import linestyle_dict, markers_dict
from typing import Tuple
from UI import UI_ModTFTracePopUp

alphabet = "abcdfghjklmnoqrtuvwxyz"


class ModTFTracePopUp(QtWidgets.QDialog, UI_ModTFTracePopUp.Ui_ModTFTracePopUp):
    def __init__(self, name, color, marker, linetype, reader):
        super().__init__()

        self.lastText = reader.strexpr
        self.checked = True
        self.reader = reader
        self.setupUi(self)
        self.StartFreqMultCB.addItems(multipliers_dict.keys())
        self.StopFreqMultCB.addItems(multipliers_dict.keys())
        self.StartFreqMultCB.setCurrentText('Hz')
        self.StopFreqMultCB.setCurrentText('Hz')
        self.StartDSB.setValue(self.reader.startFreq)
        self.StopDSB.setValue(self.reader.stopFreq)
        self.TraceTypeCB.addItems(linestyle_dict.keys())
        self.TraceTypeCB.setCurrentText(linetype)
        self.MarkersCB.addItems(markers_dict.keys())
        self.MarkersCB.setCurrentText(marker)
        self.TraceNameLE.setText(name)
        self.TFLineEdit.setText(self.lastText)
        self.TexBox = MPLTexText(self.TFViewer)
        self.TexBox.updateTex(f'${sp.latex(self.reader.getExpression())}$')
        self.color = QtGui.QColor(color)
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)

        self.data = ("", "", "")

    def exec(self) -> Tuple[str, str, str]:
        super().exec()
        return self.data

    def accept(self) -> None:
        if not self.checked:
            QtWidgets.QMessageBox.warning(self, "Advertencia", f"Por favor darle al boton Check")
            return
        self.reader.setMaxMinRange(self.StartDSB.value()*multipliers_dict[self.StartFreqMultCB.currentText()],
                                   self.StopDSB.value()*multipliers_dict[self.StopFreqMultCB.currentText()])
        self.data = (self.TraceNameLE.text(), self.color.name(), self.TraceTypeCB.currentText(),
                     self.MarkersCB.currentText(), self.reader)
        self.done(0)
        pass

    def reject(self) -> None:
        self.done(0)
        pass

    def ChooseColor(self):
        self.color = QtWidgets.QColorDialog.getColor(self.color)
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)

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
            QtWidgets.QMessageBox.warning(self, "Advertencia", f"Problema al parsear la funcion. \n {values}")

    def textChange(self, text: str):
        self.checked = False
        for letter in text.lower():
            if letter in alphabet:
                self.TFLineEdit.setText(self.lastText)
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