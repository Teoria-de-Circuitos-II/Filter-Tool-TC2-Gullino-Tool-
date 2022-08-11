from typing import Union, Tuple

import pandas as pd
from PyQt6 import QtGui, QtWidgets
from Utils.Trace import linestyle_dict, Trace, TraceType
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, T
from UI import UI_AddTracePopUp
from DataReader.CSVDataReaderDeriv import CSVDataReader
from DataReader.SpiceDataReaderDeriv import SpiceDataReader

permited_file_types = "RAW Spice file (*.raw);;" \
                      "CSV File (*.csv)"


class AddTracePopUp(QtWidgets.QDialog, UI_AddTracePopUp.Ui_AddTracePopUp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.TraceTypeCB.addItems(linestyle_dict.keys())
        self.MonteCarloGroupBox.setVisible(False)
        self.SignalGroupBox.setVisible(False)
        self.color = QtGui.QColor("#FF8C00")
        self.reader: Union[CSVDataReader, SpiceDataReader] = None
        self.tracesnames = None
        self.traces: Union[Trace, Tuple[Trace, Trace]] = None

    def exec(self) -> Union[Trace, Tuple[Trace, Trace]]:
        super().exec()
        return self.traces

    def accept(self) -> None:

        if self.Dir2FileLE.text() == '':
            QtWidgets.QMessageBox.warning(self, "Advertencia",
                                          f"Elegi el archivo o te encripto todos los datos.")
            return

        if self.BodeRadioButton.isChecked():
            if not len(self.FreqOpLE.text()):
                freqop = getLambdaFromOperation("x")
            else:
                freqop = getLambdaFromOperation(self.XOpLE.text())

            if not len(self.ModOpLE.text()):
                modop = getLambdaFromOperation("x")
            else:
                modop = getLambdaFromOperation(self.YOpLE.text())

            if not len(self.PhaseOpLE.text()):
                phaseop = getLambdaFromOperation("x")
            else:
                phaseop = getLambdaFromOperation(self.YOpLE.text())

            match self.reader:
                case CSVDataReader():
                    phasereader = CSVDataReader(self.Dir2FileLE.text())
                    self.reader.config("Mod", self.FreqDataCB.currentText(), self.ModDataCB.currentText(),
                                       freqop, modop)
                    phasereader.config("Phase", self.FreqDataCB.currentText(), self.PhaseDataCB.currentText(),
                                       freqop, phaseop)

                case SpiceDataReader():
                    if self.IsMCCheckBox.isChecked():
                        self.reader = SpiceDataReader(self.Dir2FileLE.text(), isMonteCarlo=True)
                        phasereader = SpiceDataReader(self.Dir2FileLE.text(), isMonteCarlo=True)
                        self.reader.config("Mod", self.FreqDataCB.currentText(), self.ModDataCB.currentText(),
                                           freqop, modop, self.StepQuantSpinBox.value())
                        phasereader.config("Phase", self.FreqDataCB.currentText(), self.PhaseDataCB.currentText(),
                                           freqop, phaseop, self.StepQuantSpinBox.value())
                    else:
                        phasereader = SpiceDataReader(self.Dir2FileLE.text())
                        self.reader.config("Mod", self.FreqDataCB.currentText(), self.ModDataCB.currentText(),
                                           freqop, modop)
                        phasereader.config("Phase", self.FreqDataCB.currentText(), self.PhaseDataCB.currentText(),
                                           freqop, phaseop)

            modtrace = Trace(self.TraceNameLE.text(), self.reader, self.color.name(),
                             linestyle_dict[self.TraceTypeCB.currentText()], TraceType.Module)

            if phasereader is None:
                phasereader = self.reader

            phasetrace = Trace(self.TraceNameLE.text(), phasereader, self.color.name(),
                               linestyle_dict[self.TraceTypeCB.currentText()], TraceType.Phase)

            self.traces = (modtrace, phasetrace)

        else:
            if not len(self.XOpLE.text()):
                xop = getLambdaFromOperation("x")
            else:
                xop = getLambdaFromOperation(self.XOpLE.text())

            if not len(self.YOpLE.text()):
                yop = getLambdaFromOperation("x")
            else:
                yop = getLambdaFromOperation(self.YOpLE.text())

            match self.reader:
                case CSVDataReader():
                    self.reader.config("Signal", self.XDataCB.currentText(), self.YDataCB.currentText(),
                                       xop, yop)

                case SpiceDataReader():
                    if self.IsMCCheckBox.isChecked():
                        self.reader = SpiceDataReader(self.Dir2FileLE.text(), isMonteCarlo=True)
                        self.reader.config("Signal", self.XDataCB.currentText(), self.YDataCB.currentText(),
                                           xop, yop, self.StepQuantSpinBox.value())
                    else:
                        self.reader.config("Signal", self.XDataCB.currentText(), self.YDataCB.currentText(),
                                           xop, yop)
            self.traces = Trace(self.TraceNameLE.text(), self.reader, self.color.name(),
                                linestyle_dict[self.TraceTypeCB.currentText()], TraceType.Signal)
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

    def BrowseFile(self):
        path2file = QtWidgets.QFileDialog.getOpenFileName(filter=permited_file_types)
        if path2file[0] == '':
            return
        self.Dir2FileLE.setText(path2file[0])
        if "csv" in path2file[1]:
            self.reader = CSVDataReader(path2file[0])
        elif "raw" in path2file[1]:
            self.reader = SpiceDataReader(path2file[0])

        self.tracesnames = self.reader.get_traces_names()
        self.XDataCB.clear()
        self.YDataCB.clear()
        self.FreqDataCB.clear()
        self.ModDataCB.clear()
        self.PhaseDataCB.clear()
        self.XDataCB.addItems(self.tracesnames)
        self.YDataCB.addItems(self.tracesnames)
        self.FreqDataCB.addItems(self.tracesnames)
        self.ModDataCB.addItems(self.tracesnames)
        self.PhaseDataCB.addItems(self.tracesnames)


def getLambdaFromOperation(strexpr: str):
    strexpr = correctExpression(strexpr)
    # Se Toma la expresion ingresada por el usuario, se corrije y se interpreta
    expr = parse_expr(strexpr, transformations=T[:])
    variable = expr.free_symbols

    # Transformamos la expresion en un funcion Lambda para poder utilizarla
    lambdaexpr = sp.lambdify(list(variable), expr, "numpy")

    return lambdaexpr


# Fucnion para corregir expresiones de las entradas de funciones en texto
def correctExpression(expr: str):
    validfuncs = sp.functions.__all__
    exprlower = expr.lower()
    correctedexpr = expr
    for funct in validfuncs:
        if funct.lower() + '(' in exprlower:
            correctedexpr = exprlower.replace(funct.lower(), funct)
    return correctedexpr


if __name__ == "__main__":
    import sys
    import matplotlib.pyplot as plt

    app = QtWidgets.QApplication(sys.argv)
    AddTracePopUpxd = AddTracePopUp()
    mod, fase = AddTracePopUpxd.exec()
    moduledata: pd.DataFrame = mod.reader.read()
    plt.semilogx(moduledata.iloc[:, 0], moduledata.iloc[:, 1])
    plt.show()
    AddTracePopUpxd.close()
    sys.exit()
