#! /usr/bin/env python
# -*- coding: utf-8 -*-

#Copyright (c) 2010 Dimitri Linten

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



from distutils.core import setup
import py2exe


######################## py2exe setup options ################################

options  = {
    'py2exe': {'includes' : ['sip', 'PyQt4', 'PyQt4.QtGui',
                             'matplotlib.backends',
                             'matplotlib.backends.backend_qt4agg',
                             'matplotlib.figure','pylab', 'numpy',
                             'matplotlib.numerix.fft',
                             'matplotlib.numerix.linear_algebra',
                             'matplotlib.numerix.random_array'],
               'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo',
                            '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo',
                            '_ssl','bsddb', 'curses',
                            'email', 'pywin.debugger',
                            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                            'Tkconstants', 'Tkinter','wx'],
               'dll_excludes': ['libgdk-win32-2.0-0.dll',
                                'libgobject-2.0-0.dll',
                                'libglib-2.0-0.dll', 'libgtk-win32-2.0-0.dll',
                                'libgdk_pixbuf-2.0-0.dll', 'libcairo-2.dll',
                                'libpango-1.0-0.dll', 'libgthread-2.0-0.dll',
                                'tcl84.dll', 'tk84.dll',
                                'tcl85.dll', 'tk85.dll',
                                'msvcr71.dll'],
               }
    }

# since matplotlib v1
import matplotlib
matplotlibdata_files = matplotlib.get_py2exe_datafiles()
del matplotlibdata_files[-1]

data_files = ['Microsoft.VC90.CRT.manifest',
              'msvcr90.dll', 'msvcm90.dll', 'msvcp90.dll']

data_files = data_files+matplotlibdata_files

setup(
    options = options,
    # The lib directory contains everything except the executables
    # and the python dll.
    windows = [{'script' : 'run_satellite.py',
                'icon_resources': [(1, 'satellite.ico')]}],
    # use out build_installer class as extended py2exe build
    name = "Satellite",
    version = "0.?",  # --- change this! ---
    description = "",
    author = "David Trémouilles, Dimitri Linten",
    author_email = "david.trem@gmail.com, dimitri.linten@gmail.com",
    url = "http://code.google.com/p/esdanalysistools/",
    data_files = data_files
    )
