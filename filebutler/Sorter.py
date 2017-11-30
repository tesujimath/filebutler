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

class Sorter(object):

    def __init__(self, byPath=False, bySize=False):
        self.byPath = byPath
        self.bySize = bySize

    def key(self):
        if self.byPath:
            return lambda fs: fs.path
        elif self.bySize:
            # negate size, so we sort largest first
            return lambda fs: -fs.size
        else:
            return lambda fs: 0
