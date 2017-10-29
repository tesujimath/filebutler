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
