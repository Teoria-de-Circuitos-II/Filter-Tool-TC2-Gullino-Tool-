import logging
import sys

from PyQt6 import QtWidgets, QtCore
from matplotlib import rcParams, font_manager

from Windows.AddTracePopUp import AddTracePopUp
from Windows.ModTracePopUp import ModTracePopUp
from Windows.LoadTransferFunctionPopUp import LoadTransferFunctionPopUp
from UI.UI import Ui_MainWindow
from Utils.plotWidget import MplCanvas, scale


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.traceslist = []
        self.FontFamilyComboBox.addItems(sorted(font_manager.font_family_aliases))
        self.FontFamilyComboBox.setCurrentText('serif')
        self.ModPlot = MplCanvas(self.ModuloBox)
        self.ModPlot.changeXScales(scale.LogScale.name)
        self.ModPlot.changeYScales('db')
        self.PhasePlot = MplCanvas(self.PhaseBox)
        self.PhasePlot.changeXScales(scale.LogScale.name)
        self.PhasePlot.changeYScales(scale.LinearScale.name)
        self.SignalPlot = MplCanvas(self.RespuestaBox)
        self.SignalPlot.changeXScales(scale.LinearScale.name)
        self.SignalPlot.changeYScales(scale.LinearScale.name)

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
            logging.error(values.strerror)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al plotear. \n {values.strerror}")

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
                            selectedtrace.tracename = update[0]
                            traceitem.setText(str(selectedtrace))

                        case 1:
                            selectedtrace.color = update[1]

                        case 2:
                            selectedtrace.linetype = update[2]

        except:
            types, values, traces = sys.exc_info()
            logging.error(values.strerror)
            QtWidgets.QMessageBox.critical(self, "Error", f"Error: Problemas al modificar linea. \n {values.strerror}")

    def addTraceEvent(self):
        popup = AddTracePopUp()
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

        return

    def deleteTraceEvent(self):
        index2reamove = [index.row() for index in self.TracesListBox.selectedIndexes()]
        self.traceslist = [element for i, element in enumerate(self.traceslist) if i not in index2reamove]
        for item in self.TracesListBox.selectedItems():
            self.TracesListBox.removeItemWidget(item)

    def updateFontSize(self, fontsize: int):
        rcParams["font.size"] = fontsize

    def updateFontFamily(self, fontfamily: str):
        rcParams['font.family'] = fontfamily

    def addTransferFuction(self):
        popup = LoadTransferFunctionPopUp()
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

    def showPolesAndZeros(self):

        print("hola")
