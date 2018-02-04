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
    def parse(cls, mapper, pathway, name, toks):
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
        return cls(mapper, pathway, name, path, match, replace)

    def __init__(self, mapper, pathway, name, path, match, replace):
        #print("FindFileset init '%s' '%s' '%s'" % (path, match, replace))
        Fileset.__init__(self)
        self._mapper = mapper
        self._pathway = pathway
        self.name = name
        self._path = path
        self._match = match
        self._replace = replace

    def description(self):
        return "%s directory %s" % (self.name, self._path)

    def select(self, filter=None):
        verbose_stderr("fileset %s scanning files under %s\n" % (self.name, self._path))
        pathlen = len(self._path) + (0 if self._path[-1] == '/' else 1)
        for root,dirs,files in os.walk(self._path):
            relroot = root[pathlen:]
            for x in dirs + files:
                s = os.lstat(os.path.join(root, x))
                relpath = os.path.join(relroot, x)
                path = re.sub(self._match, self._replace, relpath)
                filespec = Filespec(fileset=self,
                                    dataset=self._pathway.datasetFromPath(path),
                                    path=path,
                                    user=self._mapper.usernameFromId(s.st_uid),
                                    group=self._mapper.groupnameFromId(s.st_gid),
                                    size=s.st_size,
                                    mtime=s.st_mtime,
                                    perms=filemode(s.st_mode))
                if filter == None or filter.selects(filespec):
                    #print("FindFileset scan found %s" % filespec)
                    yield filespec
