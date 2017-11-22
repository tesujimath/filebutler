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

import errno
import os
import os.path
import re
import readline
import shlex
import string
import time

from CLIError import CLIError
from Filter import Filter
from Sorter import Sorter
from util import Giga

def parseCommandOptions(now, toks, filter=False, sorter=False):
    """Parse filter and/or sorter options."""

    # filter options
    owner = None
    sizeGeq = None
    mtimeBefore = None
    notPaths = []

    # sorter options
    bySize = False

    i = 0
    while i < len(toks):
        tok = toks[i]
        if tok == '-user' and filter:
            if i + 1 >= len(toks):
                raise CLIError("-user missing parameter")
            if owner is not None:
                raise CLIError("duplicate -user")
            owner = toks[i + 1]
            i += 1
        elif tok == '-size' and filter:
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
        elif tok == '-mtime' and filter:
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
        elif tok == '!' and filter:
            # only for -path
            if i + 2 >= len(toks) or toks[i + 1] != '-path':
                raise CLIError("! requires -path <glob>")
            notPaths.append(toks[i + 2])
            i += 2
        elif tok == '-by-size' and sorter:
            bySize = True
        else:
            category = ""
            if filter and not sorter:
                category = "filter "
            if sorter and not filter:
                category = "sorter "
            raise CLIError("unknown %sparameter %s" % (category, tok))
        i += 1

    if filter and (owner is not None or sizeGeq is not None or mtimeBefore is not None or notPaths != []):
        f0 = Filter(owner=owner, sizeGeq=sizeGeq, mtimeBefore=mtimeBefore, notPaths=notPaths)
    else:
        f0 = None
    if sorter and bySize:
        s0 = Sorter(bySize=True)
    else:
        s0 = None

    return f0, s0
