from __future__ import absolute_import
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

from builtins import str
from builtins import object
import os.path

from .Filespec import Filespec
from .FilesetInfo import FilesetInfo
from .PooledFile import PooledFile
from .util import filetimestr, verbose_stderr, debug_log, warning

class SimpleFilesetCache(object):

    def __init__(self, path, deltadir, mapper, attrs, sel):
        #debug_log("SimpleFilesetCache(%s)::__init__)\n" % path)
        self._path = path
        self._deltadir = deltadir
        self._mapper = mapper
        self._attrs = attrs
        self._sel = sel
        self._filespecs = []    # in-memory read cache
        self._info = {}         # indexed by filter string
        self._file = None
        self._filepos = 0
        self._fileinfo = None
        self._deletedFilelist = {}    # paths of deleted files
        self._deletedInfo = FilesetInfo()

    def filelistpath(self, deleted=False):
        if deleted:
            return os.path.join(self._deltadir, "deleted.filelist")
        else:
            return os.path.join(self._path, "filelist")

    def infopath(self, deleted=False):
        if deleted:
            return os.path.join(self._deltadir, "deleted.info")
        else:
            return os.path.join(self._path, "info")

    def select(self, filter=None, includeDeleted=False):
        # first read from in-memory cache, which may be empty, or partial if last file read was interrupted
        #debug_log("SimpleFilesetCache select %s from memory cache\n" % str(filter))
        for filespec in self._filespecs:
            if includeDeleted or filespec.path not in self._deletedFilelist:
                if filter is None or filter.selects(filespec):
                    #debug_log("SimpleFilesetCache read from memory %s\n" % filespec)
                    yield filespec

        # now read from file, unless this is complete
        if self._filepos is not None:
            #debug_log("reading filelist from %s cache at %s\n" % (filetimestr(self._path), self._path))
            #debug_log("SimpleFilesetCache(%s) select %s from file cache %s\n" % (self._path, str(filter), self._path))
            self._deletedFilelist = {}
            filelist = self.filelistpath()
            deletedFilelist = self.filelistpath(deleted=True)
            try:
                if os.path.exists(deletedFilelist):
                    # if deleted filelist is older than cache, remove it
                    if os.stat(deletedFilelist).st_mtime < os.stat(filelist).st_mtime:
                        #debug_log("removing obsolete deleted filelist %s\n" % deletedFilelist)
                        os.remove(deletedFilelist)
                    else:
                        #debug_log("reading deleted filelist %s\n" % deletedFilelist)
                        with open(deletedFilelist, 'r') as f:
                            for line in f:
                                self._deletedFilelist[line.rstrip('\n')] = True
            except IOError:
                warning("can't read deleted filelist %s, ignoring" % deletedFilelist)
            try:
                with PooledFile(filelist, 'r') as f:
                    if self._filepos != 0:
                        f.seek(self._filepos)
                    #debug_log("SimpleFilesetCache(%s) select %s opened file cache as %s at %d\n" % (self._path, filter, f, self._filepos))
                    try:
                        for filespec in Filespec.fromFile(f, self, self._sel):
                            self._filespecs.append(filespec)
                            if includeDeleted or filespec.path not in self._deletedFilelist:
                                if filter is None or filter.selects(filespec):
                                    #debug_log("SimpleFilesetCache read from file %s\n" % filespec)
                                    yield filespec
                    except:
                        # on any error save the filepos
                        self._filepos = f.tell()
                        #debug_log("SimpleFilesetCache(%s) exception, saving filepos at %d\n" % (self._path, self._filepos))
                        raise
                    # reading file is complete
                    self._filepos = None
            except IOError:
                warning("can't read filelist %s, ignoring" % filelist)

    def merge_info(self, acc, filter=None):
        #debug_log("SimpleFilesetCache(%s) merge_info\n" % self._path)
        if filter is None:
            #debug_log("SimpleFilesetCache(%s)::merge_info(None)\n" % self._path)
            if self._fileinfo is None:
                #debug_log("SimpleFilesetCache(%s)::merge_info(None) reading info file\n" % self._path)
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
                                self._deletedInfo = FilesetInfo.fromFile(f)
                except IOError:
                    warning("can't read deleted info %s, ignoring" % deletedInfofile)
                    self._deletedInfo = FilesetInfo()
                try:
                    with open(infofile, 'r') as f:
                        self._fileinfo = FilesetInfo.fromFile(f)
                except IOError:
                    warning("can't read info %s, ignoring" % infofile)
                    self._fileinfo = FilesetInfo()
            info = self._fileinfo
        else:
            f = str(filter)
            #debug_log("SimpleFilesetCache(%s)::merge_info(%s)\n" % (self._path, f))
            if f in self._info:
                info = self._info[f]
            else:
                #debug_log("SimpleFilesetCache(%s)::merge_info(%s) scanning\n" % (self._path, f))
                info = FilesetInfo()
                self._info[f] = info
                for filespec in self.select(filter, includeDeleted=True):
                    info.add(1, filespec.size)
        acc.accumulate(info, self._sel)
        acc.decumulate(self._deletedInfo, self._sel)

    def add(self, filespec):
        if self._fileinfo is None:
            self._fileinfo = FilesetInfo()
        self._fileinfo.add(1, filespec.size)
        # don't cache writes, as this would mean caching the whole of the filelist
        if self._file is None:
            #debug_log("SimpleFilesetCache writing file cache at %s\n" % self._path)
            if not os.path.exists(self._path):
                os.makedirs(self._path)
            self._file = PooledFile(self.filelistpath(), 'w')
        filespec.write(self._file)

    def finalize(self):
        """Finalize writing the cache."""
        if self._file is not None:
            self._file.close()
            self._file = None

        # sort the filelist
        with open(self.filelistpath()) as f:
            sorted_filelist = sorted(f, key=Filespec.formattedToPath)
        with open(self.filelistpath(), 'w') as f:
            f.writelines(sorted_filelist)

        # write info file
        with open(self.infopath(), 'w') as infofile:
            if self._fileinfo is not None:
                self._fileinfo.write(infofile)

    def delete(self, filespec):
        #debug_log("SimpleFilesetCache(%s) delete %s\n" % (self._path, filespec.path))
        self._deletedFilelist[filespec.path] = True
        self._deletedInfo.add(1, filespec.size)

    def saveDeletions(self):
        if len(self._deletedFilelist) > 0:
            deletedFilelist = self.filelistpath(deleted=True)
            #debug_log("SimpleFilesetCache(%s)::saveDeletions deletedFilelist\n" % self._path)
            try:
                if not os.path.exists(self._deltadir):
                    os.makedirs(self._deltadir)
                with open(deletedFilelist, 'w') as f:
                    for path in self._deletedFilelist:
                        f.write("%s\n" % path)
            except IOError:
                warning("can't write deleted filelist %s, ignoring" % deletedFilelist)

        if self._deletedInfo.nFiles > 0:
            deletedInfofile = self.infopath(deleted=True)
            #debug_log("SimpleFilesetCache(%s)::saveDeletions deletedInfo\n" % self._path)
            try:
                with open(deletedInfofile, 'w') as f:
                    self._deletedInfo.write(f)
            except IOError:
                warning("can't write deleted info %s, ignoring" % deletedInfofile)
                self._deletedInfo = FilesetInfo()
