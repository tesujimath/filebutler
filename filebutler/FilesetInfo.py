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

from util import size2str
from UserInfo import UserInfo

class FilesetInfo(object):
    def __init__(self):
        self.nFiles = 0
        self.totalSize = 0
        self._users = {}

    def add(self, filespec):
        self.nFiles += 1
        self.totalSize += filespec.size
        if self._users.has_key(filespec.user):
            user = self._users[filespec.user]
        else:
            user = UserInfo()
            self._users[filespec.user] = user
        user.add(filespec)

    def __str__(self):
        return "total %s over %d files" % (size2str(self.totalSize), self.nFiles)

    def users(self):
        lines = [str(self)]
        for user in sorted(self._users.items(), key=lambda u: u[1].totalSize, reverse=True):
            name = user[0]
            info = user[1]
            lines.append("%s %s over %d files" % (name, size2str(info.totalSize), info.nFiles))
        return '\n'.join(lines)
