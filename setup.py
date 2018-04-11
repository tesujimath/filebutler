#!/usr/bin/env python
#
# distutils setup script for filebutler package

from setuptools import setup, find_packages

long_description = """Filebutler is a utility for managing old files in huge directory trees.  Huge means of the order of 100 million files.  The motivation is that find is far too slow on directory trees with this many files.  Even working with filelists generated offline by find can be rather slow for interactive use.  Filebutler improves on this by structuring filelists by age, by size, by owner, and by dataset.
"""

setup(name='filebutler',
      use_scm_version=True,
      setup_requires=['setuptools_scm', 'setuptools_scm_git_archive'],
      description='Utility for managing old files in large directory structures',
      long_description=long_description,
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
          'Programming Language :: Python :: 3',
          'Topic :: System :: Systems Administration',
          'Topic :: Utilities',
      ],
      packages=find_packages(),
      entry_points={
        'console_scripts': [
            'filebutler = filebutler.__main__:main',
        ],
      },
      package_data={
          'doc': ['*.rst'],
          'examples': ['*'],
      },
      license='GPLv3',
      install_requires=[
          'future',
          'pytz',
          'setuptools',
          'tzlocal',
      ],
      python_requires='>=2.7',
     )
