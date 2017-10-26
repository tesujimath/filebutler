import os
import grp
import pwd
import re
import stat

from Filespec import Filespec
from util import filemode

class FindFileset(object):

    @classmethod
    def parse(cls, toks):
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
        return cls(path, match, replace)

    def __init__(self, path, match, replace):
        #print("FindFileset init '%s' '%s' '%s'" % (path, match, replace))
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
        #print("FindFileset %s select %s" % (self._path, filter))
        for root,dirs,files in os.walk(self._path):
            for x in dirs + files:
                filespec = self._filespec(os.path.join(root, x))
                if filter == None or filter.selects(filespec):
                    #print("FindFileset scan found %s" % filespec)
                    yield filespec
