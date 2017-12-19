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

import calendar
import errno
import os
import time

from util import fbTimeFmt, time2str, date2str, size2str

# FileSpec fields:
# path - string, relative to some (externally defined) rootdir
# user - string
# group - string
# size - in bytes
# mtime - seconds since epoch
# perms - string, in ls -l format
class Filespec(object):

    @classmethod
    def fromFile(cls, f, fileset):
        for line in f:
            fields = line.rstrip().split(None, 5)
            if len(fields) != 6:
                print("bad filespec: %s" % line.rstrip())
            else:
                yield Filespec(fileset,
                               fields[5],
                               fields[6],
                               fields[0],
                               fields[1],
                               int(fields[2]),
                               calendar.timegm(time.strptime(fields[3], fbTimeFmt)),
                               fields[4])

    def __init__(self, fileset, dataset, path, user, group, size, mtime, perms):
        self.fileset = fileset  # fileset whicih owns this filespec
        self.dataset = dataset
        self.path = path
        self.user = user
        self.group = group
        self.size = size
        self.mtime = mtime
        self.perms = perms

    def isdir(self):
        return self.perms[0] == 'd'

    def delete(self):
        try:
            if self.isdir():
                os.rmdir(self.path)
            else:
                os.remove(self.path)
            # tell owning fileset we're deleted
            self.fileset.delete(self)
        except OSError as e:
            if e.errno == errno.ENOENT:
                # deleted already, don't care
                pass
            elif e.errno == errno.EACCES:
                # silently refuse to delete where we don't have permission
                pass
            elif e.errno == errno.ENOTEMPTY:
                # silently refuse to delete non-empty directory
                pass
            else:
                raise

    def format(self, width=50):
        if width < 50:
            width = 50
        if len(self.path) > width:
            width = (len(self.path) / 10 + 1) * 10
        s = ("%s %s %4s %-" + str(width) + "s %s:%s") % (
            self.perms,
            date2str(self.mtime),
            size2str(self.size),
            self.path,
            self.user,
            self.group)
        return s, width

    def write(self, f):
        f.write("%s %s %d %s %s %s %s\n" % (
            self.user,
            self.group,
            self.size,
            time2str(self.mtime),
            self.perms,
            self.dataset,
            self.path))
