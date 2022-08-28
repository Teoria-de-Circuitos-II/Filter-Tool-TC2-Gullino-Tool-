import logging
import os.path
from typing import List
import tikzplotlib as mpl2tikz
from PyQt6 import QtWidgets
import numpy as np
from matplotlib import scale, rcParams
from matplotlib.axes import Axes
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.widgets import Cursor
from pandas import DataFrame
import mplcursors
from Utils import Trace
from Scales import dBScaleClass, dBmScaleClass, OctaveScaleClass
from DataReader.SpiceDataReaderDeriv import SpiceDataReader
from Utils.Trace import linestyle_dict, markers_dict

scale.register_scale(dBScaleClass.dBScale)
scale.register_scale(dBmScaleClass.dBmScale)
scale.register_scale(OctaveScaleClass.OctaveScale)

usable_scales = ['db', 'linear', 'log', 'dbm', 'octave']


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        if dBScaleClass.dBScale.name not in scale.get_scale_names():
            scale.register_scale(dBScaleClass.dBScale)
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.dataCursors = []
        self.axes: Axes = self.fig.add_subplot()
        self.fig.set_tight_layout(True)
        super().__init__(self.fig)
        self.TitleLabel = QtWidgets.QLabel("Titulo:", parent)
        self.TitleLineEdit = QtWidgets.QLineEdit(parent)
        self.TitleLineEdit.setMinimumWidth(155)
        self.XAxisTitleLabel = QtWidgets.QLabel("Etiq X:", parent)
        self.XAxisTitleLineEdit = QtWidgets.QLineEdit(parent)
        self.XAxisTitleLineEdit.setMinimumWidth(155)
        self.YAxisTitleLabel = QtWidgets.QLabel("Etiq Y:", parent)
        self.YAxisTitleLineEdit = QtWidgets.QLineEdit(parent)
        self.YAxisTitleLineEdit.setMinimumWidth(155)
        self.XScaleLabel = QtWidgets.QLabel("Esc X:", parent)
        self.XScaleComboBox = QtWidgets.QComboBox(parent)
        self.YScaleLabel = QtWidgets.QLabel("Esc Y:", parent)
        self.YScaleComboBox = QtWidgets.QComboBox(parent)
        self.XScaleComboBox.addItems(usable_scales)
        self.YScaleComboBox.addItems(usable_scales)

        self.navToolBar = NavToolBar(self, parent)
        self.title = ""
        self.XAxisTitle = ''
        self.YAxisTitle = ''
        self.XScale = 'linear'
        self.YScale = 'linear'
        parent.layout().addWidget(self.navToolBar, 0, 0)
        parent.layout().addWidget(self, 1, 0, 1, 11)
        parent.layout().addWidget(self.TitleLabel, 0, 1)
        parent.layout().addWidget(self.TitleLineEdit, 0, 2)
        parent.layout().addWidget(self.XAxisTitleLabel, 0, 3)
        parent.layout().addWidget(self.XAxisTitleLineEdit, 0, 4)
        parent.layout().addWidget(self.YAxisTitleLabel, 0, 5)
        parent.layout().addWidget(self.YAxisTitleLineEdit, 0, 6)
        parent.layout().addWidget(self.XScaleLabel, 0, 7)
        parent.layout().addWidget(self.XScaleComboBox, 0, 8)
        parent.layout().addWidget(self.YScaleLabel, 0, 9)
        parent.layout().addWidget(self.YScaleComboBox, 0, 10)

        self.TitleLineEdit.textChanged['QString'].connect(self.changePlotTitle)
        self.XAxisTitleLineEdit.textChanged['QString'].connect(self.changeXAxisTitle)
        self.YAxisTitleLineEdit.textChanged['QString'].connect(self.changeYAxisTitle)
        self.XScaleComboBox.currentTextChanged['QString'].connect(self.changeXScales)
        self.YScaleComboBox.currentTextChanged['QString'].connect(self.changeYScales)

        self.cursor = Cursor(self.axes, useblit=True, color='gray', linestyle='--', linewidth=0.8)

    def changePlotTitle(self, title: str):
        self.title = title

    def changeXAxisTitle(self, title: str):
        self.XAxisTitle = title

    def changeYAxisTitle(self, title: str):
        self.YAxisTitle = title

    def changeXScales(self, xscale: str):
        self.XScale = xscale
        self.XScaleComboBox.setCurrentText(self.XScale)

    def changeYScales(self, yscale: str):
        self.YScale = yscale
        self.YScaleComboBox.setCurrentText(self.YScale)

    def plot(self, traces: List[Trace.Trace]):
        self.axes.clear()
        self.dataCursors.clear()

        for trace in traces:
            data: DataFrame = trace.reader.read()
            logging.debug(data)

            if type(trace.reader) is SpiceDataReader and trace.reader.isMonteCarlo():
                for i in range(len(data.columns) - 1):
                    if i == 0:
                        line = self.axes.plot(data.iloc[:, 0], data.iloc[:, i + 1], label=trace.tracename,
                                              ls=linestyle_dict[trace.linetype], color=trace.color,
                                              marker=markers_dict[trace.marker])
                    else:
                        line = self.axes.plot(data.iloc[:, 0], data.iloc[:, i + 1], ls=linestyle_dict[trace.linetype],
                                              color=trace.color, marker=markers_dict[trace.marker])

                    self.dataCursors.append(mplcursors.cursor(line))
            else:
                line = self.axes.plot(data.iloc[:, 0], data.iloc[:, 1], label=trace.tracename,
                                      ls=linestyle_dict[trace.linetype],
                                      color=trace.color, marker=markers_dict[trace.marker])
                self.dataCursors.append(mplcursors.cursor(line))

        self.axes.set_xscale(self.XScale)
        self.axes.set_yscale(self.YScale)
        self.axes.grid(which='both')
        self.axes.legend()
        self.axes.set_title(self.title, size=rcParams['font.size'], fontfamily=rcParams['font.family'])
        self.axes.set_xlabel(self.XAxisTitle, size=rcParams['font.size'], fontfamily=rcParams['font.family'])
        self.axes.set_ylabel(self.YAxisTitle, size=rcParams['font.size'], fontfamily=rcParams['font.family'])
        ylims = self.axes.get_ylim()
        if np.abs(ylims[0] - ylims[1]) < 0.00001:
            botylim = ylims[0] - 0.0005
            topylim = ylims[1] + 0.0005
            self.axes.set_ylim(botylim, topylim)

        self.fig.canvas.draw()
        self.fig.canvas.flush_events()


class NavToolBar(NavigationToolbar):
    def __init__(self, canvas, parent, *args, **kargs):
        self.toolitems = [element for i, element in enumerate(NavigationToolbar.toolitems) if
         i not in [1, 2, 3, 6, 7, 8]]
        self.toolitems.append(('Tex', 'Save as latex', 'None',
                                              'saveLatex'))
        super().__init__(canvas, parent, *args, **kargs)

    def saveLatex(self):
        path2dir = QtWidgets.QFileDialog.getSaveFileName(filter="Tex File (*.tex)")
        if path2dir[0] == '':
            return
        path2dir, filename = os.path.split(path2dir[0])
        filenameNoExt, extension = os.path.splitext(filename)
        if extension == '':
            filename = filename + ".tex"
        mpl2tikz.clean_figure(self.canvas.figure, target_resolution=200)
        tikztext: str = mpl2tikz.get_tikz_code(filepath=f"{path2dir}/{filename}", externalize_tables=True,
                                          figure=self.canvas.figure, dpi=200, float_format=".3E")

        transform = self.canvas.axes.get_xscale()
        xscaletype = scale._scale_mapping[transform]

        transform = self.canvas.axes.get_yscale()
        yscaletype = scale._scale_mapping[transform]
        if xscaletype == 'db' or xscaletype == 'dbm':
            pos = tikztext.find("\\begin{axis}[")
            tikztext = tikztext[:pos] + "\n log basis x=10, xmode=log, \n" + tikztext[pos:]
        elif xscaletype == 'octave':
            pos = tikztext.find("\\begin{axis}[")
            tikztext = tikztext[:pos] + "\n log basis x=2, xmode=log, \n" + tikztext[pos:]

        if yscaletype == 'db' or yscaletype == 'dbm':
            pos = tikztext.find("\\begin{axis}[")
            tikztext = tikztext[:pos] + "\n log basis y=10, ymode=log, \n" + tikztext[pos:]
        elif yscaletype == 'octave':
            pos = tikztext.find("\\begin{axis}[")
            tikztext = tikztext[:pos] + "\n log basis y=2, ymode=log, \n" + tikztext[pos:]

        tikztext = tikztext.replace("{opts_str}", "[]")
        with open(f"{path2dir}/{filename}", "w") as f:
            f.write(tikztext)


def make_format(current, other):
    # current and other are axes
    def format_coord(x, y):
        # x, y are data coordinates
        # convert to display coords
        display_coord = current.transData.transform((x, y))
        inv = other.transData.inverted()
        # convert back to data coords with respect to ax
        ax_coord = inv.transform(display_coord)
        coords = [ax_coord, (x, y)]
        return ('Left: {:<}   Right: {:}'
                .format(*['({:.3E}, {:.3E})'.format(x, y) for x, y in coords]))

    return format_coord


def format_coord_complex(x, y):
    return "{:.2E} + j*({:.2E})".format(x, y)


def calculate_ticks(ax, ticks, round_to=0.1, center=False):
    upperbound = np.ceil(ax.get_ybound()[1] / round_to)
    lowerbound = np.floor(ax.get_ybound()[0] / round_to)
    dy = upperbound - lowerbound
    fit = np.floor(dy / (ticks - 1)) + 1
    dy_new = (ticks - 1) * fit
    if center:
        offset = np.floor((dy_new - dy) / 2)
        lowerbound = lowerbound - offset
    values = np.linspace(lowerbound, lowerbound + dy_new, ticks)
    return values * round_to
