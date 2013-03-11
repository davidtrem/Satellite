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

"""This is the script to launch Satellite
"""

if __name__ == '__main__':

    import argparse

    from satellitelib.core import main
    try:
        from satellitelib.ipycore import main as ipymain
    except ImportError, mes:
        print mes
        ipy_support = False
    else:
        ipy_support = True

    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser(description="Run Satellite program")
    parser.add_argument("-i", "--ipy", help="run on top of ipython",
                        action="store_true")
    args = parser.parse_args()
    if args.ipy:
        if ipy_support:
            ipymain()
        else:
            print("You might have to install missing module(s) " +
                  "to run on top of ipython")
    else:
        main()
