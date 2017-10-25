import calendar
import time

# FileSpec fields:
# path - string, relative to some (externally defined) rootdir
# user - string
# group - string
# size - in bytes
# mtime - seconds since epoch
# perms - string, in ls -l format
class Filespec(object):

    _fileTimeFmt = "%Y%m%d-%H%M%S"
    _strTimeFmt = "%Y%m%d-%H%M%S"

    @classmethod
    def fromFile(cls, f):
        for line in f:
            fields = line.split(5)
            yield Filespec(fields[5],
                           fields[0],
                           fields[1],
                           int(fields[2]),
                           calendar.timegm(time.strptime(fields[3], cls._fileTimeFmt)),
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
            time.strftime(self.__class__._strTimeFmt, time.localtime(self.mtime)),
            self.perms,
            self.path)

    def write(self, f):
        f.write("%s %s %d %s %s %s\n" % (
            self.user,
            self.group,
            self.size,
            time.strftime(self.__class__._fileTimeFmt, time.gmtime(self.mtime)),
            self.perms,
            self.path))
