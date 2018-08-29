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

from .Fileset import Fileset
from .Filter import Filter
from .util import debug_log

class FilterFileset(Fileset):

    def __init__(self, name, fileset, filter):
        #debug_log("FilterFileset(%s), filter=%s\n" % (name, filter))
        self.name = name
        self._fileset = fileset
        self._filter = filter

    def description(self):
        return "%s filter %s %s" % (self.name, self._fileset.name, self._filter)

    def select(self, filter=None):
        f1 = self._filter.intersect(filter)
        #debug_log("FilterFileset(%s)::select filter=%s\n" % (self.name, f1))
        for filespec in self._fileset.select(f1):
            yield filespec

    def merge_info(self, acc, filter=None):
        f1 = self._filter.intersect(filter)
        #debug_log("FilterFileset(%s)::select filter=%s\n" % (self.name, f1))
        self._fileset.merge_info(acc, f1)

    def getCaches(self, caches):
        self._fileset.getCaches(caches)
