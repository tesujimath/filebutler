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

import time

from Filespec import Filespec
from Filter import Filter

class FilterFileset(object):

    @classmethod
    def parse(cls, fileset, toks):
        owner = None
        sizeGeq = None
        mtimeBefore = None
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
                    n = int(size[:-1]) * 1073741824 # from manpage for find
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
                mtimeBefore = time.time() - n * 60 * 60 * 24
                i += 1
            else:
                raise CLIError("unknown filter parameter %s" % tok)
            i += 1

        filter = Filter(owner=owner, sizeGeq=sizeGeq, mtimeBefore=mtimeBefore)
        #print("parsed filter %s" % filter)
        return cls(fileset, filter)

    def __init__(self, fileset, filter):
        self._fileset = fileset
        self._filter = filter

    def select(self, filter=None):
        f1 = self._filter.intersect(filter)
        for filespec in self._fileset.select(f1):
            yield filespec
