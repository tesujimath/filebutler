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

from .Buckets import Buckets
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
        self._sizebuckets = Buckets([str2size(s) for s in self._attrs['sizebuckets']] if 'sizebuckets' in self._attrs else [])
        self._filesets = [None] * self._sizebuckets.len

    def _subpath(self, b):
        return os.path.join(self._path, str(b))

    def _subdeltadir(self, b):
        return os.path.join(self._deltadir, str(b))

    def _fileset(self, i):
        """On demand creation of child filesets."""
        b = self._sizebuckets.bound(i)
        fileset = self._filesets[i]
        if fileset is None:
            fileset = self._next(self._subpath(b), self._subdeltadir(b), self._mapper, self._attrs, self._sel.withSizebucket(b))
            self._filesets[i] = fileset
        return fileset

    def select(self, filter=None):
        merger = FilespecMerger()
        for i in range(self._sizebuckets.len):
            minSize, maxSize = self._sizebuckets.minmax(i)
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

        for i in range(self._sizebuckets.len):
            minSize, maxSize = self._sizebuckets.minmax(i)
            if filter is None or filter.sizeGeq is None or maxSize is None or maxSize >= filter.sizeGeq:
                if filter is not None and filter.sizeGeq is not None and minSize >= filter.sizeGeq:
                    f1 = Filter.clearSize(filter)
                else:
                    f1 = filter
                self._fileset(i).merge_info(acc, f1)

    def add(self, filespec):
        fileset = self._fileset(self._sizebuckets.indexContaining(filespec.size))
        fileset.add(filespec)

    def finalize(self):
        for fs in self._filesets:
            if fs is not None:
                fs.finalize()

    def saveDeletions(self):
        #debug_log("SizeFilesetCache(%s)::saveDeletions\n" % self._path)
        for fs in self._filesets:
            if fs is not None:
                fs.saveDeletions()
