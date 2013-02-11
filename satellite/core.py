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
from PyQt4 import QtCore
from PyQt4 import QtGui

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtGui.QFileDialog.getOpenFileNames = \
    QtGui.QFileDialog.getOpenFileNamesAndFilter


os.environ['QT_API'] = 'pyqt'  # for matplotlib to use pyqt

import matplotlib
matplotlib.use('Qt4Agg')  # For py2exe not to search other backends

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt4agg import (
    FigureCanvasQTAgg,
    NavigationToolbar2QTAgg as NavigationToolbar)

from thunderstorm.thunder.importers.tools import plug_dict
from thunderstorm.lightning.simple_plots import TLPFigure
from thunderstorm.lightning.simple_plots import TLPOverlayWithLeakEvol
from thunderstorm.lightning.simple_plots import LeakageIVsFigure

from thunderstorm.lightning.pulse_observer import TLPPulsePickFigure
from thunderstorm.istormlib.storm import Storm
from thunderstorm.istormlib.istorm_view import View

from thunderstorm.lightning.leakage_observer import TLPLeakagePickFigure

from thunderstorm.thunder.tlpanalysis import RawTLPdataAnalysis
from satellite.reporting import ReportFrame

from thunderstorm.thunder.tlp import Droplet


# automaticaly import and initialize qt resources
import satellite.qresource  # pylint: disable=W0611


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
    log_message_signal = QtCore.Signal(str)

    def __init__(self, importer_name, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.importer_name = importer_name
        self.importer = plug_dict[self.importer_name]()
        self.file_ext = self.importer.file_ext
        self.file_names = ""
        #Setup to display log messages in the status bar
        log = logging.getLogger('thunderstorm')
        log.setLevel(logging.INFO)
        channel = SatusBarLogHandler(self.log_message_signal)
        channel.setLevel(logging.INFO)
        channel.setFormatter(logging.Formatter('%(name)-12s: %(message)s'))
        log.addHandler(channel)

    def __call__(self):
        self.file_names = QtGui.QFileDialog.getOpenFileNames(
            None, "Open %s data file" % self.importer_name, '',
            '%s (%s)' % (self.importer_name, self.file_ext),)
            #options=QtGui.QFileDialog.DontUseNativeDialog)
        if len(self.file_names) > 0:
            self.start()  # Acutally call run self.run()

    def run(self):
        for file_name in self.file_names[0]:
            experiment = self.importer.load(str(file_name))
            self.new_data_ready.emit(experiment, file_name)


class SatusBarLogHandler(logging.Handler):
    def __init__(self, log_signal):
        logging.Handler.__init__(self)
        self.log_signal = log_signal

    def emit(self, record):
        log_message = self.format(record)
        self.log_signal.emit(log_message)


class MainWin(QtGui.QMainWindow):
    # pylint: disable=R0904
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Satellite")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(':/satellite.png'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        app.setWindowIcon(icon)
        self.resize(800, 600)

        self.statusBar().showMessage("Welcome in Satellite !")
        self.view_tab = ViewTab()
        tlp_overlay = TLPOverlayFig()
        self.core_storm = Storm(tlp_overlay.fig)
        self.view_tab.addTab(tlp_overlay, "TLP")
        # pointer to single tlp and pulsepicker figure
        self.tlpfig = None  # single tlp figure
        self.ppfig = None   # single pulse picker figure
        self.leakivsfig = None  # leakage IVs figure
        self.lpfig = None  # leakage IV pulse pick
        #initialize menu
        file_menu = self.menuBar().addMenu("&File")
        # Load oef file
        load_action = QtGui.QAction("&Load", self)
        file_menu.addAction(load_action)

        def load():
            file_names = QtGui.QFileDialog.getOpenFileNames(
                None, "Load oef file", '',
                'Open ESD Format (*.oef)',)
                #options=QtGui.QFileDialog.DontUseNativeDialog)
            if len(file_names) > 0:
                print file_names
                for file_name in file_names[0]:
                    experiment = Droplet(str(file_name))
                    self.add_new_experiment(experiment, file_name)
        load_action.triggered.connect(load)

        import_menu = file_menu.addMenu("&Import")
        for importer_name in plug_dict.keys():
            load_file_action = QtGui.QAction("&%s" % importer_name, self)
            import_menu.addAction(load_file_action)
            loader = ImportLoader(importer_name, self)
            load_file_action.triggered.connect(loader)
            loader.new_data_ready.connect(self.add_new_experiment)
            loader.log_message_signal.connect(self.status_bar_show_message)

        self.menuquit = QtGui.QAction("&Close", self,
                                      shortcut=QtGui.QKeySequence.Close,
                                      statusTip="Quit the Application",
                                      triggered=self.close)
        file_menu.addAction(self.menuquit)

        help_menu = self.menuBar().addMenu("&Help")
        self.about_action = QtGui.QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        self.about_action.setStatusTip("about satellite")
        help_menu.addAction(self.about_action)
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

        def show_leakage_pick():
            self.lpfig = LeakagesPickFig(experiment.raw_data, item.text())
            self.lpfig.show()

        def show_reporting():
            self.report_wind = ReportFrame(
                experiment.analysis.report.report_name)
            self.report_wind.c.value_changed.connect(update_report)
            self.report_wind.c.save_doc.connect(save_report)
            self.report_wind.css_change.value_changed.connect(
                update_report_style)
            self.report_wind.show()

        def update_report():
            experiment.analysis.spot_v = self.report_wind.new_spot
            experiment.analysis.fail_perc = self.report_wind.new_fail
            experiment.analysis.seuil = self.report_wind.new_seuil
            experiment.analysis.update_analysis()
            self.report_wind.view.view.reload()

        @QtCore.Slot(str)
        def save_report(save_name):
            experiment.analysis.save_analysis(save_name)
            #TODO should rename save_analysis by save

        def update_report_style():
            experiment.analysis.css = self.report_wind.css_str
            experiment.analysis.update_style()
            self.report_wind.view.view.reload()
            #TODO something is wrong with this naming

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
        #Set leakage picker in context menu
        leakage_pick_action = QtGui.QAction("Leakage pick tool", self)
        leakage_pick_action.triggered.connect(show_leakage_pick)
        leakage_pick_action.setEnabled(experiment.raw_data.has_leakage_ivs)
        leakage_pick_action.setStatusTip(
            "Visualize leakage data from selected TLP-data point(s)"
            if experiment.raw_data.has_leakage_ivs
            else "Sorry, No leakage data available")
        #Set report tool in context menu
        report_action = QtGui.QAction("Reporting tool", self)
        report_action.triggered.connect(show_reporting)
        report_action.setEnabled(experiment.analysis.has_report)
        report_action.setStatusTip(
            "Visualize report from selected TLP-data"
            if experiment.analysis.has_report
            else "Sorry, No report available")

        menu.addAction(pulse_pick_action)
        menu.addAction(tlp_action)
        menu.addAction(leakage_ivs_action)
        menu.addAction(leakage_pick_action)
        menu.addAction(report_action)
        menu.exec_(self.core_storm_listwdgt.mapToGlobal(position))

    def status_bar_show_message(self, message):
        self.statusBar().showMessage(message)

    def add_new_experiment(self, experiment, file_name):
        data_name = os.path.splitext(os.path.basename(str(file_name)))[0]
        experiment.exp_name = data_name
        self.core_storm.append(View(experiment))
        item = QtGui.QListWidgetItem(experiment.exp_name,
                                     self.core_storm_listwdgt)
        item.setToolTip(data_name)
        experiment.analysis = RawTLPdataAnalysis(experiment.raw_data)
        self.experiment_dict[id(item)] = experiment

    def core_storm_selection_change(self):
        items = self.core_storm_listwdgt.selectedItems()
        experiment_list = []
        for item in items:
            experiment_list.append(self.experiment_dict[id(item)])
        self.core_storm.overlay_raw_tlp(experiment_list=experiment_list)

    def show_about(self):
        about_str = ("Satellite\n\nversion:" + satellite.__version__ +
                     "\n\nCopyright (c) 2012 David Tremouilles\n\n")
        about_str = (about_str + "Satellite is software dedicated to " +
                     "view and analysis TLP measurements,")
        about_str = (about_str + "for further information please go on " +
                     "http://code.google.com/p/esdanalysistools/")
        QtGui.QMessageBox.about(self, "About Satellite", about_str)


def _init_logging():
    # Setting up logging to send INFO to the console
    log = logging.getLogger('thunderstorm')
    log.setLevel(logging.INFO)
    channel = logging.StreamHandler()
    channel.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(message)s')
    channel.setFormatter(formatter)
    log.addHandler(channel)


def main():
    """Call this function to run Satellite
    graphical user interface.
    """
    _init_logging()
    app = QtGui.QApplication(sys.argv)
    mainwin = MainWin(app)
    mainwin.show()
    sys.exit(app.exec_())
