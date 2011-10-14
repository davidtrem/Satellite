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

"""This is the core part of Satellite graphical user interface.
"""


import sys
import os
import os.path
from PySide import QtCore
from PySide import QtGui

os.environ['QT_API'] = 'pyside' # for matplotlib to use pyside
import matplotlib
matplotlib.use('Qt4Agg') #for py2exe not to search other backends

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QTAgg as NavigationToolbar)

from thunderstorm.thunder.importers.tools import plug_dict
from thunderstorm.lightning.simple_plots import TLPFigure
from thunderstorm.lightning.simple_plots import TLPOverlay

from thunderstorm.lightning.pulse_observer import TLPPulsePickFigure
from thunderstorm.istormlib.storm import Storm
from thunderstorm.istormlib.istorm_view import View

# automaticaly import and initialize qt resources
import satellite.qresource # pylint: disable=W0611


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

class TLPOverlayFig(MatplotlibFig):
    def __init__(self, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = TLPOverlay(self.figure)


class TlpFig(MatplotlibFig):
    def __init__(self, tlp_curve_data, title, leakage_evol=None, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.figure.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.figure.canvas.setFocus()
        self.fig = TLPFigure(self.figure, tlp_curve_data, title, leakage_evol)


class PulsesPickFig(MatplotlibFig):
    def __init__(self, raw_data, title, parent=None):
        MatplotlibFig.__init__(self, parent)
        self.fig = TLPPulsePickFigure(self.figure, raw_data, title)


class ViewTab(QtGui.QTabWidget):
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setMovable(True)
        self.setTabsClosable(False)
        self.setUsesScrollButtons(False)


class ImportLoader(QtCore.QThread):
    new_data_ready = QtCore.Signal(object, str)
    def __init__(self, importer_name, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.importer_name = importer_name
        self.importer = plug_dict[self.importer_name]()
        self.file_ext = self.importer.file_ext
        self.file_names = ""

    def __call__(self):
        self.file_names = QtGui.QFileDialog.getOpenFileNames(
            None, "Open %s data file"%self.importer_name, '',
            '%s (%s)'%(self.importer_name, self.file_ext),
            options = QtGui.QFileDialog.DontUseNativeDialog)
        if len(self.file_names) > 0:
            self.start()

    def run(self):
        for file_name in self.file_names[0]:
            experiment = self.importer.load(file_name)
            self.new_data_ready.emit(experiment, file_name)


class MainWin(QtGui.QMainWindow):
    def __init__(self, parent=None):
        QtGui.QMainWindow.__init__(self, parent)
        self.setWindowTitle("Satellite")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/satellite.png'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.resize(800, 600)
        self.view_tab = ViewTab()
        tlp_overlay = TLPOverlayFig()
        self.core_storm = Storm(tlp_overlay.fig)
        self.view_tab.addTab(tlp_overlay, "TLP")
        # pointer to single tlp and pulsepicker figure
        self.tlpfig = None  #single tlp figure
        self.ppfig = None   #single pulse picker figure

        #initialize menu
        file_menu = self.menuBar().addMenu("&File")
        import_menu = file_menu.addMenu("&Import")
        for importer_name in plug_dict.keys():
            load_file_action = QtGui.QAction("&%s"%importer_name, self)
            import_menu.addAction(load_file_action)
            loader = ImportLoader(importer_name, self)
            load_file_action.triggered.connect(loader)
            loader.new_data_ready.connect(self.add_new_experiment)

        #initialize core_storm and associated QListWidget
        core_storm_listwdgt = QtGui.QListWidget(self)
        core_storm_listwdgt.setSelectionMode(
            QtGui.QAbstractItemView.ExtendedSelection)
        core_storm_listwdgt.setDragDropMode(
            QtGui.QAbstractItemView.InternalMove)
        core_storm_listwdgt.itemSelectionChanged.connect(
            self.core_storm_selection_change)
        core_storm_listwdgt.setSortingEnabled(True)
        core_storm_listwdgt.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        core_storm_listwdgt.customContextMenuRequested.connect(self.list_menu)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(core_storm_listwdgt)
        layout.addWidget(self.view_tab)
        central_widget = QtGui.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.core_storm_listwdgt = core_storm_listwdgt
        self.experiment_dict = {}

    def list_menu(self, position):
        item = self.core_storm_listwdgt.itemAt(position)
        def show_pulse_pick():
            experiment = self.experiment_dict[id(item)]
            self.ppfig = PulsesPickFig(experiment.raw_data, item.text())
            self.ppfig.show()
        def show_tlp():
            experiment = self.experiment_dict[id(item)]
            self.tlpfig = TlpFig(experiment.raw_data.tlp_curve, item.text(),
                                 experiment.raw_data.leak_evol)
            self.tlpfig.show()

        menu = QtGui.QMenu(parent=self)
        pulse_pick_action = QtGui.QAction("Pulse pick", menu)
        pulse_pick_action.triggered.connect(show_pulse_pick)
        tlp_action = QtGui.QAction("Show TLP", menu)
        tlp_action.triggered.connect(show_tlp)
        menu.addAction(pulse_pick_action)
        menu.addAction(tlp_action)
        menu.exec_(self.core_storm_listwdgt.mapToGlobal(position))


    def add_new_experiment(self, experiment, file_name):
        data_name = os.path.splitext(os.path.basename(file_name))[0]
        experiment.exp_name = data_name
        self.core_storm.append(View(experiment))
        item = QtGui.QListWidgetItem(experiment.exp_name,
                                     self.core_storm_listwdgt)
        item.setToolTip(data_name)
        self.experiment_dict[id(item)] = experiment

    def core_storm_selection_change(self):
        items = self.core_storm_listwdgt.selectedItems()
        experiment_list = []
        for item in items:
            experiment_list.append(self.experiment_dict[id(item)])
        self.core_storm.overlay_raw_tlp(experiment_list=experiment_list)


def main():
    """Call this function to run Satellite
    graphical user interface.
    """
    app = QtGui.QApplication(sys.argv)
    mainwin = MainWin()
    mainwin.show()
    sys.exit(app.exec_())

