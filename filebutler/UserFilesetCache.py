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

from .FilesetCache import FilesetCache
from .Filter import Filter
from .util import debug_log

class UserFilesetCache(FilesetCache):

    def __init__(self, parent, path, deltadir, ctx, attrs, sel, next):
        super(self.__class__, self).__init__(parent, path, deltadir, ctx, attrs, sel, next)
        self._users = {}        # of fileset, indexed by username
        self._permissioned = {}        # of boolean, indexed by username

        # load stubs for all users found
        if os.path.exists(self._path):
            for u in self.children():
                self._users[u] = None # stub
                self._permissioned[u] = False

    def _fileset(self, u):
        """On demand creation of child filesets."""
        if u in self._users:
            fileset = self._users[u]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self, self._subpath(u), self._subdeltadir(u), self._ctx, self._attrs, self._sel.withOwner(u))
            self._users[u] = fileset
            self._permissioned[u] = False
        return fileset

    def filtered(self, filter=None):
        users = sorted(self._users.keys(), key=str)
        for u in users:
            if filter is None or filter.owner is None or u == filter.owner:
                yield self._fileset(u), Filter.clearOwner(filter)

    def create(self):
        """Create empty cache on disk, purging any previous."""
        #debug_log("UserFilesetCache creating at %s\n" % self._path)
        self.purge()
        self._users = {}
        self._permissioned = {}

    def filesetFor(self, filespec):
        return self._fileset(filespec.user)

    def add(self, filespec):
        super(self.__class__, self).add(filespec)
        # special handling for private filesets
        fileset = self.filesetFor(filespec)
        if 'private' in self._attrs and os.geteuid() == 0 and not self._permissioned[filespec.user]:
            # set permissions of fileset directory
            upath = self._subpath(filespec.user)
            uid = self._ctx.mapper.uidFromUsername(filespec.user)
            if uid != -1:
                os.chown(upath, uid, -1)
            os.chmod(upath, 0o500)
            self._permissioned[filespec.user] = True
