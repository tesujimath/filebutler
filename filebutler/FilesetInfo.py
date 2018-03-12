from __future__ import absolute_import
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

from builtins import object
from .util import size2str, warning

class FilesetInfo(object):

    @classmethod
    def fromFile(cls, f):
        fi = None
        for line in f:
            try:
                fields = line.rstrip().split(None)
                if fi is None and len(fields) == 2:
                    nFiles = int(fields[0])
                    totalSize = int(fields[1])
                    fi = cls(nFiles, totalSize)
                else:
                    raise ValueError
            except ValueError:
                warning("ignoring bad info line: %s" % line.rstrip())
        return fi

    def __init__(self, nFiles=0, totalSize=0):
        self.nFiles = nFiles
        self.totalSize = totalSize

    def add(self, nFiles, totalSize):
        self.nFiles += nFiles
        self.totalSize += totalSize

    def remove(self, nFiles, totalSize):
        self.nFiles -= nFiles
        self.totalSize -= totalSize

    def __str__(self):
        return "%s in %d files" % (size2str(self.totalSize), self.nFiles)

    def write(self, f):
        f.write("%d %d\n" % (self.nFiles, self.totalSize))
