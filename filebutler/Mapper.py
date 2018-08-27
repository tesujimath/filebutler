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

import grp
import pwd
import re

class Mapper(object):

    def __init__(self):
        self._uids = {}
        self._usernames = {}
        self._groupnames = {}
        self._datasetRegex = None
        self._datasetReplace = None

    def uidFromUsername(self, username):
        """Returns -1 if can't resolve the username."""
        if username not in self._uids:
            try:
                pw = pwd.getpwnam(username)
                uid = pw[2]
            except KeyError:
                try:
                    uid = int(username)
                except ValueError:
                    uid = -1
            self._uids[username] = uid
        else:
            uid = self._uids[username]
        return uid

    def usernameFromId(self, uid):
        if uid not in self._usernames:
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
        if gid not in self._groupnames:
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

    def setDatasetRegex(self, datasetRegex, datasetReplace):
        self._datasetRegex = datasetRegex
        self._datasetReplace = datasetReplace

    def clearDatasetRegex(self):
        self._datasetRegex = None
        self._datasetReplace = None

    def datasetFromPath(self, path):
        noDatasetFound = '-'
        if self._datasetRegex is None:
            return noDatasetFound
        dataset, n = re.subn(self._datasetRegex, self._datasetReplace, path, 1)
        if n == 1:
            return dataset
        else:
            return noDatasetFound
