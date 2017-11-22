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

import errno
import functools
import os.path

from Fileset import Fileset
from SimpleFilesetCache import SimpleFilesetCache
from UserFilesetCache import UserFilesetCache
from WeeklyFilesetCache import WeeklyFilesetCache
from util import filedatestr, filetimestr, verbose_stderr, debug_stderr, progress_stderr, stderr

# Stack up the caches we support, so that each cache can instantiate
# its next one, via its next parameter.
class Cache(Fileset):

    def __init__(self, name, fileset, path):
        Fileset.__init__(self)
        self.name = name
        self._fileset = fileset
        self._path = path
        self._cache0 = None
        self._caches = [WeeklyFilesetCache, UserFilesetCache]

    def description(self):
        return "%s cached on %s" % (self._fileset.description(), filedatestr(self._path))

    def _cache(self):
        if self._cache0 is None:
            self._cache0 = self._newcache(self._path, 0)
        return self._cache0

    def _newcache(self, path, level):
        if level < len(self._caches):
            return self._caches[level](path, functools.partial(self._newcache, level = level + 1))
        else:
            return SimpleFilesetCache(path)

    def select(self, filter=None):
        cache = self._cache()
        filterStr = " " + str(filter) if filter is not None else ""
        verbose_stderr("fileset %s%s reading from %s cache at %s\n" % (self.name, filterStr, filetimestr(self._path), self._path))
        for filespec in cache.select(filter):
            yield filespec

    def merge_info(self, inf, filter=None):
        cache = self._cache()
        cache.merge_info(inf, filter)

    def update(self):
        cache = self._cache()
        try:
            cache.create()
        except OSError as e:
            if e.errno == errno.EACCES:
                # not ours to update, so silently do nothing
                stderr("warning: can't update system cache %s\n" % self.name)
                return
        for filespec in self._fileset.select():
            try:
                cache.add(filespec)
            except IOError as e:
                if e.errno == errno.EMFILE:
                    debug_stderr("open failed, flush all caches and redo on %s\n" % self._path)
                    # It would be better to implement an LRU cache, but that
                    # hardly seems worth it.  So simply close them all.
                    cache.flush()
                    cache.add(filespec)
                else:
                    raise
        cache.flush()
        cache.writeInfo()
        progress_stderr("updated %s\n" % self.name)
