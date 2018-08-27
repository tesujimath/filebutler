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
import subprocess

class Pager(object):

    def __init__(self):
        if 'PAGER' in os.environ:
            pager = os.environ['PAGER']
        else:
            pager = 'less'
        self._pager = subprocess.Popen(pager, stdin=subprocess.PIPE, universal_newlines=True)
        self.file = self._pager.stdin

    def close(self, force=False):
        try:
            self.file.close()
        except:
            # we don't care what happens here, but most likely it's a broken pipe
            pass
        if force:
            self._pager.terminate()
        self._pager.wait()
