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
from FilesetInfo import FilesetInfo
from util import verbose_stderr, debug_stderr

class SimpleFilesetCache(object):

    def __init__(self, path):
        #debug_stderr("SimpleFilesetCache(%s)::__init__)\n" % path)
        self._path = path
        self._filespecs = None  # in-memory read cache
        self._info = {}         # indexed by filter string
        self._file = None
        self._fileinfo = None

    def filelistpath(self):
        return os.path.join(self._path, "filelist")

    def infopath(self):
        return os.path.join(self._path, "info")

    def select(self, filter=None):
        if self._filespecs is None:
            #debug_stderr("SimpleFilesetCache select %s from file cache %s\n" % (str(filter), self._path))
            self._filespecs = []
            with open(self.filelistpath(), 'r') as f:
                #debug_stderr("SimpleFilesetCache select %s opened file cache\n" % str(filter))
                for filespec in Filespec.fromFile(f):
                    self._filespecs.append(filespec)
                    if filter is None or filter.selects(filespec):
                        #debug_stderr("SimpleFilesetCache read from file %s\n" % filespec)
                        yield filespec
        else:
            #debug_stderr("SimpleFilesetCache select %s from memory cache\n" % str(filter))
            for filespec in self._filespecs:
                if filter is None or filter.selects(filespec):
                    #debug_stderr("SimpleFilesetCache read from memory %s\n" % filespec)
                    yield filespec

    def merge_info(self, inf1, filter=None):
        if filter is None:
            #debug_stderr("SimpleFilesetCache(%s)::merge_info(None)\n" % self._path)
            if self._fileinfo is None:
                #debug_stderr("SimpleFilesetCache(%s)::merge_info(None) reading info file\n" % self._path)
                with open(self.infopath(), 'r') as f:
                    self._fileinfo = FilesetInfo.fromFile(f)
            inf0 = self._fileinfo
        else:
            f = str(filter)
            #debug_stderr("SimpleFilesetCache(%s)::merge_info(%s)\n" % (self._path, f))
            if self._info.has_key(f):
                inf0 = self._info[f]
            else:
                #debug_stderr("SimpleFilesetCache(%s)::merge_info(%s) scanning\n" % (self._path, f))
                inf0 = FilesetInfo()
                self._info[f] = inf0
                for filespec in self.select(filter):
                    inf0.add(filespec)
        inf1.merge(inf0)

    def add(self, filespec):
        if self._fileinfo is None:
            self._fileinfo = FilesetInfo()
        self._fileinfo.add(filespec)
        # don't cache writes, as this would mean caching the whole of the filelist
        if self._file is None:
            #debug_stderr("SimpleFilesetCache writing file cache at %s\n" % self._path)
            if not os.path.exists(self._path):
                os.makedirs(self._path)
            self._file = open(self.filelistpath(), 'w')
        filespec.write(self._file)

    def flush(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        if self._file is not None:
            #debug_stderr("flushing %s\n" % self.filelistpath())
            self._file.close()
            self._file = None

    def writeInfo(self):
        with open(self.infopath(), 'w') as infofile:
            if self._fileinfo is not None:
                self._fileinfo.write(infofile)
