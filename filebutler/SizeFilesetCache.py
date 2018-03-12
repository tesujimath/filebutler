from __future__ import absolute_import
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

from builtins import str
from builtins import range
from builtins import object
import datetime
import os.path
import re
import shutil

from .Filter import Filter
from .FilespecMerger import FilespecMerger
from .PooledFile import listdir
from .util import str2size, verbose_stderr, debug_log

class SizeFilesetCache(object):

    def __init__(self, path, deltadir, mapper, attrs, sel, next):
        self._path = path
        self._deltadir = deltadir
        self._mapper = mapper
        self._attrs = attrs
        self._sel = sel
        self._next = next
        self._initializeBuckets()

    def _initializeBuckets(self):
        self._sizes = [0]
        self._buckets = [None]
        if 'sizebuckets' in self._attrs:
            for sizestr in self._attrs['sizebuckets']:
                self._addBucket(str2size(sizestr))

    def _addBucket(self, size):
        for i in range(len(self._sizes)):
            if size == self._sizes[i]:
                # already present, do nothing
                return
            elif size < self._sizes[i]:
                self._sizes.insert(i, size)
                self._buckets.insert(i, None) # stub
                return
        self._sizes.append(size)
        self._buckets.append(None) # stub

    def _subpath(self, w):
        return os.path.join(self._path, str(w))

    def _subdeltadir(self, w):
        return os.path.join(self._deltadir, str(w))

    def _slot(self, w):
        """Return slot for a given filesize."""
        for i in reversed(list(range(len(self._sizes)))):
            if w >= self._sizes[i]:
                return i
        raise ValueError("no slot found for size %d, %s" % (w, str(self._sizes)))

    def _fileset(self, i):
        """On demand creation of child filesets."""
        w = self._sizes[i]
        fileset = self._buckets[i]
        if fileset is None:
            fileset = self._next(self._subpath(w), self._subdeltadir(w), self._mapper, self._attrs, self._sel)
            self._buckets[i] = fileset
        return fileset

    def select(self, filter=None):
        merger = FilespecMerger()
        for i in range(len(self._sizes)):
            minSize = self._sizes[i]
            maxSize = self._sizes[i + 1] - 1 if i < len(self._sizes) - 1 else None
            if filter is None or filter.sizeGeq is None or maxSize is None or maxSize >= filter.sizeGeq:
                if filter is not None and filter.sizeGeq is not None and minSize >= filter.sizeGeq:
                    f1 = Filter.clearSize(filter)
                else:
                    f1 = filter
                merger.add(self._fileset(i).select(f1))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        #debug_log("SizeFilesetCache(%s) merge_info\n" % self._path)

        for i in range(len(self._sizes)):
            minSize = self._sizes[i]
            maxSize = self._sizes[i + 1] - 1 if i < len(self._sizes) - 1 else None
            if filter is None or filter.sizeGeq is None or maxSize is None or maxSize >= filter.sizeGeq:
                if filter is not None and filter.sizeGeq is not None and minSize >= filter.sizeGeq:
                    f1 = Filter.clearSize(filter)
                else:
                    f1 = filter
                self._fileset(i).merge_info(acc, f1)

    def add(self, filespec):
        fileset = self._fileset(self._slot(filespec.size))
        fileset.add(filespec)

    def finalize(self):
        for b in self._buckets:
            if b is not None:
                b.finalize()

    def saveDeletions(self):
        #debug_log("SizeFilesetCache(%s)::saveDeletions\n" % self._path)
        for b in self._buckets:
            if b is not None:
                b.saveDeletions()
