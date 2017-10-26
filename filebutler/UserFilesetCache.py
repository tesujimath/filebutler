import os.path

class UserFilesetCache(object):

    def __init__(self, path, next):
        self._path = path
        self._next = next
        self._users = {}        # of fileset, indexed by integer user

        # load stubs for all users found
        if os.path.exists(self._path):
            for u in os.listdir(self._path):
                self._users[u] = None # stub

    def _subpath(self, u):
        return os.path.join(self._path, u)

    def _fileset(self, u):
        """On demand creation of child filesets."""
        if self._users.has_key(u):
            fileset = self._users[u]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(u))
            self._users[u] = fileset
        return fileset

    def select(self, filter=None):
        users = sorted(self._users.keys())
        for u in users:
            if filter is None or filter.owner is None or u == filter.owner:
                # no yield from in python 2, so:
                for filespec in self._fileset(u).select(filter):
                    yield filespec

    def save(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        for fileset in self._users.values():
            fileset.save()

    def add(self, filespec):
        fileset = self._fileset(filespec.user)
        fileset.add(filespec)

