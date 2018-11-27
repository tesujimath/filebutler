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

from .FilesetInfoAccumulator import FilesetInfoAccumulator
from .FilespecMerger import FilespecMerger
from .PooledFile import listdir
from .util import debug_log, verbose_stderr, warning

class FilesetCache(object):
    """FilesetCache is a base class."""

    def __init__(self, parent, path, deltadir, ctx, attrs, sel, next):
        self._parent = parent
        self._path = path
        self._deltadir = deltadir
        self._ctx = ctx
        self._attrs = attrs
        self._sel = sel
        self._next = next
        self._fileinfo = None
        self._deletedInfo = FilesetInfoAccumulator(self._attrs)

    def __hash__(self):
        """For storage in sets."""
        return id(self)

    def __eq__(self, other):
        """For storage in sets."""
        return self is other

    def _subpath(self, x):
        return os.path.join(self._path, '_' + str(x))

    def _subdeltadir(self, x):
        return os.path.join(self._deltadir, '_' + str(x))

    def children(self):
        """Child filesets are stored with a leading underscore, to leave room for metadata."""
        for x in listdir(self._path):
            if x.startswith('_'):
                yield x[1:]

    def infopath(self, deleted=False):
        if deleted:
            return os.path.join(self._deltadir, "deleted.info")
        else:
            return os.path.join(self._path, "info")

    def purge(self):
        """Purge existing cache on disk, and create empty."""
        #debug_log("FilesetCache purging %s\n" % self._path)
        if os.path.exists(self._path):
            # Purge existing cache.
            # For safety in case of misconfiguration, we only delete directories with a leading underscore
            for x in listdir(self._path):
                px = os.path.join(self._path, x)
                if x.startswith('_'):
                    shutil.rmtree(px)
                elif x == 'info':
                    os.remove(px)
                else:
                    verbose_stderr("WARNING: cache purge ignoring %s\n" % px)
        else:
            os.makedirs(self._path)

    def select(self, filter=None):
        merger = FilespecMerger()
        for f, f1 in self.filtered(filter):
            merger.add(f.select(f1))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        """Return whether merged from cache; otherwise caller will have to scan over filespecs."""
        #debug_log("FilesetCache(%s) merge_info\n" % self._path)
        if filter is None:
            #debug_log("FilesetCache(%s)::merge_info(None)\n" % self._path)
            if self._fileinfo is None:
                #debug_log("FilesetCache(%s)::merge_info(None) reading info file\n" % self._path)
                infofile = self.infopath()
                deletedInfofile = self.infopath(deleted=True)
                try:
                    if os.path.exists(deletedInfofile):
                        # if deleted filelist is older than cache, remove it
                        if os.stat(deletedInfofile).st_mtime < os.stat(infofile).st_mtime:
                            #debug_log("removing obsolete deleted infofile %s\n" % deletedInfofile)
                            os.remove(deletedInfofile)
                        else:
                            #debug_log("reading deleted infofile %s\n" % deletedInfofile)
                            with open(deletedInfofile, 'r') as f:
                                self._deletedInfo = FilesetInfoAccumulator.fromFile(f, self._attrs)
                except IOError:
                    warning("can't read deleted info %s, ignoring" % deletedInfofile)
                    self._deletedInfo = FilesetInfoAccumulator(self._attrs)
                try:
                    with open(infofile, 'r') as f:
                        self._fileinfo = FilesetInfoAccumulator.fromFile(f, self._attrs)
                except IOError:
                    warning("can't read info %s, ignoring" % infofile)

            if self._fileinfo is not None:
                acc.accumulate(self._fileinfo)
                acc.decumulate(self._deletedInfo)
                #debug_log("FilesetCache(%s)::merge_info() done\n" % self._path)
                return True
            #debug_log("FilesetCache(%s)::merge_info() not merged yet\n" % self._path)

        #debug_log("FilesetCache(%s)::merge_info() still here\n" % self._path)
        # didn't manage to read infofile, or we need a filtered scan
        if self._next is not None:
            #debug_log("FilesetCache(%s)::merge_info() asking children\n" % self._path)
            for f, f1 in self.filtered(filter):
                f.merge_info(acc, f1)
            return True
        else:
            #debug_log("FilesetCache(%s)::merge_info() baling\n" % self._path)
            return False

    def add(self, filespec):
        if self._next is not None:
            self.filesetFor(filespec).add(filespec)
        if self._fileinfo is None:
            self._fileinfo = FilesetInfoAccumulator(self._attrs)
        self._fileinfo.add(filespec)

    def finalize(self):
        #debug_log("FilesetCache::finalize(%s)\n" % self._path)
        finalized = False
        if self._next is not None:
            for f, f1 in self.filtered(None):
                f.finalize()
                if not finalized:
                    finalized = True

        # write info file, only if a child did something
        if self._next is None or finalized:
            with open(self.infopath(), 'w') as infofile:
                if self._fileinfo is not None:
                    self._fileinfo.write(infofile)

    def delete(self, filespec):
        #debug_log("FilesetCache(%s)::delete %s\n" % (self._path, filespec.path))
        self._deletedInfo.add(filespec)
        self._ctx.pendingCaches.add(self)
        if self._parent is not None:
            self._parent.delete(filespec)

    def saveDeletions(self):
        #debug_log("FilesetCache(%s)::saveDeletions\n" % self._path)
        try:
            if not os.path.exists(self._deltadir):
                os.makedirs(self._deltadir)
        except IOError:
            warning("can't create deltadir %s, ignoring" % self._deltadir)
            return
        if self._deletedInfo.nFiles > 0:
            deletedInfofile = self.infopath(deleted=True)
            #debug_log("FilesetCache(%s)::saveDeletions deletedInfo\n" % self._path)
            try:
                with open(deletedInfofile, 'w') as f:
                    self._deletedInfo.write(f)
            except IOError:
                warning("can't write deleted info %s, ignoring" % deletedInfofile)
                self._deletedInfo = FilesetInfoAccumulator(self._attrs)
