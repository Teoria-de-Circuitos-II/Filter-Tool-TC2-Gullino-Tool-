from typing import Union, Tuple, List

import pandas as pd
from PyQt6 import QtGui, QtWidgets, QtCore
from Utils.Trace import markers_dict, linestyle_dict, Trace, TraceType
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr, T
from UI import UI_AddTracePopUp
from DataReader.CSVDataReaderDeriv import CSVDataReader
from DataReader.SpiceDataReaderDeriv import SpiceDataReader

permited_file_types = "RAW Spice file (*.raw);;" \
                      "CSV File (*.csv)"


class YAxisDataWidget:
    def __init__(self, parent: QtWidgets, CBdata: List[str], row: int = 0, column: int = 0, rowspan: int = 1,
                 columnspan: int = 1):
        self.color = QtGui.QColor("#FF8C00")
        self.GroupBox = QtWidgets.QGroupBox()
        self.GroupBox.setSizePolicy(QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Preferred,
                                                          QtWidgets.QSizePolicy.Policy.Maximum))
        self.GriLayout: QtWidgets.QGridLayout = QtWidgets.QGridLayout()
        self.GroupBox.setLayout(self.GriLayout)
        self.YDataLabel = QtWidgets.QLabel("Eje Y:", self.GroupBox)
        self.YDataCB = QtWidgets.QComboBox(self.GroupBox)
        self.YDataCB.addItems(CBdata)
        self.YOpLabel = QtWidgets.QLabel("Operacion:", self.GroupBox)
        self.YOpLE = QtWidgets.QLineEdit(self.GroupBox)
        self.TraceNameLabel = QtWidgets.QLabel("Nombre:", self.GroupBox)
        self.TraceNameLE = QtWidgets.QLineEdit(self.GroupBox)
        self.TraceColorLabel = QtWidgets.QLabel("Color:", self.GroupBox)
        self.TraceColorButton = QtWidgets.QPushButton(self.GroupBox)
        self.TraceColorButton.setMinimumSize(QtCore.QSize(30, 30))
        self.TraceColorButton.setMaximumSize(QtCore.QSize(30, 30))
        self.TraceColorButton.setText("")
        self.TraceLineTypeLabel = QtWidgets.QLabel("Tipo de Linea:", self.GroupBox)
        self.TraceLineTypeCB = QtWidgets.QComboBox(self.GroupBox)
        self.TraceLineTypeCB.addItems(linestyle_dict.keys())
        self.TraceMarkerLabel = QtWidgets.QLabel("Marcador:", self.GroupBox)
        self.TraceMarkerCB = QtWidgets.QComboBox(self.GroupBox)
        self.TraceMarkerCB.addItems(markers_dict.keys())
        self.TraceMarkerCB.setCurrentText('nothing')

        self.GriLayout.addWidget(self.YDataLabel, 0, 0)
        self.GriLayout.addWidget(self.YDataCB, 0, 1)
        self.GriLayout.addWidget(self.YOpLabel, 0, 2)
        self.GriLayout.addWidget(self.YOpLE, 0, 3, 1, 3)
        self.GriLayout.addWidget(self.TraceNameLabel, 1, 0)
        self.GriLayout.addWidget(self.TraceNameLE, 1, 1)
        self.GriLayout.addWidget(self.TraceColorLabel, 1, 2)
        self.GriLayout.addWidget(self.TraceColorButton, 1, 3)
        self.GriLayout.addWidget(self.TraceLineTypeLabel, 2, 0)
        self.GriLayout.addWidget(self.TraceLineTypeCB, 2, 1)
        self.GriLayout.addWidget(self.TraceMarkerLabel, 2, 2)
        self.GriLayout.addWidget(self.TraceMarkerCB, 2, 3)

        self.TraceColorButton.clicked.connect(lambda: YAxisDataWidget.ChooseColor(self))
        palette = self.TraceColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.TraceColorButton.setPalette(palette)
        parent.layout().addWidget(self.GroupBox, row, column, rowspan, columnspan)

    def getData(self):
        if not len(self.YOpLE.text()):
            yop = getLambdaFromOperation("x")
        else:
            yop = getLambdaFromOperation(self.YOpLE.text())
        return self.YDataCB.currentText(), self.TraceNameLE.text(), self.color.name(), \
               self.TraceLineTypeCB.currentText(), yop, self.TraceMarkerCB.currentText()

    def updateOptions(self, CBdata: List[str]):
        self.YDataCB.clear()
        self.YDataCB.addItems(CBdata)

    def ChooseColor(self):
        self.color = QtWidgets.QColorDialog.getColor(self.color)
        palette = self.TraceColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.TraceColorButton.setPalette(palette)


class AddTracePopUp(QtWidgets.QDialog, UI_AddTracePopUp.Ui_AddTracePopUp):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.BodeTraceTypeCB.addItems(linestyle_dict.keys())
        self.MarkersCB.addItems(markers_dict.keys())
        self.MarkersCB.setCurrentText('nothing')
        self.MonteCarloGroupBox.setVisible(False)
        self.scrollArea.setVisible(False)
        self.color = QtGui.QColor("#FF8C00")
        palette = self.BodeColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.BodeColorButton.setPalette(palette)
        self.reader: Union[CSVDataReader, SpiceDataReader] = None
        self.tracesnames: List[str] = []
        self.traces: List[Trace] = []
        self.YDataList: List[YAxisDataWidget] = []
        self.YAxisQuantUpdate(self.YAxisQuantSpinBox.value())

    def exec(self) -> List[Trace]:
        super().exec()
        return self.traces

    def accept(self) -> None:

        if self.Dir2FileLE.text() == '':
            QtWidgets.QMessageBox.warning(self, "Advertencia",
                                          f"Elegi el archivo o te encripto todos los datos.")
            return
        for item in self.YDataList:
            if self.XDataCB.currentText() == item.YDataCB.currentText() and self.SignalRadioButton.isChecked():
                QtWidgets.QMessageBox.warning(self, "Advertencia",
                                              f"Elegi otros ejes que eso no puedo.")
                return

        if (self.FreqDataCB.currentText() == self.ModDataCB.currentText() or
            self.FreqDataCB.currentText() == self.PhaseDataCB.currentText()) and self.BodeRadioButton.isChecked():
            QtWidgets.QMessageBox.warning(self, "Advertencia",
                                          f"Elegi otros ejes que eso no puedo.")
            return

        if self.BodeRadioButton.isChecked():
            if not len(self.FreqOpLE.text()):
                freqop = getLambdaFromOperation("x")
            else:
                freqop = getLambdaFromOperation(self.FreqOpLE.text())

            if not len(self.ModOpLE.text()):
                modop = getLambdaFromOperation("x")
            else:
                modop = getLambdaFromOperation(self.ModOpLE.text())

            if not len(self.PhaseOpLE.text()):
                phaseop = getLambdaFromOperation("x")
            else:
                phaseop = getLambdaFromOperation(self.PhaseOpLE.text())

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

            modtrace = Trace(self.BodeTraceNameLE.text(), self.reader, self.color.name(),
                             self.BodeTraceTypeCB.currentText(), self.MarkersCB.currentText(), TraceType.Module)

            if phasereader is None:
                phasereader = self.reader

            phasetrace = Trace(self.BodeTraceNameLE.text(), phasereader, self.color.name(),
                               self.BodeTraceTypeCB.currentText(), self.MarkersCB.currentText(), TraceType.Phase)

            self.traces = [modtrace, phasetrace]

        else:
            if not len(self.XOpLE.text()):
                xop = getLambdaFromOperation("x")
            else:
                xop = getLambdaFromOperation(self.XOpLE.text())

            match self.reader:
                case CSVDataReader():
                    for YAxis in self.YDataList:
                        reader = CSVDataReader(self.Dir2FileLE.text())
                        data = YAxis.getData()
                        reader.config("Signal", self.XDataCB.currentText(), data[0],
                                      xop, data[4])
                        trace = Trace(data[1], reader, data[2],
                                      data[3], data[5], TraceType.Signal)
                        self.traces.append(trace)

                case SpiceDataReader():
                    if self.IsMCCheckBox.isChecked():
                        for YAxis in self.YDataList:
                            reader = SpiceDataReader(self.Dir2FileLE.text(), isMonteCarlo=True)
                            data = YAxis.getData()

                            reader.config("Signal", self.XDataCB.currentText(), data[0],
                                          xop, data[4], self.StepQuantSpinBox.value())

                            trace = Trace(data[1], reader, data[2],
                                          data[3], data[5], TraceType.Signal)

                            self.traces.append(trace)
                    else:
                        for YAxis in self.YDataList:
                            reader = SpiceDataReader(self.Dir2FileLE.text())
                            data = YAxis.getData()
                            reader.config("Signal", self.XDataCB.currentText(), data[0],
                                          xop, data[4])

                            trace = Trace(data[1], reader, data[2],
                                          data[3], data[5], TraceType.Signal)

                            self.traces.append(trace)

        self.done(0)
        pass

    def reject(self) -> None:
        self.done(0)
        pass

    def ChooseBodeColor(self):
        self.color = QtWidgets.QColorDialog.getColor(self.color)
        palette = self.BodeColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.BodeColorButton.setPalette(palette)

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
        self.FreqDataCB.clear()
        self.ModDataCB.clear()
        self.PhaseDataCB.clear()
        self.XDataCB.addItems(self.tracesnames)
        self.FreqDataCB.addItems(self.tracesnames)
        self.ModDataCB.addItems(self.tracesnames)
        self.PhaseDataCB.addItems(self.tracesnames)
        for Yaxis in self.YDataList:
            Yaxis.updateOptions(self.tracesnames)

    def YAxisQuantUpdate(self, newQuant: int):
        actualQuant = len(self.YDataList)

        if actualQuant > newQuant:
            for i in range(actualQuant - newQuant):
                oldY = self.YDataList.pop()
                oldY.GroupBox.deleteLater()

        else:
            for i in range(newQuant - actualQuant):
                newYData = YAxisDataWidget(self.SignalGroupBox, self.tracesnames, actualQuant + i + 1, 0, 1, 5)
                self.YDataList.append(newYData)
        return


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
