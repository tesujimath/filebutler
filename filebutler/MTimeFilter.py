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

import datetime
import fnmatch
import re

from .util import date2str, week_number, liberal

class MTimeFilter(object):

    @classmethod
    def age(cls, daystart, s, isAfter):
        """Return a new MTimeFilter selecting before/after the given age."""
        epoch = daystart - int(s) * 60 * 60 * 24
        if isAfter:
            return cls(after=epoch)
        else:
            return cls(before=epoch)

    def __init__(self, before=None, after=None):
        self.consistent = before is None or after is None or before > after
        self._before = before
        self._after = after

    def intersect(self, f1):
        """Return a new filter which is the intersection of self with the parameter f1."""
        if f1 is None:
            return self
        else:
            return self.__class__(before=liberal(min, self._before, f1._before),
                                  after=liberal(max, self._after, f1._after))

    def selects(self, mtime):
        if not self.consistent:
            return False
        if self._before is not None and mtime >= self._before:
            return False
        if self._after is not None and mtime < self._after:
            return False
        return True

    def selects_week(self, w):
        """Return whether the filter intersects with the given week, and whether this is total containment."""
        if self._before is not None:
            wBefore = week_number(self._before)
            intersects = w <= wBefore
            contains = intersects and wBefore != w
        else:
            intersects = True
            contains = True
        if intersects:
            if self._after is not None:
                wAfter = week_number(self._after)
                intersects = w >= wAfter
                contains = contains and intersects and wAfter != w
        return intersects, contains

    def __str__(self):
        if self._before is not None:
            selectors = [ "%s:%s" % ("older", date2str(self._before)) ]
        else:
            selectors = []
        if self._after is not None:
            selectors.append("%s:%s" % ("younger", date2str(self._after)))
        return ','.join(selectors) if selectors else "anytime"
