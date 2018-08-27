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

from .FilesetInfoAccumulator import FilesetInfoAccumulator
from .FilesetSelector import FilesetSelector

class Fileset(object):
    """Fileset is a base class."""

    def __init__(self):
        pass

    def info(self, attrs, filter=None):
        acc = FilesetInfoAccumulator(attrs)
        self.merge_info(acc, filter)
        return acc

    def sorted(self, filter=None, sorter=None):
        if sorter is None:
            for filespec in self.select(filter):
                yield filespec
        else:
            filespecs = []
            for filespec in self.select(filter):
                filespecs.append(filespec)
            filespecs.sort(key=sorter.key())
            for filespec in filespecs:
                yield filespec

    def delete(self, filespec):
        pass
