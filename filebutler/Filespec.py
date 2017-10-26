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
