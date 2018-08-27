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

import calendar
import errno
import os
import time

from .util import fbTimeFmt, time2str, date2str, size2str, debug_log

# FileSpec fields:
# path - string, relative to some (externally defined) rootdir
# user - string
# group - string
# size - in bytes
# mtime - seconds since epoch
# perms - string, in ls -l format
class Filespec(object):

    @classmethod
    def fromFile(cls, f, fileset, sel):
        for line in f:
            fields = line.rstrip().split(None, 4)
            if len(fields) != 5:
                print("bad filespec: %s" % line.rstrip())
            else:
                yield Filespec(fileset,
                               sel.dataset,
                               fields[4],
                               sel.owner,
                               fields[0],
                               int(fields[1]),
                               calendar.timegm(time.strptime(fields[2], fbTimeFmt)),
                               fields[3])

    def __init__(self, fileset, dataset, path, user, group, size, mtime, perms):
        self.fileset = fileset  # fileset whicih owns this filespec
        self.dataset = dataset
        self.path = path
        self.user = user
        self.group = group
        self.size = size
        self.mtime = mtime
        self.perms = perms

    def __str__(self):
        return self.format(all=True)[0]

    def isdir(self):
        return self.perms[0] == 'd'

    def delete(self, logf):
        """Delete file or directory, logging path to logf on success."""
        deleted = False
        try:
            if self.isdir():
                os.rmdir(self.path)
            else:
                os.remove(self.path)
            deleted = True
            # tell owning fileset we're deleted
            self.fileset.delete(self)
        except OSError as e:
            debug_log("failed to delete %s, %s\n" % (self.path, e))
            if e.errno == errno.ENOENT:
                # deleted already, don't care
                pass
            elif e.errno == errno.EACCES or e.errno == errno.EPERM:
                # silently refuse to delete where we don't have permission
                pass
            elif e.errno == errno.ENOTEMPTY:
                # silently refuse to delete non-empty directory
                pass
            else:
                raise
        if deleted:
            logf.write("%s%s\n" % self.format(pad=False))

    @classmethod
    def formattedToPath(cls, formatted):
        """Return the file path from a formatted Filespec (with all=False)."""
        return formatted.split(None, 4)[4]

    def format(self, width=0, all=False, pad=True):
        usergroup = "%s:%s" % (self.user, self.group)
        if len(usergroup) >= width:
            width = len(usergroup) + 1
        if not pad:
            width = 0
        s = ("%s %-" + str(width) + "s %s %4s %s") % (
            self.perms,
            usergroup,
            date2str(self.mtime),
            size2str(self.size),
            self.path)
        if all:
            s += " %s" % (self.dataset)
        return s, width

    def write(self, f):
        f.write("%s %d %s %s %s\n" % (
            self.group,
            self.size,
            time2str(self.mtime),
            self.perms,
            self.path))
