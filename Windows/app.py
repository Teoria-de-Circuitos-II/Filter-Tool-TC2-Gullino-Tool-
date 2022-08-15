import logging
import os
import sys

import control
from PyQt6 import QtWidgets, QtCore, QtGui
from matplotlib import rcParams, font_manager, pyplot as plt

from DataReader.TFDataReaderDeriv import TFDataReader
from Utils.Trace import Trace, TraceType
from Windows.AddSignalResponse import AddSignalResponse
from Windows.AddTracePopUp import AddTracePopUp
from Windows.ModTracePopUp import ModTracePopUp
from Windows.LoadTransferFunctionPopUp import LoadTransferFunctionPopUp
from UI.UI import Ui_MainWindow
from Utils.plotWidget import MplCanvas, scale


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.traceslist = []
        self.tfTrace = []
        self.FontFamilyComboBox.addItems(sorted(font_manager.font_family_aliases))
        self.FontFamilyComboBox.setCurrentText('serif')
        self.FontSizeSpinbox.setValue(15)
        self.ModPlot = MplCanvas(self.ModuloBox)
        self.ModPlot.changeXScales(scale.LogScale.name)
        self.ModPlot.changeYScales('db')
        self.PhasePlot = MplCanvas(self.PhaseBox)
        self.PhasePlot.changeXScales(scale.LogScale.name)
        self.PhasePlot.changeYScales(scale.LinearScale.name)
        self.SignalPlot = MplCanvas(self.RespuestaBox)
        self.SignalPlot.changeXScales(scale.LinearScale.name)
        self.SignalPlot.changeYScales(scale.LinearScale.name)

        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resource_path("info.png")))
        self.InfoButton.setIcon(icon)
        self.InfoButton.setIconSize(QtCore.QSize(30, 30))

    def Plot(self):
        ModTraces = []
        PhaseTraces = []
        SignalTraces = []

        for traceindex in range(len(self.traceslist)):
            traceitem = self.TracesListBox.item(traceindex)
            trace = self.traceslist[traceindex]

            if traceitem.checkState() == QtCore.Qt.CheckState.Checked:
                match trace.type.name:
                    case "Module":
                        ModTraces.append(trace)
                    case "Phase":
                        PhaseTraces.append(trace)
                    case "Signal":
                        SignalTraces.append(trace)
            else:
                continue
        try:
            self.ModPlot.plot(ModTraces)
            self.PhasePlot.plot(PhaseTraces)
            self.SignalPlot.plot(SignalTraces)
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al plotear. \n {values}")

        return

    def ModTrace(self, traceitem: QtWidgets.QListWidgetItem):
        try:
            traceindex = self.TracesListBox.indexFromItem(traceitem)
            selectedtrace = self.traceslist[traceindex.row()]
            popup = ModTracePopUp(selectedtrace.tracename, selectedtrace.color, selectedtrace.linetype)
            update = popup.exec()
            for i in range(len(update)):
                if update[i] != "":
                    match i:
                        case 0:
                            if isinstance(selectedtrace.reader,
                                          TFDataReader) and selectedtrace.type == TraceType.Module:
                                index2remove = self.TransFuncComboBox.findText(str(selectedtrace))
                                self.TransFuncComboBox.removeItem(index2remove)
                                selectedtrace.tracename = update[0]
                                traceitem.setText(str(selectedtrace))
                                self.TransFuncComboBox.addItem(str(selectedtrace))
                            else:
                                selectedtrace.tracename = update[0]
                                traceitem.setText(str(selectedtrace))

                        case 1:
                            selectedtrace.color = update[1]

                        case 2:
                            selectedtrace.linetype = update[2]

        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al modificar linea. \n {values}")

    def addTraceEvent(self):
        try:
            popup = AddTracePopUp()
            traces2add = popup.exec()
            logging.debug(traces2add)
            if hasattr(traces2add, '__iter__'):
                if None in traces2add:
                    return
                for trace in traces2add:
                    self.traceslist.append(trace)
                    item = QtWidgets.QListWidgetItem(str(trace), self.TracesListBox)
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                    self.TracesListBox.addItem(item)
            elif type(traces2add) is Trace:
                if traces2add is None:
                    return
                self.traceslist.append(traces2add)
                item = QtWidgets.QListWidgetItem(str(traces2add), self.TracesListBox)
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                self.TracesListBox.addItem(item)
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al agregar medicion. \n {values}")
        return

    def deleteTraceEvent(self):
        try:
            index2reamove = [index.row() for index in self.TracesListBox.selectedIndexes()]
            self.traceslist = [element for i, element in enumerate(self.traceslist) if i not in index2reamove]
            for item in self.TracesListBox.selectedItems():
                if self.TransFuncComboBox.findText(item.text()) != -1:
                    self.TransFuncComboBox.removeItem(self.TransFuncComboBox.findText(item.text()))
                self.TracesListBox.takeItem(self.TracesListBox.row(item))
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al quitar linea. \n {values}")

    def updateFontSize(self, fontsize: int):
        rcParams["font.size"] = fontsize

    def updateFontFamily(self, fontfamily: str):
        rcParams['font.family'] = fontfamily

    def addTransferFuction(self):
        try:
            popup = LoadTransferFunctionPopUp()
            traces2add = popup.exec()
            logging.debug(traces2add)
            if hasattr(traces2add, '__iter__'):
                if None in traces2add:
                    return
                self.tfTrace.append(traces2add[0])
                self.TransFuncComboBox.addItem(str(traces2add[0]))
                for trace in traces2add:
                    self.traceslist.append(trace)
                    item = QtWidgets.QListWidgetItem(str(trace), self.TracesListBox)
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                    self.TracesListBox.addItem(item)
            else:
                if traces2add is None:
                    return
                self.traceslist.append(traces2add)
                self.tfTrace.append(traces2add)
                self.TransFuncComboBox.addItem(str(traces2add))
                item = QtWidgets.QListWidgetItem(str(traces2add), self.TracesListBox)
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                self.TracesListBox.addItem(item)
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al agregar funcion transferencia. \n {values}")

    def addResponse2TF(self):
        try:
            if self.TransFuncComboBox.currentIndex() == -1:
                return
            trace2use = None
            for trace in self.tfTrace:
                if str(trace) == self.TransFuncComboBox.currentText():
                    trace2use = trace
            popup = AddSignalResponse(trace2use.reader.transFunc, trace2use.tracename)
            traces2add = popup.exec()
            logging.debug(traces2add)
            if type(traces2add) is tuple:
                if None in traces2add:
                    return
                for trace in traces2add:
                    self.traceslist.append(trace)
                    item = QtWidgets.QListWidgetItem(str(trace), self.TracesListBox)
                    item.setCheckState(QtCore.Qt.CheckState.Checked)
                    self.TracesListBox.addItem(item)
            else:
                if traces2add is None:
                    return
                self.traceslist.append(traces2add)
                item = QtWidgets.QListWidgetItem(str(traces2add), self.TracesListBox)
                item.setCheckState(QtCore.Qt.CheckState.Checked)
                self.TracesListBox.addItem(item)
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al agregar respuesta. \n {values}")

    def showPolesAndZeros(self):
        try:
            if self.TransFuncComboBox.currentIndex() == -1:
                return
            trace2use = None
            for trace in self.tfTrace:
                if str(trace) == self.TransFuncComboBox.currentText():
                    trace2use = trace
            tf = control.TransferFunction(trace2use.reader.transFunc.num, trace2use.reader.transFunc.den)
            control.pzmap(tf, plot=True)
            plt.show()
        except:
            types, values, traces = sys.exc_info()
            logging.error(values)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al mostrar diagrama de polos y ceros."
                                                          f" \n {values}")
        return

    def showInfo(self):
        QtWidgets.QMessageBox.information(self, "Informacion", 'Al usarse un archivo .raw como carga de datos es '
                                                               'importante que se elija no comprimir las mediciones, '
                                                               'dado que esto reduce mucho la calidad de los '
                                                               'gráficos. Para esto en la configuración de LTSpice, '
                                                               'se debe deshabilitar las opciones de compresión de '
                                                               '1er y 2do orden, que se encuentran en "Control '
                                                               'Panel"-> "Compression"\n\n'
                                                               'Para los archivos .csv, es necesario que la primera'
                                                               ' fila contenga los títulos de los datos, es lo que se '
                                                               'mostrará al momento de seleccionar que datos graficar.'
                                                               ' La segunda fila del archivo se saltea (mantiene'
                                                               ' compatibilidad con los osciloscopios digitales que '
                                                               'ponen las unidades en la segunda fila) ')
        return
