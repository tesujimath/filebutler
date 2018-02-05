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

from FilesetInfo import FilesetInfo

class Grouper(object):

    def __init__(self, collapse=None):
        self._collapse = collapse
        self._collapsingPath = None
        self._collapsingInfo = None

    def setOutput(self, f):
        self._f = f
        self._width = 0

    def _collapsed(self, path):
        n = self._collapse
        slash = path.find('/')
        while slash >= 0 and n > 0:
            slash = path.find('/', slash + 1)
            n -= 1
        if slash >= 0:
            return path[:slash + 1]
        else:
            return path

    def _formatPath(self, path):
        if self._width < 50:
            self._width = 50
        if len(path) > self._width:
            self._width = (len(path) / 10 + 1) * 10
        s = ("%-" + str(self._width) + "s") % path
        return s

    def write(self, filespec):
        if self._collapse is None:
            s, self._width = filespec.format(self._width)
            self._f.write("%s\n" % s)
        else:
            p = self._collapsed(filespec.path)
            if p != self._collapsingPath:
                if self._collapsingPath is not None:
                    s = self._formatPath(self._collapsingPath)
                    self._f.write("%s %s\n" % (s, self._collapsingInfo))
                self._collapsingPath = p
                self._collapsingInfo = FilesetInfo()
            self._collapsingInfo.add(1, filespec.size)

    def flush(self):
        if self._collapse is not None and self._collapsingPath is not None:
            s = self._formatPath(self._collapsingPath)
            self._f.write("%s %s\n" % (s, self._collapsingInfo))
