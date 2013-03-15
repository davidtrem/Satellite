# -*- coding: iso-8859-1 -*-

import os
from PyQt4 import QtGui, QtCore
import PyQt4.QtWebKit

QtCore.Signal = QtCore.pyqtSignal
QtCore.Slot = QtCore.pyqtSlot
QtGui.QFileDialog.getOpenFileNames = \
    QtGui.QFileDialog.getOpenFileNamesAndFilter

h = 400
l = 900


class Communicate(QtCore.QObject):
    value_changed = QtCore.Signal()
    save_doc = QtCore.Signal(str)


class PreferenceDialog(QtGui.QDialog):

    def __init__(self, parent=None):
        QtGui.QDialog.__init__(self, parent)
        self.dispo = QtGui.QVBoxLayout(self)
        self.setWindowTitle("Set Preference for the Report")
        #define the spot entry
        self.spotLayout = QtGui.QHBoxLayout()
        self.spotLayout.addWidget(QtGui.QLabel("Spot Value [V]:"))
        self.vspot = QtGui.QLineEdit()
        self.vspot.setValidator(QtGui.QDoubleValidator(self.vspot))
        self.spotLayout.addWidget(self.vspot)
        self.dispo.addLayout(self.spotLayout)
        #define the failure level entry
        self.failLayout = QtGui.QHBoxLayout()
        self.failLayout.addWidget(QtGui.QLabel("Fail Level [%]:"))
        self.pfail = QtGui.QLineEdit()
        self.pfail.setValidator(QtGui.QIntValidator(self.pfail))
        self.failLayout.addWidget(self.pfail)
        self.dispo.addLayout(self.failLayout)
        #define the threshold level entry
        self.seuilLayout = QtGui.QHBoxLayout()
        self.seuilLayout.addWidget(QtGui.QLabel("Threshold Level [V]:"))
        self.vseuil = QtGui.QLineEdit()
        self.vseuil.setValidator(QtGui.QDoubleValidator(self.vseuil))
        self.seuilLayout.addWidget(self.vseuil)
        self.dispo.addLayout(self.seuilLayout)

        self.butLayout = QtGui.QHBoxLayout()
        okButton = QtGui.QPushButton("OK", self)
        okButton.connect(okButton, QtCore.SIGNAL("clicked()"),
                         self, QtCore.SLOT("set_accept()"))
        cancelButton = QtGui.QPushButton("Cancel", self)
        cancelButton.connect(cancelButton, QtCore.SIGNAL("clicked()"),
                             self, QtCore.SLOT("reject()"))
        self.butLayout.addWidget(okButton)
        self.butLayout.addWidget(cancelButton)
        self.butLayout.addStretch()
        self.dispo.addStretch()
        self.dispo.addLayout(self.butLayout)
        self.setLayout(self.dispo)
        self.resize(600, 300)

    def set_accept(self):
        self.new_spot = float(self.vspot.text())
        self.new_fail = int(self.pfail.text())
        self.new_seuil = float(self.vseuil.text())

        self.accept()


class ReportWidget(QtGui.QWidget):

    def __init__(self, my_adr, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.dispo = QtGui.QVBoxLayout(self)

        my_url = PyQt4.QtCore.QUrl.fromLocalFile(my_adr)
        self.view = PyQt4.QtWebKit.QWebView(self)
        self.view.load(my_url)
        self.dispo.addWidget(self.view)
        self.setLayout(self.dispo)

    def printFile(self, printer):
        #printer.setPageSize(QtGui.QPrinter.A4)
        self.view.page().mainFrame().print_(printer)


class ReportFrame(QtGui.QMainWindow):
    def __init__(self, my_adr, parent=None):
        QtGui.QMainWindow.__init__(self, parent)

        self.setFont(QtGui.QFont("Verdana"))
        self.setWindowTitle("Report From TLP Measurement")
        try:
            self.setWindowIcon(QtGui.Icon("icon.jpg"))
        except:
            pass
        #TODO Very bad design should not pass on exception
        fen = QtGui.QDesktopWidget().screenGeometry()

        self.statusBar().showMessage("Report Window")

        menubar = self.menuBar()
        fileMenu = menubar.addMenu("&File")

        self.menusave = QtGui.QAction(
            "&Save", self, shortcut=QtGui.QKeySequence.Save,
            statusTip="Save the Report", triggered=self.save_in_file)
        fileMenu.addAction(self.menusave)

        self.menuprint = QtGui.QAction(
            "&Print", self, shortcut=QtGui.QKeySequence.Print,
            statusTip="Print the Report", triggered=self.print_file)
        fileMenu.addAction(self.menuprint)

        self.menuquit = QtGui.QAction(
            "&Close", self, shortcut=QtGui.QKeySequence.Close,
            statusTip="Quit the Application", triggered=self.close)
        fileMenu.addAction(self.menuquit)

        self.menupref = QtGui.QAction(
            "Preference", self,
            statusTip="define the preference for the report",
            triggered=self.set_preference)
        editMenu = menubar.addMenu("&Edit")
        editMenu.addAction(self.menupref)

        self.menuseuil = QtGui.QAction(
            "Show Threshold Data", self,
            statusTip="show the threshold data used for data extraction",
            triggered=self.show_threshold)
        editMenu.addAction(self.menuseuil)

        self.menucss = QtGui.QAction(
            "Set Report Style", self,
            statusTip="set css file to define the report style",
            triggered=self.set_css_file)
        editMenu.addAction(self.menucss)

        self.view = ReportWidget(my_adr, self)

        self.setCentralWidget(self.view)
        self.resize(l, h)
        size = self.geometry()
        self.move((fen.width() - size.width()) / 2,
                  (fen.height() - size.height()) / 2)
        self.report_adr = my_adr
        self.c = Communicate()
        self.css_change = Communicate()

    def save_in_file(self):
        saveName = QtGui.QFileDialog.getSaveFileName(
            self, "Save Report", ".", "Report Files (*.doc)")
        if not saveName[0] == "":
            self.c.save_doc.emit(saveName[0])

    def print_file(self):
        myPrint = QtGui.QPrinter()

        printDialog = QtGui.QPrintDialog(myPrint, self)
        if printDialog.exec_() == QtGui.QDialog.Accepted:
            self.view.printFile(myPrint)

    def set_preference(self):
        preference_dialog = PreferenceDialog(self)
        if preference_dialog.exec_() == QtGui.QDialog.Accepted:
            #print "values were accepted"
            #print preference_dialog.new_spot,preference_dialog.new_fail,
            #preference_dialog.new_seuil
            self.new_spot = preference_dialog.new_spot
            self.new_fail = preference_dialog.new_fail
            self.new_seuil = preference_dialog.new_seuil

            self.c.value_changed.emit()
        #else:
        #    print "canceled; don't do anything!"

    def show_threshold(self):
        baseDir = os.path.dirname(self.report_adr)
        baseDir = os.path.join(baseDir, 'report_analysis')
        my_url = PyQt4.QtCore.QUrl.fromLocalFile(baseDir + "/derivative.png")
        self.wind = QtGui.QMainWindow()
        self.myWid = PyQt4.QtWebKit.QWebView(self)
        self.myWid.load(my_url)
        self.wind.setCentralWidget(self.myWid)
        self.wind.show()

    def set_css_file(self):
        self.css_file = QtGui.QFileDialog.getOpenFileName(
            None, "Open css file", '',
            'CSS (*.css)', options=0)
        if len(self.css_file) > 0:
            self.css_str = self.css_file[0]
            self.css_change.value_changed.emit()
