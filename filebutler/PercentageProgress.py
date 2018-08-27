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

from past.utils import old_div
import math
import time

from .util import progress_stderr

class PercentageProgress(object):

    def __init__(self, prefix):
        self._fmt = "\r" + prefix + " [%.1f%% complete%s]"
        self._start = time.time()
        self._progress = -1
        self._maxlen = 0
        self.report(0)

    def report(self, p):
        """Report progress p, from 0 to 1."""
        if p - self._progress > 0.001:
            self._progress = p
            if p > 0:
                elapsed = time.time() - self._start
                t = max(math.floor(elapsed * 1.0 / p - elapsed), 0)
                m = old_div(t, 60)
                s = t % 60
                remaining = ", %d:%02d remaining" % (m, s)
            else:
                remaining = ""
            message = self._fmt % (p * 100, remaining)
            progress_stderr(message)
            if len(message) > self._maxlen:
                self._maxlen = len(message)

    def complete(self):
        progress_stderr("\r%s\r" % (' ' * self._maxlen))
