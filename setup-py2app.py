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

from distutils.core import setup
import py2app
from satellite import __version__

######################## py2exe setup options ################################

options = {
    'py2exe': {'includes': ['sip', 'PyQt4', 'PyQt4.QtGui'],
                'excludes': ['_gtkagg', '_tkagg', '_agg2', '_cairo',
                             '_cocoaagg', '_fltkagg', '_gtk', '_gtkcairo',
                             '_ssl', 'bsddb', 'curses',
                             'email', 'pywin.debugger',
                             'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
                             'Tkconstants', 'Tkinter', 'wx'],
               }
    }

# since matplotlib v1
import matplotlib
data_files = matplotlib.get_py2exe_datafiles()

setup(
    options=options,
    # The lib directory contains everything except the executables
    # and the python dll.
    app=["satellite.py"],
    setup_requires=["py2app"],
    name="Satellite",
    version=__version__,
    description="",
    author="David Trémouilles",
    author_email="david.trem@gmail.com",
    url="http://code.google.com/p/esdanalysistools/",
    data_files=data_files
    )
