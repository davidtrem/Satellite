#! /usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2010 Dimitri Linten
#Copyright (c) 2011 David Tremouilles

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

"""Python setup script to generate
windows executable for Satellite
"""

from esky.bdist_esky import Executable
from distutils.core import setup
from satellite import __version__


######################## py2exe setup options ################################

options = {
    'bdist_esky': {
    'includes': [],
    'excludes': ['sip', 'PyQt4', 'PyQt4.QtGui', 'PyQt4.Qt',
                  'PyQt4.QtGui', 'PyQt4.QtCore', 'PyQt4.QtSvg',
                 '_gtkagg', '_tkagg', '_agg2', '_cairo',
                 '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo',
                 '_ssl', 'bsddb', 'curses',
                 'email', 'pywin.debugger',
                 'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                 'Tkconstants', 'Tkinter', 'wx'],
               }
               }

# since matplotlib v1
import matplotlib
matplotlibdata_files = matplotlib.get_py2exe_datafiles()
#del matplotlibdata_files[-1]

data_files = [('Microsoft.VC90.CRT', ('Microsoft.VC90.CRT.manifest',
              'msvcr90.dll', 'msvcm90.dll', 'msvcp90.dll'))]

data_files = data_files + matplotlibdata_files


run_sat = Executable('satellite.py',
            #  give our app the standard Python icon
            icon='satellite.ico',
            #  we could make the app gui-only by setting this to True
            gui_only=True,
            #  any other keyword args would be passed on to py2exe
          )

setup(
    options=options,
    scripts=[run_sat],
    # use out build_installer class as extended py2exe build
    name="Satellite",
    version=__version__,
    description="",
    author="David Trémouilles, Dimitri Linten",
    author_email="david.trem@gmail.com, dimitri.linten@gmail.com",
    url="http://code.google.com/p/esdanalysistools/",
    data_files=data_files
    )
