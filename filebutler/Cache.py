import functools
import os.path

from SimpleFilelistCache import SimpleFilelistCache
from UserFilelistCache import UserFilelistCache
from WeeklyFilelistCache import WeeklyFilelistCache

# Stack up the caches we support, so that each cache can instantiate
# its next one, via its next parameter.
class Cache(object):

    def __init__(self, filelist, path):
        self._filelist = filelist
        self._path = path
        self._caches = [WeeklyFilelistCache, UserFilelistCache]

    def _filelistHelper(self, path, level):
        if level < len(self._caches):
            return self._caches[level](path, functools.partial(self._filelistHelper, level = level + 1))
        else:
            return SimpleFilelistCache(path)

    def filelist(self):
        return self._filelistHelper(self._path, 0)

    def update(self):
        cache = self.filelist()
        if os.path.exists(self._path):
            cache.purge()
        for filespec in self._filelist.select():
            cache.add(filespec)
        cache.save()
