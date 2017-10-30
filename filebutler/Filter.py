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
import fnmatch

from CLIError import CLIError
from util import Giga, time2str, debug_stderr

def liberal(fn, a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return fn(a, b)

class Filter(object):

    @classmethod
    def parse(cls, now, toks):
        owner = None
        sizeGeq = None
        mtimeBefore = None
        notPaths = []
        i = 0
        while i < len(toks):
            tok = toks[i]
            if tok == '-user':
                if i + 1 >= len(toks):
                    raise CLIError("-user missing parameter")
                if owner is not None:
                    raise CLIError("duplicate -user")
                owner = toks[i + 1]
                i += 1
            elif tok == '-size':
                if i + 1 >= len(toks):
                    raise CLIError("-size missing parameter")
                size = toks[i + 1]
                if len(size) < 2 or size[-1] != 'G':
                    raise CLIError("-size only supports +nG format")
                try:
                    n = int(size[:-1]) * Giga
                except ValueError:
                    raise CLIError("-size only supports +nG format")
                if sizeGeq is not None:
                    raise CLIError("duplicate -size")
                sizeGeq = n
                i += 1
            elif tok == '-mtime':
                if i + 1 >= len(toks):
                    raise CLIError("-mtime missing parameter")
                mtime = toks[i + 1]
                if len(mtime) < 2 or mtime[0] != '+':
                    raise CLIError("-mtime only supports +n format")
                try:
                    n = int(mtime[1:])
                except ValueError:
                    raise CLIError("-mtime only supports +n format")
                if mtimeBefore is not None:
                    raise CLIError("duplicate -mtime")
                mtimeBefore = now - n * 60 * 60 * 24
                i += 1
            elif tok == '!':
                # only for -path
                if i + 2 >= len(toks) or toks[i + 1] != '-path':
                    raise CLIError("! requires -path <glob>")
                notPaths.append(toks[i + 2])
                i += 2
            else:
                raise CLIError("unknown filter parameter %s" % tok)
            i += 1

        return cls(owner=owner, sizeGeq=sizeGeq, mtimeBefore=mtimeBefore, notPaths=notPaths)

    def __init__(self, owner=None, sizeGeq=None, mtimeBefore=None, notPaths=[]):
        self.owner = owner
        self.sizeGeq = sizeGeq
        self.mtimeBefore = mtimeBefore
        self.notPaths = notPaths

    def __str__(self):
        if self.owner is not None:
            owner = self.owner
        else:
            owner = ''
        if self.sizeGeq is not None:
            sizeGeq = "%d" % self.sizeGeq
        else:
            sizeGeq = ''
        if self.mtimeBefore is not None:
            mtimeBefore = time2str(self.mtimeBefore)
        else:
            mtimeBefore = ''
        notPaths = str(self.notPaths)
        return "owner:%s,size:%s,mtime:%s,!path:%s" % (owner, sizeGeq, mtimeBefore, notPaths)

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
        sizeGeq = liberal(max, self.sizeGeq, f1.sizeGeq)
        mtimeBefore = liberal(min, self.mtimeBefore, f1.mtimeBefore)
        notPaths = self.notPaths + f1.notPaths
        f2 = self.__class__(owner, sizeGeq, mtimeBefore, notPaths)
        debug_stderr("Filter(%s).intersect(%s)=%s\n" % (self, f1, f2))
        return f2

    def selects(self, filespec):
        if self.owner is not None and '+' in self.owner:
            return False
        if self.owner is not None and filespec.user != self.owner:
            return False
        if self.sizeGeq is not None and filespec.size < self.sizeGeq:
            return False
        if self.mtimeBefore is not None and filespec.mtime >= self.mtimeBefore:
            return False
        if len(self.notPaths) > 0:
            for notPath in self.notPaths:
                if fnmatch.fnmatchcase(filespec.path, notPath):
                    return False
        #debug_stderr("%s selects %s\n" % (self, filespec.path))
        return True
