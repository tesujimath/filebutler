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


class Buckets(object):

    def __init__(self, bounds):
        self._bounds = [0]
        for b in bounds:
            self._insert(b)

    def _insert(self, b):
        for i in range(len(self._bounds)):
            if b == self._bounds[i]:
                # already present, do nothing
                return
            elif b < self._bounds[i]:
                self._bounds.insert(i, b)
                return
        self._bounds.append(b)

    def indexContaining(self, x):
        """Return slot containing a given value."""
        for i in reversed(list(range(len(self._bounds)))):
            if x >= self._bounds[i]:
                return i
        raise ValueError("no slot containing %d, %s" % (x, str(self._bounds)))

    def index(self, b):
        """Return slot for given bound."""
        for i in reversed(list(range(len(self._bounds)))):
            if b == self._bounds[i]:
                return i
        raise ValueError("no slot with bound %d, %s" % (b, str(self._bounds)))

    def bound(self, i):
        return self._bounds[i]

    def minmax(self, i):
        """Return (min, max), or None for max if this is the last bucket."""
        return self._bounds[i], (self._bounds[i + 1] - 1 if i < len(self._bounds) - 1 else None)

    @property
    def len(self):
        return len(self._bounds)
