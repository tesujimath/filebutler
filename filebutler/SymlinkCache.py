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

import os.path
import shutil

from .PooledFile import PooledFile
from .util import verbose_stderr

class SymlinkCache(object):

    def __init__(self, path):
        self._path = os.path.join(path, 'symlinks')
        self._files = {}

    def _target(self, target):
        """Return target dir and path"""
        # We want to store a list of files, and also arbitrarily nested directories.
        # We have to ensure separation of target paths from metadata (filelist), so we
        # prefix all target path components with underscore.  This somewhat messes up the
        # nice presentation of paths, but there doesn't seem to be a nicer way to do it that
        # is guaranteed to work.  For example consider this:
        # dirlink -> a/b
        # filelink -> a/b/c
        # We need a file in which we can write the dirlink, as well as a directory to hold
        # that for filelink.
        escaped_target = target.replace('/', '/_')[1:]
        target_dir = os.path.normpath(os.path.join(self._path, escaped_target))
        target_filelist = os.path.join(target_dir, "filelist")
        return target_dir, target_filelist

    def _external_path(self, target_path):
        """Return external path for target."""
        return target_path[len(self._path):].replace('/_', '/')

    def add(self, source, target):
        target_dir, target_filelist = self._target(os.path.normpath(target))
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        f = self._files.get(target)
        if f is None:
            f = PooledFile(target_filelist, 'a')
            self._files[target] = f
        f.write("%s\n" % source)

    def purge(self):
        shutil.rmtree(self._path)

    def sources(self, external_target, recursive):
        # don't want trailing slashes
        if external_target != '/':
            external_target = external_target.rstrip('/')
        filelists = []
        symlinks = []
        target_dir, target_filelist = self._target(external_target)
        # build list of filelists we will look at
        if recursive:
            for root, dirs, files in os.walk(target_dir):
                for f in files:
                    if f == "filelist":
                        filelists.append((self._external_path(root), os.path.join(root, f)))
        else:
            filelists = [(external_target, target_filelist)]

        # generate results for each filelist
        for target, filelist in filelists:
            try:
                with open(filelist, 'r') as f:
                    symlinks.extend([ "%s <- %s " % (target, source) for source in f.read().splitlines() ])
            except FileNotFoundError:
                pass
        return symlinks

    def complete(self, prefix):
        #verbose_stderr("SymlinkCache::complete('%s')\n" % prefix)
        external_dir, file_prefix = os.path.split(prefix)
        target_dir, target_filelist = self._target(external_dir)
        #verbose_stderr("complete '%s' '%s' '%s'\n" % (target_dir, external_dir, file_prefix))
        if not os.path.exists(target_dir):
            #verbose_stderr("no target_dir\n")
            return []
        else:
            return self._matching(external_dir, target_dir, file_prefix)

    def _matching(self, external_dir, target_dir, file_prefix):
        matching_files = []     # external paths
        matching_dirs = []      # tuple of (external, target)
        for entry in os.listdir(target_dir):
            if entry.startswith('_%s' % file_prefix):
                entry_target = os.path.join(target_dir, entry)
                is_file = os.path.exists(os.path.join(entry_target, "filelist"))
                if is_file:
                    matching_files.append(os.path.join(external_dir, entry[1:]))
                # maybe it also completes as a directory
                entry_target_size = len(os.listdir(entry_target))
                if entry_target_size > 1 and is_file or entry_target_size > 0 and not is_file:
                    matching_dirs.append((os.path.join(external_dir, entry[1:] + '/'), entry_target))

        if matching_files or len(matching_dirs) > 1:
            # found multiple matches, so return them
            matches = matching_files + [ x[0] for x in matching_dirs ]
            #verbose_stderr("_matching returning simply %s\n" % str(matches))
        elif matching_dirs:
            # only one matching directory, so expand another level
            external_subdir, target_subdir = matching_dirs[0]
            #verbose_stderr("_matching recursing on %s, %s\n" % (external_subdir, target_subdir))
            matches = self._matching(external_subdir, target_subdir, '')
        else:
            matches = []
        return matches
