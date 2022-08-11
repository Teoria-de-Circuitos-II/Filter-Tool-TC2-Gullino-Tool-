import logging
import logging.config
import sys
from typing import Tuple

import numpy as np
import sympy as sp
from matplotlib import pyplot as plt
from scipy import signal
from sympy.parsing.sympy_parser import parse_expr, T
import UI.UI_AddSignalResponse
from PyQt6 import QtGui, QtWidgets
from DataReader.DataReaderBase import DataReader
from Utils.Trace import Trace, linestyle_dict, TraceType

functions_dict = {'Coseno': lambda f, A, t: A * np.cos(t * 2 * np.pi * f),
                  'Escalon': lambda tf: signal.step(tf, N=2000),
                  'Pulso periodico': lambda f, A, t, DC: A * signal.square(t * 2 * np.pi * f, DC),
                  'Triangular periodica': lambda f, A, t, DC: A * signal.sawtooth(t * 2 * np.pi * f, DC),
                  'Impulso': lambda tf: signal.impulse(tf, N=2000),
                  'Funcion arbitraria': lambda expr, time, f: getLambdaFromOperation(expr)(time * f)}


class AddSignalResponse(QtWidgets.QDialog, UI.UI_AddSignalResponse.Ui_AddSignalResponse):
    def __init__(self, transFunc, name):
        super().__init__()
        self.setupUi(self)
        self.tracename = name
        self.color = QtGui.QColor("#FF8C00")
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)
        self.TraceTypeCB.addItems(linestyle_dict.keys())
        self.ISComboBox.addItems(functions_dict.keys())
        self.transFunc = transFunc
        self.trace: Tuple[Trace, Trace] = None

    def exec(self) -> Tuple[Trace, Trace]:
        super().exec()
        return self.trace

    def accept(self) -> None:

        if self.ISComboBox.currentText() == 'Funcion arbitraria' and self.FuncInputTE.toPlainText() == '':
            return
        # 'Coseno': lambda f, A, t: A * np.cos(t * 2 * np.pi * f),
        # 'Escalon': lambda tf: signal.step(tf, N=2000),
        # 'Pulso periodico': lambda f, A, t, DC: A * signal.square(t * 2 * np.pi * f, DC),
        # 'Triangular periodica': lambda f, A, t, DC: A * signal.sawtooth(t * 2 * np.pi * f, DC),
        # 'Impulso': lambda tf: signal.impulse(tf, N=2000),
        # 'Funcion arbitraria': lambda expr, time, f: getLambdaFromOperation(expr)(time * f)
        inreader = DataReader()
        outreader = DataReader()
        periods_quant = self.TQUANTDoubleSpinBox.value()
        match self.ISComboBox.currentText():
            case 'Coseno':
                time = np.linspace(0, periods_quant / self.FInputCosDB.value(), int(np.round(1000 * periods_quant)))
                inputpoints = functions_dict['Coseno'](self.FInputCosDB.value(), self.AInputCosDB.value(), time)
                outtime, outputpoints, xoutpoints = signal.lsim(self.transFunc, inputpoints, time)
            case 'Escalon':
                time, outputpoints = functions_dict['Escalon'](self.transFunc)
                inputpoints = [1 for i in time]
                outtime = time
            case 'Pulso periodico':
                time = np.linspace(0, periods_quant / self.FInputCosDB.value(), int(1000 * periods_quant))
                inputpoints = functions_dict['Pulso periodico'](self.FInputCosDB.value(), self.AInputCosDB.value(),
                                                                time, self.DCInputTriagSqDB.value())
                outtime, outputpoints, xoutpoints = signal.lsim(self.transFunc, inputpoints, time)
            case 'Triangular periodica':
                time = np.linspace(0, periods_quant / self.FInputCosDB.value(), int(1000 * periods_quant))
                inputpoints = functions_dict['Triangular periodica'](self.FInputCosDB.value(), self.AInputCosDB.value(),
                                                                     time, self.DCInputTriagSqDB.value())
                outtime, outputpoints, xoutpoints = signal.lsim(self.transFunc, inputpoints, time)
            case 'Impulso':
                time, outputpoints = functions_dict['Impulso'](self.transFunc)
                maxtime = time[-1]
                outtime = time
                inputpoints = [0, 1, 0.9, 1, 0.9, 1, 0]
                time = [0, 0, 1/maxtime, 0, -1/maxtime, 0, 0]

            case 'Funcion arbitraria':
                time = np.linspace(0, 1 / self.FInputCosDB.value(), 1000)
                inputpoints = functions_dict['Funcion arbitraria'](self.FuncInputTE.toPlainText(), time,
                                                                   self.FInputCosDB.value())
                if periods_quant.is_integer():  # Cantidad entera de periodos
                    inputpoints = np.tile(inputpoints, int(periods_quant))
                else:  # Cantidad real de periodos
                    inputpoints = np.tile(inputpoints, int(np.floor(periods_quant) + 1))
                    indexlimit = int(1000 * periods_quant)
                    inputpoints = inputpoints[0:indexlimit]

                time = np.linspace(0, periods_quant / self.FInputCosDB.value(), int(1000 * periods_quant))
                outtime, outputpoints, xoutpoints = signal.lsim(self.transFunc, inputpoints, time)

        logging.debug(f"Largo de input: {len(inputpoints)}")
        logging.debug(f"Largo de output: {len(outputpoints)}")

        inreader.setData(time, inputpoints)
        outreader.setData(outtime, outputpoints)
        intrace = Trace(self.tracename + "Input", inreader, self.color.name(),
                        linestyle_dict[self.TraceTypeCB.currentText()], TraceType.Signal)
        outtrace = Trace(self.tracename + "Output", outreader, self.color.name(),
                         linestyle_dict[self.TraceTypeCB.currentText()], TraceType.Signal)
        self.trace = (intrace, outtrace)
        self.done(0)

    def reject(self) -> None:
        self.done(0)
        pass

    def CurrInputSignalComboBox(self, text):    # Combo box de seleccion de señal de entrada
        match text:
            case 'Coseno':
                self.InputTypeStackedWidget.setCurrentIndex(1)
            case 'Escalon':
                self.InputTypeStackedWidget.setCurrentIndex(0)
            case 'Pulso periodico':
                self.InputTypeStackedWidget.setCurrentIndex(2)
            case 'Triangular periodica':
                self.InputTypeStackedWidget.setCurrentIndex(2)
            case 'Impulso':
                self.InputTypeStackedWidget.setCurrentIndex(0)
            case 'Funcion arbitraria':
                self.InputTypeStackedWidget.setCurrentIndex(3)

    def ChooseColor(self):
        self.color = QtWidgets.QColorDialog.getColor(self.color)
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)


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


if __name__ == '__main__':
    logging.config.fileConfig("../logging.ini")
    app = QtWidgets.QApplication(sys.argv)
    AddTracePopUpxd = AddSignalResponse(signal.TransferFunction([1, 2], [3, 2]), "Try")
    trace = AddTracePopUpxd.exec()
    inputita = trace[0].reader.read()
    outputita = trace[1].reader.read()
    inputita.plot(x='X', y='Y', kind='line')
    outputita.plot(x='X', y='Y', kind='line')
    plt.show()
    sys.exit()
