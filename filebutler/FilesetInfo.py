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

from util import size2str, warning
from UserInfo import UserInfo

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
                elif fi is not None and len(fields) == 3:
                    username = fields[0]
                    nFiles = int(fields[1])
                    totalSize = int(fields[2])
                    fi._users[username] = UserInfo(nFiles, totalSize)
                else:
                    raise ValueError
            except ValueError:
                warning("ignoring bad info line: %s" % line.rstrip())
        return fi

    def __init__(self, nFiles=0, totalSize=0):
        self.nFiles = nFiles
        self.totalSize = totalSize
        self._users = {}

    def add(self, filespec):
        self.nFiles += 1
        self.totalSize += filespec.size
        if self._users.has_key(filespec.user):
            user = self._users[filespec.user]
        else:
            user = UserInfo()
            self._users[filespec.user] = user
        user.add(1, filespec.size)

    def merge(self, inf1):
        self.nFiles += inf1.nFiles
        self.totalSize += inf1.totalSize
        for u in inf1._users.keys():
            user1 = inf1._users[u]
            if not self._users.has_key(u):
                user0 = UserInfo()
                self._users[u] = user0
            else:
                user0 = self._users[u]
            user0.add(user1.nFiles, user1.totalSize)

    def __str__(self):
        return "total %s over %d files" % (size2str(self.totalSize), self.nFiles)

    def users(self):
        lines = [str(self)]
        for user in sorted(self._users.items(), key=lambda u: u[1].totalSize, reverse=True):
            name = user[0]
            info = user[1]
            # exclude trivial small stuff
            if info.totalSize > 1024:
                lines.append("%s %s over %d files" % (name, size2str(info.totalSize), info.nFiles))
        return '\n'.join(lines)

    def write(self, f):
        f.write("%d %d\n" % (self.nFiles, self.totalSize))
        for u, user in self._users.iteritems():
            f.write("%s %d %d\n" % (u, user.nFiles, user.totalSize))
