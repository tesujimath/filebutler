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

from .Filter import Filter
from .FilesetCache import FilesetCache
from .PooledFile import listdir
from .util import verbose_stderr, debug_log

class WeeklyFilesetCache(FilesetCache):

    @classmethod
    def week(cls, t):
        """Return time t as an integer valued week YYYYWW."""
        dt = datetime.datetime.fromtimestamp(t)
        isoyear,isoweek,isoweekday = dt.isocalendar()
        return isoyear * 100 + isoweek

    def __init__(self, parent, path, deltadir, ctx, attrs, sel, next):
        super(self.__class__, self).__init__(parent, path, deltadir, ctx, attrs, sel, next)
        self._weeks = {}        # of fileset, indexed by integer week

        # load stubs for all weeks found
        if os.path.exists(self._path):
            for wstr in self.children():
                w = int(wstr)
                self._weeks[w] = None # stub

    def _fileset(self, w):
        """On demand creation of child filesets."""
        if w in self._weeks:
            fileset = self._weeks[w]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self, self._subpath(w), self._subdeltadir(w), self._ctx, self._attrs, self._sel)
            self._weeks[w] = fileset
        return fileset

    def filtered(self, filter=None):
        """Yield each child fileset and its filter."""
        weeks = sorted(self._weeks.keys())
        #debug_log("filtered(%s) with %d weeks to consider\n" % (self._path, len(weeks)))
        for w in weeks:
            #debug_log("filtered(%s) considering %s\n" % (self._path, str(w)))
            if filter is None or filter.mtimeBefore is None or w <= self.__class__.week(filter.mtimeBefore):
                if filter is not None and filter.mtimeBefore is not None and w < self.__class__.week(filter.mtimeBefore):
                    f1 = Filter.clearMtime(filter)
                else:
                    f1 = filter
                #debug_log("filtered(%s) yielding %s\n" % (self._path, str(w)))
                yield self._fileset(w), f1

    def create(self):
        """Create empty cache on disk, purging any previous."""
        #debug_log("WeeklyFilesetCache creating at %s\n" % self._path)
        self.purge()
        self._weeks = {}

    def filesetFor(self, filespec):
        w = self.__class__.week(filespec.mtime)
        return self._fileset(w)
