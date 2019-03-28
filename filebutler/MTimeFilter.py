# Copyright 2017-2019 Simon Guest
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

from past.utils import old_div
import datetime
import fnmatch
import re

from .util import date2str, week_number

class MTimeFilter(object):

    def __init__(self, daystart, s):
        self.consistent = True
        self._after = True
        if len(s) > 1 and s[0] == '+':
            self._after = False
            s_n = s[1:]
        else:
            s_n = s
        self._epoch = daystart - int(s_n) * 60 * 60 * 24

    def intersect(self, f1):
        """Return a new filter which is the intersection of self with the parameter f1."""
        if f1 is None:
            return self
        if self._after != f1._after:
            self.consistent = False
            return self
        if self._after:
            self._epoch = max(self._epoch, f1._epoch)
        else:
            self._epoch = min(self._epoch, f1._epoch)

    def selects(self, mtime):
        if not self.consistent:
            return False
        if self._after:
            return mtime >= self._epoch
        else:
            return mtime < self._epoch

    def selects_week(self, w):
        """Return whether the filter intersects with the given week, and whether this is total containment."""
        w0 = week_number(self._epoch)
        intersects = w >= w0 if self._after else w <= w0
        contains = intersects and w0 != w
        return intersects, contains

    def __str__(self):
        return "%s:%s" % ("younger" if self._after else "older", date2str(self._epoch))
