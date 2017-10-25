import os.path

class UserFilelistCache(object):

    def __init__(self, path, next):
        self._path = path
        self._next = next
        self._users = {}        # of filelist, indexed by integer user

        # load stubs for all users found
        if os.path.exists(self._path):
            for u in os.listdir(self._path):
                self._users[u] = None # stub

    def _subpath(self, u):
        return os.path.join(self._path, u)

    def _filelist(self, u):
        """On demand creation of child filelists."""
        if self._users.has_key(u):
            filelist = self._users[u]
        else:
            filelist = None
        if filelist is None:
            filelist = self._next(self._subpath(u))
            self._users[u] = filelist
        return filelist

    def select(self, filter):
        users = sorted(self._users.keys())
        for u in users:
            if filter.owner is None or u == filter.owner:
                # no yield from in python 2, so:
                for filespec in self._filelist(u).select(filter):
                    yield filespec

    def save(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        for filelist in self._users.values():
            filelist.save()

    def add(self, filespec):
        filelist = self._filelist(filespec.user)
        filelist.add(filespec)

