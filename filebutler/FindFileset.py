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

import errno
import os
import os.path
import grp
import pwd
import re
import stat

from .CLIError import CLIError
from .Fileset import Fileset
from .Filespec import Filespec
from .PooledFile import listdir
from .util import filemode, verbose_stderr

class FindFileset(Fileset):

    @classmethod
    def parse(cls, ctx, name, toks):
        if len(toks) == 1:
            path = toks[0]
            match = '^'
            replace = toks[0].rstrip('/') + '/'
        elif len(toks) == 3:
            path = toks[0]
            match = toks[1]
            replace = toks[2]
        else:
            raise CLIError("find requires path, and either both of match-re, replace-str or neither")
        return cls(ctx, name, path, match, replace)

    def __init__(self, ctx, name, path, match, replace):
        #print("FindFileset init '%s' '%s' '%s'" % (path, match, replace))
        super(self.__class__, self).__init__()
        self._ctx = ctx
        self.name = name
        self._path = path
        self._match = match
        self._replace = replace

    def description(self):
        return "%s directory %s" % (self.name, self._path)

    def select(self, filter=None):
        verbose_stderr("fileset %s scanning files under %s\n" % (self.name, self._path))
        pathlen = len(self._path) + (0 if self._path[-1] == '/' else 1)
        dirs = [self._path]
        # can't use os.walk, as that fails if we hit too many open files
        while dirs != []:
            root = dirs[0]
            relroot = root[pathlen:]
            dirs = dirs[1:]
            try:
                entries = listdir(root)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # ignore just-disappeared directory
                    continue
                else:
                    raise

            for x in entries:
                xpath = os.path.join(root, x)
                xrel = os.path.join(relroot, x)
                try:
                    s = os.lstat(xpath)
                except OSError as e:
                    if e.errno == errno.ENOENT:
                        # ignore just-disappeared path
                        continue
                    else:
                        raise
                if stat.S_ISDIR(s.st_mode):
                    dirs.append(xpath)
                path = re.sub(self._match, self._replace, xrel)
                filespec = Filespec(fileset=self,
                                    dataset=self._ctx.pathway.datasetFromPath(path),
                                    path=path,
                                    user=self._ctx.mapper.usernameFromId(s.st_uid),
                                    group=self._ctx.mapper.groupnameFromId(s.st_gid),
                                    size=s.st_size,
                                    mtime=s.st_mtime,
                                    perms=filemode(s.st_mode))
                if filter == None or filter.selects(filespec):
                    #print("FindFileset scan found %s" % filespec)
                    yield filespec
