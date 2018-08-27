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

import calendar
import os
import time

from .util import fbTimeFmt, time2str, date2str, size2str

class FilespecMerger(object):
    """Merge filespecs from multiple iterators in order of path."""

    def __init__(self):
        self._iters = []

    def add(self, iter):
        """Add an iterator, to be merged in with the others."""
        self._iters.append(iter)

    def merge(self):
        """Yield from all the iterators in order."""
        # get initial value for each iterator
        values = []
        for iter in self._iters:
            try:
                value = next(iter)
            except StopIteration:
                value = None
            values.append(value)

        # merge least value each time until done
        done = False
        while not done:
            # find min value
            min_i = None
            for i in range(len(values)):
                if values[i] is not None and (min_i is None or values[i].path < values[min_i].path):
                    min_i = i

            if min_i is not None:
                yield values[min_i]
                # get next value for iterator which returned this one
                try:
                    values[min_i] = next(self._iters[min_i])
                except StopIteration:
                    values[min_i] = None
            else:
                done = True
