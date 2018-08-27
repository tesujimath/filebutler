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

from copy import copy

from .FilesetInfo import FilesetInfo
from .Filespec import Filespec

class Grouper(object):

    def __init__(self, collapse=None):
        self._collapse = collapse
        self._collapsing = None

    def setOutput(self, f):
        self._f = f
        self._width = 0

    def _collapsed(self, path):
        n = self._collapse
        slash = path.find('/')
        while slash >= 0 and n > 0:
            slash = path.find('/', slash + 1)
            n -= 1
        if slash >= 0:
            return path[:slash]
        else:
            return path

    def _writeFilespec(self, filespec):
        s, self._width = filespec.format(self._width)
        self._f.write("%s\n" % s)

    def write(self, filespec):
        if self._collapse is None:
            self._writeFilespec(filespec)
        else:
            p = self._collapsed(filespec.path)
            if self._collapsing is None or p != self._collapsing.path:
                if self._collapsing is not None:
                    self._writeFilespec(self._collapsing)
                self._collapsing = copy(filespec)
                self._collapsing.path = p
                self._collapsing.perms = 'd' + self._collapsing.perms[1:]
            self._collapsing.size += filespec.size

    def flush(self):
        if self._collapse is not None and self._collapsing is not None:
            self._writeFilespec(self._collapsing)
