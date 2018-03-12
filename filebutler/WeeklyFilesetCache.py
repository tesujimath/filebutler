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
from builtins import object
import datetime
import os.path
import re
import shutil

from .Filter import Filter
from .FilespecMerger import FilespecMerger
from .PooledFile import listdir
from .util import verbose_stderr, debug_log

class WeeklyFilesetCache(object):

    @classmethod
    def week(cls, t):
        """Return time t as an integer valued week YYYYWW."""
        dt = datetime.datetime.fromtimestamp(t)
        isoyear,isoweek,isoweekday = dt.isocalendar()
        return isoyear * 100 + isoweek

    def __init__(self, path, deltadir, mapper, attrs, sel, next):
        self._path = path
        self._deltadir = deltadir
        self._mapper = mapper
        self._attrs = attrs
        self._sel = sel
        self._next = next
        self._weeks = {}        # of fileset, indexed by integer week

        # load stubs for all weeks found
        if os.path.exists(self._path):
            for wstr in listdir(self._path):
                w = int(wstr)
                self._weeks[w] = None # stub

    def _subpath(self, w):
        return os.path.join(self._path, str(w))

    def _subdeltadir(self, w):
        return os.path.join(self._deltadir, str(w))

    def _fileset(self, w):
        """On demand creation of child filesets."""
        if w in self._weeks:
            fileset = self._weeks[w]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(w), self._subdeltadir(w), self._mapper, self._attrs, self._sel)
            self._weeks[w] = fileset
        return fileset

    def select(self, filter=None):
        merger = FilespecMerger()
        weeks = sorted(self._weeks.keys())
        for w in weeks:
            if filter is None or filter.mtimeBefore is None or w <= self.__class__.week(filter.mtimeBefore):
                if filter is not None and filter.mtimeBefore is not None and w < self.__class__.week(filter.mtimeBefore):
                    f1 = Filter.clearMtime(filter)
                else:
                    f1 = filter
                merger.add(self._fileset(w).select(f1))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        #debug_log("WeeklyFilesetCache(%s) merge_info\n" % self._path)
        for w in list(self._weeks.keys()):
            if filter is None or filter.mtimeBefore is None or w <= self.__class__.week(filter.mtimeBefore):
                if filter is not None and filter.mtimeBefore is not None and w < self.__class__.week(filter.mtimeBefore):
                    f1 = Filter.clearMtime(filter)
                else:
                    f1 = filter
                self._fileset(w).merge_info(acc, f1)

    def create(self):
        """Create empty cache on disk, purging any previous."""
        #debug_log("WeeklyFilesetCache creating at %s\n" % self._path)
        if os.path.exists(self._path):
            # Purge existing cache.
            # For safety in case of misconfiguration, we only delete directories in the format YYYYWW
            YYYYWW = re.compile(r"""^\d\d\d\d\d\d$""")
            for x in listdir(self._path):
                px = os.path.join(self._path, x)
                if YYYYWW.match(x):
                    shutil.rmtree(px)
                else:
                    verbose_stderr("WARNING: cache purge ignoring %s\n" % px)
        else:
            os.makedirs(self._path)
        self._weeks = {}

    def add(self, filespec):
        w = self.__class__.week(filespec.mtime)
        fileset = self._fileset(w)
        fileset.add(filespec)

    def finalize(self):
        for w in self._weeks.values():
            if w is not None:
                w.finalize()

    def saveDeletions(self):
        #debug_log("WeeklyFilesetCache(%s)::saveDeletions\n" % self._path)
        for w in self._weeks.values():
            if w is not None:
                w.saveDeletions()
