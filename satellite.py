#! /usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2010 David Trémouilles

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


import sys
import os.path
from PyQt4 import QtCore
from PyQt4 import QtGui

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar

from thunderstorm.thunder.importers.tools import plug_dict
from thunderstorm.lightning.simple_plots import (TLPFigure,
                                                 PulsesFigure)
                                                 
                                                 
class MatplotlibFig(QtGui.QWidget):
    def __init__(self, parent=None):
        QtGui.QWidget.__init__(self)
        figure = Figure()
        fig_canvas = FigureCanvasQTAgg(figure)
        fig_toolbar = NavigationToolbar(fig_canvas, self)
        fig_vbox = QtGui.QVBoxLayout()
        fig_vbox.addWidget(fig_canvas)
        fig_vbox.addWidget(fig_toolbar)
        fig_canvas.setParent(self)
        self.setLayout(fig_vbox)
        self.figure = figure
                                            

class TlpFig(MatplotlibFig):
    def __init__(self, tlp_curve_data, title, leakage_evol=None, parent=None):           
        MatplotlibFig.__init__(self, parent)
        self.figure.canvas.setFocusPolicy( QtCore.Qt.ClickFocus )
        self.figure.canvas.setFocus()
        TLPFigure(self.figure, tlp_curve_data, title, leakage_evol)
 
class PulsesFig(MatplotlibFig):
    def __init__(self, pulses, title, parent=None):
        MatplotlibFig.__init__(self, parent)
        PulsesFigure(self.figure, pulses, title)       


class DevicesTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setMovable(True)
        self.setTabsClosable(False)
        self.setUsesScrollButtons(True)


class DeviceDataTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setMovable(False)
        self.setTabsClosable(False)
        self.setUsesScrollButtons(False)
        self.setTabPosition(QtGui.QTabWidget.West)


class ImportLoader(QtCore.QThread):
    new_data_ready = QtCore.pyqtSignal(object, str)
    def __init__(self, importer_name, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.importer_name = importer_name
        self.importer = plug_dict[self.importer_name]()
        self.file_ext = self.importer.file_ext
        self.file_name = ""

    def __call__(self, file_name):
        self.file_name = QtGui.QFileDialog.getOpenFileName(
            None, "Open %s data file"%self.importer_name, '',
            '%s (%s)'%(self.importer_name, self.file_ext))
        if self.file_name != "":
            self.start()

    def run(self):
        experiment = self.importer.load(unicode(self.file_name))
        self.new_data_ready.emit(experiment, self.file_name)


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("Satellite")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap('satellite.png'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.resize(800, 600)
        self.device_tab = DevicesTab(self)
        self.setCentralWidget(self.device_tab)

        file_menu = self.menuBar().addMenu("&File")
        import_menu = file_menu.addMenu("&Import")
        for importer_name in plug_dict.keys():
            load_file_action = QtGui.QAction("&%s"%importer_name, self)
            import_menu.addAction(load_file_action)
            loader = ImportLoader(importer_name, self)
            load_file_action.triggered.connect(loader)
            loader.new_data_ready.connect(self.add_new_experiment)


    def add_new_experiment(self, experiment, file_name):
        data_name = os.path.splitext(os.path.basename(unicode(file_name)))[0]
        device_data_tab = DeviceDataTab()
        device_data_tab.addTab(TlpFig(experiment.raw_data.tlp_curve,
                                      experiment.exp_name,
                                      experiment.raw_data.leak_evol),
                               "TLP curve")
        device_data_tab.addTab(PulsesFig(experiment.raw_data.pulses,
                                               experiment.exp_name),
                               "Pulses")
        self.device_tab.addTab(device_data_tab,
                               data_name)


def main():
    app = QtGui.QApplication(sys.argv)
    mainwin = MainWin()
    mainwin.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
