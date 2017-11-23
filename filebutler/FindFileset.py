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

from CLIError import CLIError
from Fileset import Fileset
from Filespec import Filespec
from util import filemode, verbose_stderr

class FindFileset(Fileset):

    @classmethod
    def parse(cls, idMapper, name, toks):
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
        return cls(idMapper, name, path, match, replace)

    def __init__(self, idMapper, name, path, match, replace):
        #print("FindFileset init '%s' '%s' '%s'" % (path, match, replace))
        Fileset.__init__(self)
        self._idMapper = idMapper
        self.name = name
        self._path = path
        self._match = match
        self._replace = replace

    def description(self):
        return "%s directory %s" % (self.name, self._path)

    def _filespec(self, path):
        s = os.lstat(path)

        return Filespec(path=path,
                        user=self._idMapper.usernameFromId(s.st_uid),
                        group=self._idMapper.groupnameFromId(s.st_gid),
                        size=s.st_size,
                        mtime=s.st_mtime,
                        perms=filemode(s.st_mode))

    def select(self, filter=None):
        verbose_stderr("fileset %s scanning files under %s\n" % (self.name, self._path))
        for root,dirs,files in os.walk(self._path):
            for x in dirs + files:
                filespec = self._filespec(os.path.join(root, x))
                if filter == None or filter.selects(filespec):
                    #print("FindFileset scan found %s" % filespec)
                    yield filespec
