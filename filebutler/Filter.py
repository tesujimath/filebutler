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
import datetime
import fnmatch
import re

from .util import Giga, date2str, debug_log

def liberal(fn, a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return fn(a, b)

class Filter(object):

    @classmethod
    def clearOwner(cls, f0):
        """Return a copy of f0 with no owner specified, or None if f0 is None."""
        if f0 is None or f0.dataset is None and f0.sizeGeq is None and f0.mtimeBefore is None and f0.notPaths == [] and f0.regex is None:
            return None
        else:
            return cls(None, f0.dataset, f0.sizeGeq, f0.mtimeBefore, f0.notPaths, f0.regex)

    @classmethod
    def clearDataset(cls, f0):
        """Return a copy of f0 with no dataset specified, or None if f0 is None."""
        if f0 is None or f0.owner is None and f0.sizeGeq is None and f0.mtimeBefore is None and f0.notPaths == [] and f0.regex is None:
            return None
        else:
            return cls(f0.owner, None, f0.sizeGeq, f0.mtimeBefore, f0.notPaths, f0.regex)

    @classmethod
    def clearMtime(cls, f0):
        """Return a copy of f0 with no mtime specified, or None if f0 is None."""
        if f0 is None or f0.owner is None and f0.dataset is None and f0.sizeGeq is None and f0.notPaths == [] and f0.regex is None:
            return None
        else:
            return cls(f0.owner, f0.dataset, f0.sizeGeq, None, f0.notPaths, f0.regex)

    @classmethod
    def clearSize(cls, f0):
        """Return a copy of f0 with no size specified, or None if f0 is None."""
        if f0 is None or f0.owner is None and f0.dataset is None and f0.mtimeBefore is None and f0.notPaths == [] and f0.regex is None:
            return None
        else:
            return cls(f0.owner, f0.dataset, None, f0.mtimeBefore, f0.notPaths, f0.regex)

    def __init__(self, owner=None, dataset=None, sizeGeq=None, mtimeBefore=None, notPaths=[], regex=None):
        self.owner = owner
        self.dataset = dataset
        self.sizeGeq = sizeGeq
        self.mtimeBefore = mtimeBefore
        self.notPaths = notPaths
        self.regex = regex
        self.regexC = re.compile(self.regex) if self.regex is not None else None

    def __str__(self):
        s = ""
        def append(s0, s1):
            if len(s0) > 0:
                return s0 + ',' + s1
            else:
                return s1
        if self.owner is not None:
            s = append(s, "owner:%s" % self.owner)
        if self.dataset is not None:
            s = append(s, "dataset:%s" % self.dataset)
        if self.sizeGeq is not None:
            s = append(s, "size:+%dG" % (old_div(self.sizeGeq, Giga)))
        if self.mtimeBefore is not None:
            s = append(s, "older:%s" % date2str(self.mtimeBefore))
        if len(self.notPaths) > 0:
            s = append(s, "!paths:%s" % str(self.notPaths))
        if self.regex is not None:
            s = append(s, "regex:%s" % self.regex)
        return s

    def intersect(self, f1):
        """Return a new filter which is the intersection of self with the parameter f1."""
        if f1 is None:
            return self

        if self.owner is None:
            owner = f1.owner
        elif f1.owner is not None:
            if self.owner == f1.owner:
                owner = self.owner
            else:
                # incompatible, so set to something impossible, which we test for in selects()
                owner = "%s+%s" % (self.owner, f1.owner)
        else:
            owner = self.owner
        if self.dataset is None:
            dataset = f1.dataset
        elif f1.dataset is not None:
            if self.dataset == f1.dataset:
                dataset = self.dataset
            else:
                # incompatible, so set to something impossible, which we test for in selects()
                dataset = '/'
        else:
            dataset = self.dataset
        sizeGeq = liberal(max, self.sizeGeq, f1.sizeGeq)
        mtimeBefore = liberal(min, self.mtimeBefore, f1.mtimeBefore)
        notPaths = self.notPaths + f1.notPaths
        regex = self.regex if f1.regex is None else f1.regex if self.regex is None else "(?=%s)(?=%s)" % (self.regex, f1.regex)
        f2 = self.__class__(owner, dataset, sizeGeq, mtimeBefore, notPaths, regex)
        #debug_log("Filter(%s).intersect(%s)=%s\n" % (self, f1, f2))
        return f2

    def selects(self, filespec):
        if self.owner is not None and '+' in self.owner:
            return False
        if self.owner is not None and filespec.user != self.owner:
            return False
        if self.dataset == '/':
            return False
        if self.dataset is not None and filespec.dataset != self.dataset:
            return False
        if self.sizeGeq is not None and filespec.size < self.sizeGeq:
            return False
        if self.mtimeBefore is not None and filespec.mtime >= self.mtimeBefore:
            return False
        if len(self.notPaths) > 0:
            for notPath in self.notPaths:
                if fnmatch.fnmatchcase(filespec.path, notPath):
                    return False
        if self.regex is not None and not re.search(self.regexC, filespec.path):
            return False
        #debug_log("%s selects %s\n" % (self, filespec.path))
        return True
