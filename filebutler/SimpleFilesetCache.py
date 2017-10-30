# Copyright 2017 Simon Guest
#
# This file is part of filebutler.
#
# Filebutler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Filebutler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with filebutler.  If not, see <http://www.gnu.org/licenses/>.

import os.path

from Filespec import Filespec
from util import verbose_stderr, diagnostic_stderr

class SimpleFilesetCache(object):

    def __init__(self, path):
        self._path = path
        self._filespecs = None  # in-memory read cache
        self._file = None

    def select(self, filter=None):
        if self._filespecs is None:
            #diagnostic_stderr("SimpleFilesetCache select %s from file cache %s\n" % (str(filter), self._path))
            self._filespecs = []
            with open(self._path, 'r') as f:
                #diagnostic_stderr("SimpleFilesetCache select %s opened file cache\n" % str(filter))
                for filespec in Filespec.fromFile(f):
                    self._filespecs.append(filespec)
                    #diagnostic_stderr("SimpleFilesetCache read from file %s\n" % filespec)
                    yield filespec
        else:
            #diagnostic_stderr("SimpleFilesetCache select %s from memory cache\n" % str(filter))
            for filespec in self._filespecs:
                if filter is None or filter.selects(filespec):
                    #diagnostic_stderr("SimpleFilesetCache read from memory %s\n" % filespec)
                    yield filespec

    def add(self, filespec):
        # don't cache writes, as this would mean caching the whole of the filelist
        if self._file is None:
            #diagnostic_stderr("SimpleFilesetCache writing file cache at %s\n" % self._path)
            self._file = open(self._path, 'w')
        filespec.write(self._file)

    def flush(self):
        if self._file is not None:
            #diagnostic_stderr("flushing %s\n" % self._path)
            self._file.close()
            self._file = None
