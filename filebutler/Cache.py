import functools
import os.path

from SimpleFilesetCache import SimpleFilesetCache
from UserFilesetCache import UserFilesetCache
from WeeklyFilesetCache import WeeklyFilesetCache

# Stack up the caches we support, so that each cache can instantiate
# its next one, via its next parameter.
class Cache(object):

    def __init__(self, fileset, path):
        self._fileset = fileset
        self._path = path
        self._caches = [WeeklyFilesetCache, UserFilesetCache]

    def _filesetHelper(self, path, level):
        if level < len(self._caches):
            return self._caches[level](path, functools.partial(self._filesetHelper, level = level + 1))
        else:
            return SimpleFilesetCache(path)

    def fileset(self):
        return self._filesetHelper(self._path, 0)

    def update(self):
        cache = self.fileset()
        if os.path.exists(self._path):
            cache.purge()
        for filespec in self._fileset.select():
            cache.add(filespec)
        cache.save()
