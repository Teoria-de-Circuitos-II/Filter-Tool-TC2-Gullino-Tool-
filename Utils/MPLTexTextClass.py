from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure
from matplotlib.axes import Axes


class MPLTexText(FigureCanvas):
    def __init__(self, parent=None, width=.5, height=.5, dpi=100):
        self.left, self.Rectwidth = .25, width
        self.bottom, self.Rectheight = .25, height
        self.right = self.left + self.Rectwidth
        self.top = self.bottom + self.Rectheight

        self.fig = Figure(figsize=(self.Rectwidth, self.Rectheight), dpi=dpi)
        super().__init__(self.fig)
        if parent is not None:
            parent.layout().addWidget(self)
        self.ax: Axes = self.fig.add_subplot()
        self.ax.set_axis_off()

    def updateTex(self, latexExpr: str):
        self.ax.clear()
        self.ax.text(0.5 * (self.left + self.right), 0.5 * (self.bottom + self.top), latexExpr,
                     horizontalalignment='center',
                     verticalalignment='center',
                     transform=self.ax.transAxes,
                     fontsize=18)
        self.ax.set_axis_off()
        self.draw()
