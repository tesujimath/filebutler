# Copyright 2017-2018 Simon Guest
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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import errno
import functools
import os.path

from .CLIError import CLIError
from .ConfigError import ConfigError
from .DatasetFilesetCache import DatasetFilesetCache
from .Fileset import Fileset
from .FilesetSelector import FilesetSelector
from .PooledFile import PooledFile
from .SimpleFilesetCache import SimpleFilesetCache
from .SizeFilesetCache import SizeFilesetCache
from .UserFilesetCache import UserFilesetCache
from .WeeklyFilesetCache import WeeklyFilesetCache
from .util import filedatestr, filetimestr, verbose_stderr, debug_log, progress_stderr, warning

# Stack up the caches we support, so that each cache can instantiate
# its next one, via its next parameter.
class Cache(Fileset):

    caches = {
        'weekly':  WeeklyFilesetCache,
        'size':    SizeFilesetCache,
        'dataset': DatasetFilesetCache,
        'user':    UserFilesetCache,
    }
    defaultCacheKinds = ['weekly', 'user', 'size', 'dataset']

    def __init__(self, name, fileset, path, deltadir, ctx, attrs):
        super(self.__class__, self).__init__()
        self.name = name
        self._fileset = fileset
        self._path = path
        self._deltadir = deltadir
        self._ctx = ctx
        self._attrs = attrs.copy() # copy the dictionary, so we freeze its values
        self._cache0 = None
        cacheKinds = self._attrs['cache'] if 'cache' in self._attrs else self.__class__.defaultCacheKinds
        try:
            self._caches = [self.__class__.caches[kind] for kind in cacheKinds]
        except KeyError as e:
            raise ConfigError("invalid cache kind '%s' (valid kinds are %s)" % (e, ', '.join(sorted(self.__class__.caches.keys()))))

    def _exists(self):
        try:
            s = os.stat(self._path)
            exists = True
        except OSError as e:
            if e.errno == errno.ENOENT:
                exists = False
            else:
                raise
        return exists

    def _abortIfMissingCache(self):
        if not self._exists():
            raise CLIError("<missing-cache>, use 'update-cache %s', or 'update-cache' for all" % self.name)

    def description(self):
        if self._exists():
            return "%s cached on %s" % (self._fileset.description(), filedatestr(self._path))
        else:
            return "%s <missing-cache>" % (self._fileset.description())

    def _cache(self):
        if self._cache0 is None:
            self._cache0 = self._newcache(None, self._path, self._deltadir, self._ctx, self._attrs, FilesetSelector(), 0)
        return self._cache0

    def _newcache(self, parent, path, deltadir, ctx, attrs, sel, level):
        if level < len(self._caches):
            return self._caches[level](parent, path, deltadir, ctx, attrs, sel, functools.partial(self._newcache, level = level + 1))
        else:
            return SimpleFilesetCache(parent, path, deltadir, ctx, attrs, sel)

    def select(self, filter=None):
        self._abortIfMissingCache()
        cache = self._cache()
        filterStr = " " + str(filter) if filter is not None else ""
        verbose_stderr("fileset %s%s reading from %s cache at %s\n" % (self.name, filterStr, filetimestr(self._path), self._path))
        for filespec in cache.select(filter):
            yield filespec

    def merge_info(self, acc, filter=None):
        self._abortIfMissingCache()
        #debug_log("Cache(%s) merge_info\n" % self.name)
        cache = self._cache()
        cache.merge_info(acc, filter)

    def update(self):
        cache = self._cache()
        try:
            cache.create()
        except OSError as e:
            if e.errno == errno.EACCES or e.errno == errno.EPERM:
                # not ours to update, so silently do nothing
                warning("can't update system cache %s" % self.name)
                return
        for filespec in self._fileset.select():
            cache.add(filespec)
        # ensure from here on we don't hit open file problems
        PooledFile.flushAll()
        cache.finalize()
        # touch cache rootdir, to show updated
        os.utime(self._path, None)
        progress_stderr("updated %s\n" % self.name)

    def getCaches(self, caches):
        caches[self.name] = self
