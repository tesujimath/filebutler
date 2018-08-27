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

from builtins import object
import os.path

from .FilespecMerger import FilespecMerger

class FilesetCache(object):
    """FilesetCache is a base class."""

    def __init__(self, path, deltadir, mapper, attrs, sel, next):
        self._path = path
        self._deltadir = deltadir
        self._mapper = mapper
        self._attrs = attrs
        self._sel = sel
        self._next = next

    def infopath(self, deleted=False):
        if deleted:
            return os.path.join(self._deltadir, "deleted.info")
        else:
            return os.path.join(self._path, "info")

    def select(self, filter=None):
        merger = FilespecMerger()
        for f, f1 in self.filtered(filter):
            merger.add(f.select(f1))
        # no yield from in python 2, so:
        for filespec in merger.merge():
            yield filespec

    def merge_info(self, acc, filter=None):
        for f, f1 in self.filtered(filter):
            f.merge_info(acc, f1)
