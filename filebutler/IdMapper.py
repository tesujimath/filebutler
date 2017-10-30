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

import grp
import pwd

class IdMapper(object):

    def __init__(self):
        self._usernames = {}
        self._groupnames = {}

    def usernameFromId(self, uid):
        if not self._usernames.has_key(uid):
            try:
                pw = pwd.getpwuid(uid)
                name = pw[0]
            except KeyError:
                name = str(uid)
            self._usernames[uid] = name
        else:
            name = self._usernames[uid]
        return name

    def usernameFromString(self, s):
        try:
            uid = int(s)
            return self.usernameFromId(uid)
        except ValueError:
            return s

    def groupnameFromId(self, gid):
        if not self._groupnames.has_key(gid):
            try:
                gr = grp.getgrgid(gid)
                name = gr[0]
            except KeyError:
                name = str(gid)
            self._groupnames[gid] = name
        else:
            name = self._groupnames[gid]
        return name

    def groupnameFromString(self, s):
        try:
            gid = int(s)
            return self.groupnameFromId(gid)
        except ValueError:
            return s
