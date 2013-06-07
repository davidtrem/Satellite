# -*- coding: utf-8 -*-

#Copyright (c) 2013 David Trémouilles

#Permission is hereby granted, free of charge, to any person
#obtaining a copy of this software and associated documentation
#files (the "Software"), to deal in the Software without
#restriction, including without limitation the rights to use,
#copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the
#Software is furnished to do so, subject to the following
#conditions:

#The above copyright notice and this permission notice shall be
#included in all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
#OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
#NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
#HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
#WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
#OTHER DEALINGS IN THE SOFTWARE.

from .qt import QtCore
from .qt import QtGui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QTAgg as NavigationToolbar)

from thunderstorm.lightning.simple_plots import TLPFigure
from thunderstorm.lightning.simple_plots import TLPOverlayWithLeakEvol
from thunderstorm.lightning.simple_plots import LeakageIVsFigure
from thunderstorm.lightning.pulse_observer import TLPPulsePickFigure
from thunderstorm.lightning.leakage_observer import TLPLeakagePickFigure


class MatplotlibFig(QtGui.QWidget):
    # pylint: disable=R0904
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self, parent)
        figure = Figure()
        fig_canvas = FigureCanvasQTAgg(figure)
        fig_toolbar = NavigationToolbar(fig_canvas, self)
        fig_vbox = QtGui.QVBoxLayout()
        fig_vbox.addWidget(fig_canvas)
        fig_vbox.addWidget(fig_toolbar)
        fig_canvas.setParent(self)
        fig_canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        fig_canvas.setFocus()
        self.setLayout(fig_vbox)
        self.figure = figure


class TLPOverlayFig(MatplotlibFig):
    # pylint: disable=R0904
    def __init__(self, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = TLPOverlayWithLeakEvol(self.figure)


class TlpFig(MatplotlibFig):
    # pylint: disable=R0904
    def __init__(self, tlp_curve_data, title, leakage_evol=None, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = TLPFigure(self.figure, tlp_curve_data, title, leakage_evol)


class PulsesPickFig(MatplotlibFig):
    # pylint: disable=R0904
    def __init__(self, raw_data, title, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = TLPPulsePickFigure(self.figure, raw_data, title)


class LeakageIVsFig(MatplotlibFig):
    # pylint: disable=R0904
    def __init__(self, ivs_data, title, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = LeakageIVsFigure(self.figure, ivs_data, title)


class LeakagesPickFig(MatplotlibFig):
    # pylint: disable=R0904
    def __init__(self, raw_data, title, parent=None):
        MatplotlibFig.__init__(self, parent)
#       self.fig = LeakageIVsFigure(self.figure, ivs_data, title)
        self.fig = TLPLeakagePickFigure(self.figure, raw_data, title)
