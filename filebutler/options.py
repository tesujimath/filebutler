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

import os
import os.path
import re
import readline
import shlex
import time

from .CLIError import CLIError
from .Filter import Filter
from .Sorter import Sorter
from .Grouper import Grouper
from .util import str2size

def parseCommandOptions(now, toks, filter=False, sorter=False, grouper=False):
    """Parse filter and/or sorter options."""

    # filter options
    owner = None
    dataset = None
    sizeGeq = None
    mtimeBefore = None
    notPaths = []
    regex = None

    # sorter options
    bySize = False

    # grouper options
    collapse = None

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
        elif tok == '-dataset' and filter:
            if i + 1 >= len(toks):
                raise CLIError("-dataset missing parameter")
            if dataset is not None:
                raise CLIError("duplicate -dataset")
            dataset = toks[i + 1]
            i += 1
        elif tok == '-size' and filter:
            if i + 1 >= len(toks):
                raise CLIError("-size missing parameter")
            size = toks[i + 1]
            if len(size) < 2 or size[0] != '+':
                raise CLIError("-size only supports +n[kMGT] format")
            n = str2size(size[1:])
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
        elif tok == '-regex' and filter:
            if i + 1 >= len(toks):
                raise CLIError("-regex missing parameter")
            regex = toks[i + 1]
            # check the syntax
            try:
                regexC = re.compile(regex)
            except:
                raise CLIError("invalid regex %s" % regex)
            i += 1
        elif tok == '-by-size' and sorter:
            bySize = True
        elif tok == '-depth' and grouper:
            if i + 1 >= len(toks):
                raise CLIError("-depth missing parameter")
            try:
                collapse = int(toks[i + 1])
            except ValueError:
                raise CLIError("-depth requires integer parameter")
            i += 1
        else:
            category = ""
            if filter and not sorter and not grouper:
                category = "filter "
            if sorter and not filter and not grouper:
                category = "sorter "
            if grouper and not sorter and not filter:
                category = "grouper "
            raise CLIError("unknown %sparameter %s" % (category, tok))
        i += 1

    if filter and (owner is not None or dataset is not None or sizeGeq is not None or mtimeBefore is not None or notPaths != [] or regex is not None):
        f0 = Filter(owner=owner, dataset=dataset, sizeGeq=sizeGeq, mtimeBefore=mtimeBefore, notPaths=notPaths, regex=regex)
    else:
        f0 = None
    if sorter and bySize:
        s0 = Sorter(bySize=bySize)
    else:
        s0 = None
    if grouper:
        g0 = Grouper(collapse=collapse)
    else:
        g0 = None

    return f0, s0, g0
