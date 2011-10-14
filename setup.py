#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python setup script for Satellite
"""

from distutils.core import setup

setup(name = 'Satellite',
      version = '0.7a1',
      author = 'David Trémouilles',
      author_email = 'david.trem at gmail.com',
      url = 'http://code.google.com/p/esdanalysistools/',
      license = 'MIT',
      platforms = ['any'],
      packages = ['satellite'],
      scripts = ['run_satellite.py',],
      )
