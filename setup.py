#!/usr/bin/env python
#
# distutils setup script for filebutler package

import os
from setuptools import setup

setup(name='filebutler',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      description='Utility for managing old files in large directory structures',
      author='Simon Guest',
      author_email='simon.guest@tesujimath.org',
      url='https://github.com/tesujimath/filebutler',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      packages=['filebutler'],
      scripts=['bin/filebutler'],
      license='GPLv3',
      install_requires=[
          'pytz',
          'tzlocal',
      ],
      python_requires='>=2.7, <3',
     )
