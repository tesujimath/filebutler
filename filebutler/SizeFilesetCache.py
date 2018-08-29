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

import datetime
import os.path
import re

from .Buckets import Buckets
from .FilesetCache import FilesetCache
from .Filter import Filter
from .util import str2size, verbose_stderr, debug_log

class SizeFilesetCache(FilesetCache):

    def __init__(self, parent, path, deltadir, ctx, attrs, sel, next):
        super(self.__class__, self).__init__(parent, path, deltadir, ctx, attrs, sel, next)
        self._sizebuckets = Buckets([str2size(s) for s in self._attrs['sizebuckets']] if 'sizebuckets' in self._attrs else [])
        self._filesets = [None] * self._sizebuckets.len

    def _fileset(self, i):
        """On demand creation of child filesets."""
        b = self._sizebuckets.bound(i)
        fileset = self._filesets[i]
        if fileset is None:
            fileset = self._next(self, self._subpath(b), self._subdeltadir(b), self._ctx, self._attrs, self._sel.withSizebucket(b))
            self._filesets[i] = fileset
        return fileset

    def filtered(self, filter=None):
        for i in range(self._sizebuckets.len):
            minSize, maxSize = self._sizebuckets.minmax(i)
            if filter is None or filter.sizeGeq is None or maxSize is None or maxSize >= filter.sizeGeq:
                if filter is not None and filter.sizeGeq is not None and minSize >= filter.sizeGeq:
                    f1 = Filter.clearSize(filter)
                else:
                    f1 = filter
                yield self._fileset(i), f1

    def create(self):
        """Create empty cache on disk, purging any previous."""
        #debug_log("SizeFilesetCache creating at %s\n" % self._path)
        self.purge()
        self._filesets = [None] * self._sizebuckets.len

    def filesetFor(self, filespec):
        return self._fileset(self._sizebuckets.indexContaining(filespec.size))
