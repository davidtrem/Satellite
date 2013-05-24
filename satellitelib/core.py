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
from os.path import (realpath, dirname)
import logging
from PyQt4 import QtCore
from PyQt4 import QtGui

import h5py

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtGui.QFileDialog.getOpenFileNames = \
    QtGui.QFileDialog.getOpenFileNamesAndFilter
QtGui.QFileDialog.getOpenFileName = \
    QtGui.QFileDialog.getOpenFileNameAndFilter


os.environ['QT_API'] = 'pyqt'  # for matplotlib to use pyqt

import matplotlib
matplotlib.use('Qt4Agg')  # For py2exe not to search other backends

from thunderstorm.thunder.importers.tools import plug_dict

from thunderstorm.istormlib.storm import Storm
from thunderstorm.istormlib.istorm_view import View

from thunderstorm.thunder.tlpanalysis import RawTLPdataAnalysis

from .matplot import (TLPOverlayFig, PulsesPickFig, TlpFig,
                      LeakageIVsFig, LeakagesPickFig)

from .guielem import SatusBarLogHandler, ViewTab
from .reporting import ReportFrame


class ImportLoader(QtCore.QThread):
    # pylint: disable=R0904
    new_data_ready = QtCore.Signal(object, object)
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
            raw_data = self.importer.raw_data_from_file(str(file_name))
            self.new_data_ready.emit(raw_data, self.importer)


class MainWin(QtGui.QMainWindow):
    # pylint: disable=R0904
    def __init__(self, app):
        QtGui.QMainWindow.__init__(self)
        self.setWindowTitle("Satellite")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(dirname(realpath(__file__))
                                     + os.sep + 'satellite.png'),
                       QtGui.QIcon.Normal, QtGui.QIcon.Off)
        app.setWindowIcon(icon)
        self.resize(800, 600)

        self.statusBar().showMessage("Welcome in Satellite !")
        self.view_tab = ViewTab()
        self.tlp_overlay = TLPOverlayFig()
        self.view_tab.addTab(self.tlp_overlay, "TLP")
        self.core_storm = None
        # pointer to single tlp and pulsepicker figure
        self.tlpfig = None  # single tlp figure
        self.ppfig = None   # single pulse picker figure
        self.leakivsfig = None  # leakage IVs figure
        self.lpfig = None  # leakage IV pulse pick

        file_menu = self.menuBar().addMenu("&File")

        #New oef file
        new_file_action = QtGui.QAction("&New", self)
        file_menu.addAction(new_file_action)

        def oef_new():
            new_name = QtGui.QFileDialog.getSaveFileName(
                self, "New oef file", './untitled.oef',
                "Open ESD Format (*.oef)")
            if new_name is not None:
                file_name = str(new_name)
                new_file = h5py.File(file_name, 'w')
                new_file.close()
                self.core_storm = Storm(file_name)
                self.core_storm_listwdgt.clear()
                self.droplet_dict = {}
        new_file_action.triggered.connect(oef_new)

        #Open oef file
        open_action = QtGui.QAction("&Open", self)
        file_menu.addAction(open_action)

        def oef_open():
            file_tuple = QtGui.QFileDialog.getOpenFileName(
                self, "Load oef file", '',
                'Open ESD Format (*.oef)',)
            if len(file_tuple) > 0:
                file_name = file_tuple[0]
                self.core_storm = Storm(str(file_name))
                self.core_storm_listwdgt.clear()
                self.droplet_dict = {}
                for view in self.core_storm:
                    droplet = view.experiment
                    item = QtGui.QListWidgetItem(droplet.exp_name,
                                                 self.core_storm_listwdgt)
                    item.setToolTip(droplet.exp_name)
                    self.droplet_dict[id(item)] = droplet
        open_action.triggered.connect(oef_open)

        # Import menu
        import_menu = file_menu.addMenu("&Import")
        for importer_name in plug_dict.keys():
            load_file_action = QtGui.QAction("&%s" % importer_name, self)
            import_menu.addAction(load_file_action)
            loader = ImportLoader(importer_name, self)
            load_file_action.triggered.connect(loader)
            loader.new_data_ready.connect(self.add_new_droplet)
            loader.log_message_signal.connect(self.status_bar_show_message)

        # Quit menu
        self.menuquit = QtGui.QAction("&Quit", self,
                                      shortcut=QtGui.QKeySequence.Close,
                                      statusTip="Quit the Application",
                                      triggered=self.close)
        file_menu.addAction(self.menuquit)

        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        self.about_action = QtGui.QAction("About", self)
        self.about_action.triggered.connect(self.show_about)
        self.about_action.setStatusTip("about satellite")
        help_menu.addAction(self.about_action)
        #initialize associated QListWidget to the open storm
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
        split = QtGui.QSplitter()
        split.addWidget(core_storm_listwdgt)
        split.addWidget(self.view_tab)
        layout = QtGui.QHBoxLayout()
        layout.addWidget(split)
        central_widget = QtGui.QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        self.core_storm_listwdgt = core_storm_listwdgt
        self.droplet_dict = {}

    def list_menu(self, position):
        item = self.core_storm_listwdgt.itemAt(position)
        droplet = self.droplet_dict[id(item)]

        def show_pulse_pick():
            self.ppfig = PulsesPickFig(droplet.raw_data, item.text())
            self.ppfig.show()

        def show_tlp():
            self.tlpfig = TlpFig(droplet.raw_data.tlp_curve, item.text(),
                                 droplet.raw_data.leak_evol)
            self.tlpfig.show()

        def show_leakage_ivs():
            self.leakivsfig = LeakageIVsFig(droplet.raw_data.iv_leak,
                                            item.text())
            self.leakivsfig.show()

        def show_leakage_pick():
            self.lpfig = LeakagesPickFig(droplet.raw_data, item.text())
            self.lpfig.show()

        def show_reporting():
            def update_report():
                droplet.analysis.spot_v = self.report_wind.new_spot
                droplet.analysis.fail_perc = self.report_wind.new_fail
                droplet.analysis.seuil = self.report_wind.new_seuil
                droplet.analysis.update_analysis()
                self.report_wind.view.view.reload()

            @QtCore.Slot(str)
            def save_report(save_name):
                droplet.analysis.save_analysis(save_name)
                #TODO should rename save_analysis by save

            def update_report_style():
                droplet.analysis.css = self.report_wind.css_str
                droplet.analysis.update_style()
                self.report_wind.view.view.reload()
                #TODO something is wrong with this naming
            if not hasattr(droplet, "analysis"):
                droplet.analysis = RawTLPdataAnalysis(droplet)
            self.report_wind = ReportFrame(
                droplet.analysis.report.report_name)
            self.report_wind.c.value_changed.connect(update_report)
            self.report_wind.c.save_doc.connect(save_report)
            self.report_wind.css_change.value_changed.connect(
                update_report_style)
            self.report_wind.show()

        menu = QtGui.QMenu(self)
        #Set pulse picker in context menu
        pulse_pick_action = QtGui.QAction("Pulse pick tool", self)
        pulse_pick_action.triggered.connect(show_pulse_pick)
        pulse_pick_action.setEnabled(droplet.raw_data.has_transient_pulses)
        pulse_pick_action.setStatusTip(
            "Visualize transient data from selected TLP-data point(s)"
            if droplet.raw_data.has_transient_pulses
            else "Sorry, No transient data available")
        #Set tlp with leakage evolution  in context menu
        tlp_action = QtGui.QAction("TLP with leakage", self)
        tlp_action.triggered.connect(show_tlp)
        tlp_action.setEnabled(droplet.raw_data.has_leakage_evolution)
        tlp_action.setStatusTip(
            "Visualize TLP with leakage evolution"
            if droplet.raw_data.has_leakage_evolution
            else "Sorry, No leakage evolution data available")
        #Set leakage ivs in context menu
        leakage_ivs_action = QtGui.QAction("Leakage IVs", self)
        leakage_ivs_action.triggered.connect(show_leakage_ivs)
        leakage_ivs_action.setEnabled(droplet.raw_data.has_leakage_ivs)
        leakage_ivs_action.setStatusTip(
            "Visualize leakage IVs"
            if droplet.raw_data.has_leakage_ivs
            else "Sorry, No leakage IVs available")
        #Set leakage picker in context menu
        leakage_pick_action = QtGui.QAction("Leakage pick tool", self)
        leakage_pick_action.triggered.connect(show_leakage_pick)
        leakage_pick_action.setEnabled(droplet.raw_data.has_leakage_ivs)
        leakage_pick_action.setStatusTip(
            "Visualize leakage data from selected TLP-data point(s)"
            if droplet.raw_data.has_leakage_ivs
            else "Sorry, No leakage data available")
        #Set report tool in context menu
        report_action = QtGui.QAction("Reporting tool", self)
        report_action.triggered.connect(show_reporting)
        report_action.setStatusTip("Visualize report from selected TLP-data")

        menu.addAction(pulse_pick_action)
        menu.addAction(tlp_action)
        menu.addAction(leakage_ivs_action)
        menu.addAction(leakage_pick_action)
        menu.addAction(report_action)
        menu.exec_(self.core_storm_listwdgt.mapToGlobal(position))

    def status_bar_show_message(self, message):
        self.statusBar().showMessage(message)

    def add_new_droplet(self, raw_data, importer):
        droplet = importer.load_in_droplet(raw_data, self.core_storm._h5file)
        self.core_storm.append(View(droplet))
        item = QtGui.QListWidgetItem(droplet.exp_name,
                                     self.core_storm_listwdgt)
        item.setToolTip(droplet.raw_data.original_file_name)
        self.droplet_dict[id(item)] = droplet

    def core_storm_selection_change(self):
        items = self.core_storm_listwdgt.selectedItems()
        droplet_list = []
        for item in items:
            droplet_list.append(self.droplet_dict[id(item)])
        self.core_storm.overlay_raw_tlp(self.tlp_overlay.fig,
                                        experiment_list=tuple(droplet_list))

    def show_about(self):
        about_str = ("Satellite\n\nversion:" + satellitelib.__version__ +
                     "\n\nCopyright (c) 2013 David Tremouilles\n\n")
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
