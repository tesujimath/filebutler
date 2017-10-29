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

import os
import grp
import pwd
import re
import stat

from Fileset import Fileset
from Filespec import Filespec
from util import filemode, verbose_stderr

class FindFileset(Fileset):

    @classmethod
    def parse(cls, name, toks):
        if len(toks) == 1:
            path = toks[0]
            match = '/'
            replace = ''
        elif len(toks) == 3:
            path = toks[0]
            match = toks[1]
            replace = toks[2]
        else:
            raise CLIError("find requires path, and either both of match-re, replace-str or neither")
        return cls(name, path, match, replace)

    def __init__(self, name, path, match, replace):
        #print("FindFileset init '%s' '%s' '%s'" % (path, match, replace))
        Fileset.__init__(self)
        self._name = name
        self._path = path
        self._match = match
        self._replace = replace
        self._users = {}
        self._groups = {}

    def _filespec(self, path):
        s = os.lstat(path)
        # cache the results of looking up user and group names
        if not self._users.has_key(s.st_uid):
            pw = pwd.getpwuid(s.st_uid)
            user = pw[0]
            self._users[s.st_uid] = user
        else:
            user = self._users[s.st_uid]
        if not self._groups.has_key(s.st_gid):
            gr = grp.getgrgid(s.st_gid)
            group = gr[0]
            self._groups[s.st_gid] = group
        else:
            group = self._groups[s.st_gid]

        return Filespec(path=path,
                        user=user,
                        group=group,
                        size=s.st_size,
                        mtime=s.st_mtime,
                        perms=filemode(s.st_mode))

    def select(self, filter=None):
        verbose_stderr("fileset %s scanning files under %s\n" % (self._name, self._path))
        for root,dirs,files in os.walk(self._path):
            for x in dirs + files:
                filespec = self._filespec(os.path.join(root, x))
                if filter == None or filter.selects(filespec):
                    #print("FindFileset scan found %s" % filespec)
                    yield filespec
