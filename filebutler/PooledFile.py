# Copyright 2017-2018 Simon Guest
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import errno
import os

from .FatalError import FatalError
from .util import debug_log

def listdir(path):
    """Just like os.listdir, but close pooled files if hit too many open."""
    try:
        files = os.listdir(path)
    except OSError as e:
        if e.errno == errno.EMFILE:
            debug_log("listdir failed for %s, flush all pooled files\n" % path)
            PooledFile.flushAll()
            files = os.listdir(path)
        else:
            raise
    return files

class PooledFile(object):
    """A File object in a pool, which catches too many open files."""

    pool = {}

    @classmethod
    def flushAll(cls):
        """Flush all files in the pool."""
        for f in list(cls.pool.keys()):
            f.flush()

    def __init__(self, name, mode='r'):
        self._name = name
        self._mode = mode
        self._file = None
        self._readpos = None
        self.__class__.pool[self] = True

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()

    def _readmode(self):
        return self._mode == 'r'

    def _open(self):
        try:
            self._file = open(self._name, self._mode)
        except IOError as e:
            if e.errno == errno.EMFILE:
                debug_log("open failed for %s, flush all pooled files\n" % self._name)
                # It would be better to implement an LRU cache, but that
                # hardly seems worth it.  So simply close them all.
                self.__class__.flushAll()
                self._file = open(self._name, self._mode)
            else:
                raise
        if self._readmode() and self._readpos is not None:
            self._file.seek(self._readpos)

    def __iter__(self):
        """Iterate over the lines in a file opened for read."""
        done = False
        while not done:
            if self._file is None:
                self._open()
            line = self._file.readline()
            if line != '':
                yield line
            else:
                done = True

    def seek(self, offset):
        if self._file is not None:
            self._file.seek(offset)
        elif self._readmode():
            self._readpos = offset
        else:
            raise FatalError("seek on closed PooledFile for write, unsupported")

    def tell(self):
        if self._file is not None:
            return self._file.tell()
        elif self._readmode():
            return self._readpos
        else:
            raise FatalError("tell on closed PooledFile for write, unsupported")

    def write(self, s):
        if self._file is None:
            self._open()
        self._file.write(s)

    def flush(self):
        if self._file is not None:
            if self._readmode():
                self._readpos = self._file.tell()
            else:
                # subsequently need to append
                self._mode = 'a'
            self._file.close()
            self._file = None

    def close(self):
        if self._file is not None:
            self._file.close()
            self._file = None
        del self.__class__.pool[self]
