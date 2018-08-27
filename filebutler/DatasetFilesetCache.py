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

from builtins import object
import os.path

from .FilesetCache import FilesetCache
from .Filter import Filter
from .PooledFile import listdir
from .util import debug_log

class DatasetFilesetCache(FilesetCache):

    def __init__(self, path, deltadir, mapper, attrs, sel, next):
        super(self.__class__, self).__init__(path, deltadir, mapper, attrs, sel, next)
        self._datasets = {}        # of fileset, indexed by dataset

        # load stubs for all datasets found
        if os.path.exists(self._path):
            for d in listdir(self._path):
                self._datasets[d] = None # stub

    def _subpath(self, d):
        return os.path.join(self._path, d)

    def _subdeltadir(self, d):
        return os.path.join(self._deltadir, d)

    def _fileset(self, d):
        """On demand creation of child filesets."""
        if d in self._datasets:
            fileset = self._datasets[d]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(d), self._subdeltadir(d), self._mapper, self._attrs, self._sel.withDataset(d))
            self._datasets[d] = fileset
        return fileset

    def filtered(self, filter=None):
        datasets = sorted(self._datasets.keys())
        for d in datasets:
            if filter is None or filter.dataset is None or d == filter.dataset:
                yield self._fileset(d), Filter.clearDataset(filter)

    def filesetFor(self, filespec):
        return self._fileset(filespec.dataset)
