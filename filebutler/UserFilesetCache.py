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
from FilespecMerger import FilespecMerger
from PooledFile import listdir
from util import debug_log

class UserFilesetCache(object):

    def __init__(self, path, deltadir, attrs, sel, next):
        self._path = path
        self._deltadir = deltadir
        self._attrs = attrs
        self._sel = sel
        self._next = next
        self._users = {}        # of fileset, indexed by integer user

        # load stubs for all users found
        if os.path.exists(self._path):
            for u in listdir(self._path):
                self._users[u] = None # stub

    def _subpath(self, u):
        return os.path.join(self._path, u)

    def _subdeltadir(self, u):
        return os.path.join(self._deltadir, u)

    def _fileset(self, u):
        """On demand creation of child filesets."""
        if self._users.has_key(u):
            fileset = self._users[u]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(u), self._subdeltadir(u), self._attrs, self._sel.withOwner(u))
            self._users[u] = fileset
        return fileset

    def select(self, filter=None):
        merger = FilespecMerger()
        users = sorted(self._users.keys())
        for u in users:
            if filter is None or filter.owner is None or u == filter.owner:
                merger.add(self._fileset(u).select(Filter.clearOwner(filter)))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        #debug_log("UserFilesetCache(%s) merge_info\n" % self._path)
        for u in self._users.keys():
            if filter is None or filter.owner is None or u == filter.owner:
                self._fileset(u).merge_info(acc, Filter.clearOwner(filter))

    def add(self, filespec):
        fileset = self._fileset(filespec.user)
        fileset.add(filespec)

    def finalize(self):
        for u in self._users.itervalues():
            if u is not None:
                u.finalize()

    def saveDeletions(self):
        #debug_log("UserFilesetCache(%s)::saveDeletions\n" % self._path)
        for u in self._users.itervalues():
            if u is not None:
                u.saveDeletions()
