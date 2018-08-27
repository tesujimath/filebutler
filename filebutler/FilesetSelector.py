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

class FilesetSelector(object):

    def __init__(self, owner=None, dataset=None, sizebucket=None):
        self.owner = owner
        self.dataset = dataset
        self.sizebucket = sizebucket

    def withOwner(self, owner):
        return self.__class__(owner, self.dataset, self.sizebucket)

    def withDataset(self, dataset):
        return self.__class__(self.owner, dataset, self.sizebucket)

    def withSizebucket(self, sizebucket):
        return self.__class__(self.owner, self.dataset, sizebucket)
