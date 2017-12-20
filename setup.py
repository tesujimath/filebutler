#!/usr/bin/env python
#
# distutils setup script for filebutler package

import os
from distutils.core import setup

setup(name='filebutler',
      version=os.environ['VERSION'],
      description='Utility for managing old files in large directory structures',
      author='Simon Guest',
      author_email='simon.guest@tesujimath.org',
      url='https://github.com/tesujimath/filebutler',
      packages=['filebutler'],
      scripts=['bin/filebutler'],
      license='GPLv3'
     )
