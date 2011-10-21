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
import logging
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
from thunderstorm.lightning.simple_plots import LeakageIVsFigure

from thunderstorm.lightning.pulse_observer import TLPPulsePickFigure
from thunderstorm.istormlib.storm import Storm
from thunderstorm.istormlib.istorm_view import View

# automaticaly import and initialize qt resources
import satellite.qresource # pylint: disable=W0611


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
        self.fig = TLPOverlay(self.figure)


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


class ViewTab(QtGui.QTabWidget):
    # pylint: disable=R0904
    def __init__(self, parent=None):
        QtGui.QTabWidget.__init__(self, parent)
        self.setMovable(True)
        self.setTabsClosable(False)
        self.setUsesScrollButtons(False)


class ImportLoader(QtCore.QThread):
    # pylint: disable=R0904
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


class SatusBarLogHandler(logging.Handler):
    def __init__(self, statusbar):
        logging.Handler.__init__(self)
        self.statusbar = statusbar

    def emit(self, record):
        log_message = self.format(record)
        self.statusbar.showMessage(log_message)


class MainWin(QtGui.QMainWindow):
    # pylint: disable=R0904
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Satellite")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/satellite.png'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.setWindowIcon(icon)
        self.resize(800, 600)

        #Setup to display log messages in the status bar
        log = logging.getLogger('thunderstorm')
        log.setLevel(logging.INFO)
        channel = SatusBarLogHandler(self.statusBar())
        channel.setLevel(logging.INFO)
        channel.setFormatter(logging.Formatter('%(name)-12s: %(message)s'))
        log.addHandler(channel)

        self.statusBar().showMessage("Welcome in Satellite !")
        self.view_tab = ViewTab()
        tlp_overlay = TLPOverlayFig()
        self.core_storm = Storm(tlp_overlay.fig)
        self.view_tab.addTab(tlp_overlay, "TLP")
        # pointer to single tlp and pulsepicker figure
        self.tlpfig = None  #single tlp figure
        self.ppfig = None   #single pulse picker figure
        self.leakivsfig = None #leakage IVs figure

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
        experiment = self.experiment_dict[id(item)]
        def show_pulse_pick():
            self.ppfig = PulsesPickFig(experiment.raw_data, item.text())
            self.ppfig.show()

        def show_tlp():
            self.tlpfig = TlpFig(experiment.raw_data.tlp_curve, item.text(),
                                 experiment.raw_data.leak_evol)
            self.tlpfig.show()

        def show_leakage_ivs():
            self.leakivsfig = LeakageIVsFig(experiment.raw_data.iv_leak,
                                            item.text())
            self.leakivsfig.show()

        menu = QtGui.QMenu(self)
        #Set pulse picker in context menu
        pulse_pick_action = QtGui.QAction("Pulse pick tool", self)
        pulse_pick_action.triggered.connect(show_pulse_pick)
        pulse_pick_action.setEnabled(experiment.raw_data.has_transient_pulses)
        pulse_pick_action.setStatusTip(
            "Visualize transient data from selected TLP-data point(s)"
            if experiment.raw_data.has_transient_pulses
            else "Sorry, No transient data available")
        #Set tlp with leakage evolution  in context menu
        tlp_action = QtGui.QAction("TLP with leakage", self)
        tlp_action.triggered.connect(show_tlp)
        tlp_action.setEnabled(experiment.raw_data.has_leakage_evolution)
        tlp_action.setStatusTip(
            "Visualize TLP with leakage evolution"
            if experiment.raw_data.has_leakage_evolution
            else "Sorry, No leakage evolution data available")
        #Set leakage ivs in context menu
        leakage_ivs_action = QtGui.QAction("Leakage IVs", self)
        leakage_ivs_action.triggered.connect(show_leakage_ivs)
        leakage_ivs_action.setEnabled(experiment.raw_data.has_leakage_ivs)
        leakage_ivs_action.setStatusTip(
            "Visualize leakage IVs"
            if experiment.raw_data.has_leakage_ivs
            else "Sorry, No leakage IVs available")

        menu.addAction(pulse_pick_action)
        menu.addAction(tlp_action)
        menu.addAction(leakage_ivs_action)
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
    # Setting up logging to send INFO to the console
    log = logging.getLogger('thunderstorm')
    log.setLevel(logging.INFO)
    channel = logging.StreamHandler()
    channel.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(message)s')
    channel.setFormatter(formatter)
    log.addHandler(channel)

    app = QtGui.QApplication(sys.argv)
    mainwin = MainWin()
    mainwin.show()
    sys.exit(app.exec_())

