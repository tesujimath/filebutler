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

import os.path

from .FilesetCache import FilesetCache
from .Filter import Filter
from .util import debug_log

class DatasetFilesetCache(FilesetCache):

    def __init__(self, parent, path, deltadir, ctx, attrs, sel, next):
        super(self.__class__, self).__init__(parent, path, deltadir, ctx, attrs, sel, next)
        self._datasets = {}        # of fileset, indexed by dataset

        # load stubs for all datasets found
        if os.path.exists(self._path):
            for d in self.children():
                self._datasets[d] = None # stub

    def _fileset(self, d):
        """On demand creation of child filesets."""
        if d in self._datasets:
            fileset = self._datasets[d]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self, self._subpath(d), self._subdeltadir(d), self._ctx, self._attrs, self._sel.withDataset(d))
            self._datasets[d] = fileset
        return fileset

    def filtered(self, filter=None):
        datasets = sorted(self._datasets.keys())
        for d in datasets:
            if filter is None or filter.dataset is None or d == filter.dataset:
                yield self._fileset(d), Filter.clearDataset(filter)

    def create(self):
        """Create empty cache on disk, purging any previous."""
        #debug_log("DatasetFilesetCache creating at %s\n" % self._path)
        self.purge()
        self._datasets = {}

    def filesetFor(self, filespec):
        return self._fileset(filespec.dataset)
