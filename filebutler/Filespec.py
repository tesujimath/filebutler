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
import time

from util import fbTimeFmt, time2str

# FileSpec fields:
# path - string, relative to some (externally defined) rootdir
# user - string
# group - string
# size - in bytes
# mtime - seconds since epoch
# perms - string, in ls -l format
class Filespec(object):

    @classmethod
    def fromFile(cls, f):
        for line in f:
            fields = line.rstrip().split(None, 5)
            if len(fields) != 6:
                print("bad filespec: %s" % line.rstrip())
            else:
                yield Filespec(fields[5],
                               fields[0],
                               fields[1],
                               int(fields[2]),
                               calendar.timegm(time.strptime(fields[3], fbTimeFmt)),
                               fields[4])

    def __init__(self, path, user, group, size, mtime, perms):
        self.path = path
        self.user = user
        self.group = group
        self.size = size
        self.mtime = mtime
        self.perms = perms

    def __str__(self):
        return "%s:%s %d %s %s %s" % (
            self.user,
            self.group,
            self.size,
            time2str(self.mtime),
            self.perms,
            self.path)

    def write(self, f):
        f.write("%s %s %d %s %s %s\n" % (
            self.user,
            self.group,
            self.size,
            time2str(self.mtime),
            self.perms,
            self.path))
