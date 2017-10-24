import time

# FileSpec fields:
# path - string, relative to some (externally defined) rootdir
# user - string
# group - string
# size - in bytes
# mtime - seconds since epoch
# perms - string, in ls -l format
class Filespec(object):
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
            time.strftime("%Y%m%d-%H%M%S", time.localtime(self.mtime)),
            self.perms,
            self.path)
