# Copyright 2017-2023 Simon Guest
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

import os.path
from .util import date2str, size2str

class CondaEnvCounter(object):
    """Count conda environment and their sizes."""

    def __init__(self):
        self._envs = {}
        self._current_env_root = None
        self._current_env_size = 0
        self._current_env_count = 0
        self._current_env_mtime = None
        self._accumulated_dirs = {}

    def _begin_env(self, env_root, mtime, size):
        self._current_env_root = env_root
        self._current_env_size = size
        self._current_env_count = 1
        self._current_env_mtime = mtime

        # fold in anything we saw previously
        for path, (size, count) in self._accumulated_dirs.items():
            if path.startswith(env_root):
                self._current_env_size += size
                self._current_env_count += count
        self._accumulated_dirs = {}

    def _end_env(self):
        self._envs[ self._current_env_root ] = (self._current_env_mtime, self._current_env_size, self._current_env_count)
        self._current_env_root = None
        self._current_env_size = 0

    def _accumulate(self, path, size):
        if path in self._accumulated_dirs:
            accumulated_size, accumulated_count = self._accumulated_dirs[path]
            self._accumulated_dirs[path] = (accumulated_size + size, accumulated_count + 1)
        else:
            self._accumulated_dirs[path] = (size, 1)

    def _count(self, path, mtime, size):
        if self._current_env_root is not None:
            if path.startswith(self._current_env_root):
                self._current_env_size += size
                self._current_env_count += 1
            else:
                self._end_env()
        else:
            if os.path.basename(path) == "conda-meta":
                env_root = os.path.dirname(path)
                self._begin_env(env_root, mtime, size)
            else:
                self._accumulate(path, size)

    def add(self, filespec):
        if filespec.perms[0] == 'd':
            self._count(filespec.path, filespec.mtime, filespec.size)
        else:
            parent_dir = os.path.dirname(filespec.path)
            self._count(parent_dir, filespec.mtime, filespec.size)

    def dump(self, f):
        total_size = 0
        total_count = 0
        for path in sorted(self._envs):
            (mtime, size, count) = self._envs[path]
            total_size += size
            total_count += count
            f.write("%s\t%s\t%10d\t%s\n" % (date2str(mtime), size2str(size), count, path))
        f.write("== TOTAL ==\t%s\t%10d\n" % (size2str(total_size), total_count))
