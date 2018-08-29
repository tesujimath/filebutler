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
from .FilespecMerger import FilespecMerger

class UnionFileset(Fileset):

    def __init__(self, name, filesets):
        self.name = name
        self._filesets = filesets

    def description(self):
        return "%s union %s" % (self.name, ' '.join(sorted([fileset.name for fileset in self._filesets])))

    def select(self, filter=None):
        merger = FilespecMerger()
        for fileset in self._filesets:
            merger.add(fileset.select(filter))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        for fileset in self._filesets:
            fileset.merge_info(acc, filter)

    def getCaches(self, caches):
        for fileset in self._filesets:
            fileset.getCaches(caches)
