#!/usr/bin/env python
#
# distutils setup script for filebutler package

from distutils.core import setup

setup(name='filebutler',
      version='0.4.0',
      description='Utility for managing old files in large directory structures',
      author='Simon Guest',
      author_email='simon.guest@tesujimath.org',
      url='https://github.com/tesujimath/filebutler',
      packages=['filebutler'],
      scripts=['bin/filebutler'],
      license='GPLv3'
     )
