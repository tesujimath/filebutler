# Copyright 2017 Simon Guest
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

from util import time2str

def liberal(fn, a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return fn(a, b)

class Filter(object):
    def __init__(self, owner=None, sizeGeq=None, mtimeBefore=None):
        self.owner = owner
        self.sizeGeq = sizeGeq
        self.mtimeBefore = mtimeBefore

    def __str__(self):
        if self.owner is not None:
            owner = self.owner
        else:
            owner = '*'
        if self.sizeGeq is not None:
            sizeGeq = "%d" % self.sizeGeq
        else:
            sizeGeq = '*'
        if self.mtimeBefore is not None:
            mtimeBefore = time2str(self.mtimeBefore)
        else:
            mtimeBefore = '*'
        return "owner:%s,size:%s,mtime:%s" % (owner, sizeGeq, mtimeBefore)

    def intersect(self, filter):
        """Return a new filter which is the intersection of self with the parameter filter."""
        if filter is None:
            return self

        if self.owner is None:
            owner = filter.owner
        elif filter.owner is not None:
            if self.owner == filter.owner:
                owner = self.owner
            else:
                # incompatible, so set to something impossible, which we test for in selects()
                owner = "%s+%s" % (self.owner, filter.owner)
        else:
            owner = None
        sizeGeq = liberal(max, self.sizeGeq, filter.sizeGeq)
        mtimeBefore = liberal(min, self.mtimeBefore, filter.mtimeBefore)
        return self.__class__(owner, sizeGeq, mtimeBefore)

    def selects(self, filespec):
        if self.owner is not None and '+' in self.owner:
            return False
        if self.owner is not None and filespec.user != self.owner:
            return False
        if self.sizeGeq is not None and filespec.size < self.sizeGeq:
            return False
        if self.mtimeBefore is not None and filespec.mtime >= self.mtimeBefore:
            return False
        return True
