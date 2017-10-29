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

class SimpleFilesetCache(object):

    def __init__(self, path):
        self._path = path
        self._filespecs = None

    def select(self, filter=None):
        if self._filespecs is None:
            self._filespecs = []
            with open(self._path, 'r') as f:
                for filespec in Filespec.fromFile(f):
                    self._filespecs.append(filespec)
                    #print("SimpleFilesetCache read from file %s" % filespec)
                    yield filespec
        else:
            for filespec in self._filespecs:
                if filter is None or filter.selects(filespec):
                    #print("SimpleFilesetCache read from memory %s" % filespec)
                    yield filespec

    def save(self):
        with open(self._path, 'w') as f:
            if self._filespecs is not None:
                for filespec in self._filespecs:
                    filespec.write(f)

    def add(self, filespec):
        if self._filespecs is None:
            self._filespecs = []
        self._filespecs.append(filespec)
