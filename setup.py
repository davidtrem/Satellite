#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Python setup script for Satellite
"""

from distutils.core import setup
from satellitelib import __version__

setup(name='Satellite',
      version=__version__,
      author='David Trémouilles',
      author_email='david.trem at gmail.com',
      url='http://code.google.com/p/esdanalysistools/',
      license='MIT',
      platforms=['any'],
      packages=['satellitelib',
                'satellitelib.qt'],
      package_data={'satellitelib': ['satellite.png']},
      scripts=['satellite.py', ],
      )
