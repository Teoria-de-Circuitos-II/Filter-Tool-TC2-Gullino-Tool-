from PyQt6 import QtGui, QtWidgets
from Utils.Trace import linestyle_dict
from typing import Tuple
from UI import UI_ModTracePopUp


class ModTracePopUp(QtWidgets.QDialog, UI_ModTracePopUp.Ui_ModTracePopUp):
    def __init__(self, name, color, linetype):
        super().__init__()
        self.setupUi(self)

        self.TraceTypeCB.addItems(linestyle_dict.keys())
        self.TraceTypeCB.setCurrentText(linetype)

        self.TraceNameLE.setText(name)

        self.color = QtGui.QColor(color)
        palette = self.ColorButton.palette()
        palette.setColor(QtGui.QPalette.ColorRole.Button, self.color)
        self.ColorButton.setPalette(palette)

        self.data = ("", "", "")

    def exec(self) -> Tuple[str, str, str]:
        super().exec()
        return self.data

    def accept(self) -> None:
        self.data = (self.TraceNameLE.text(), self.color.name(), self.TraceTypeCB.currentText())
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



