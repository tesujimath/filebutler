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

from Filter import Filter
from util import debug_stderr

class DatasetFilesetCache(object):

    def __init__(self, path, logdir, next):
        self._path = path
        self._logdir = logdir
        self._next = next
        self._datasets = {}        # of fileset, indexed by dataset

        # load stubs for all datasets found
        if os.path.exists(self._path):
            for d in os.listdir(self._path):
                self._datasets[d] = None # stub

    def _subpath(self, d):
        return os.path.join(self._path, d)

    def _sublogdir(self, d):
        return os.path.join(self._logdir, d)

    def _fileset(self, d):
        """On demand creation of child filesets."""
        if self._datasets.has_key(d):
            fileset = self._datasets[d]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(d), self._sublogdir(d))
            self._datasets[d] = fileset
        return fileset

    def select(self, filter=None):
        datasets = sorted(self._datasets.keys())
        for d in datasets:
            if filter is None or filter.owner is None or d == filter.owner:
                # no yield from in python 2, so:
                for filespec in self._fileset(d).select(Filter.clearOwner(filter)):
                    yield filespec

    def merge_info(self, acc, sel, filter=None):
        for d in self._datasets.keys():
            if filter is None or filter.owner is None or d == filter.owner:
                self._fileset(d).merge_info(acc, sel.withDataset(d), Filter.clearOwner(filter))

    def create(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)

    def add(self, filespec):
        fileset = self._fileset(filespec.dataset)
        fileset.add(filespec)

    def flush(self):
        for fileset in self._datasets.values():
            fileset.flush()

    def writeInfo(self):
        for d in self._datasets.itervalues():
            if d is not None:
                d.writeInfo()

    def saveDeletions(self):
        #debug_stderr("DatasetFilesetCache(%s)::saveDeletions\n" % self._path)
        for d in self._datasets.itervalues():
            if d is not None:
                d.saveDeletions()
