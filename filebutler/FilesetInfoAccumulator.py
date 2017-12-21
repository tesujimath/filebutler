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

from util import size2str, warning
from FilesetInfo import FilesetInfo

class FilesetInfoAccumulator(object):

    def __init__(self, nFiles=0, totalSize=0):
        self._total = FilesetInfo(nFiles, totalSize)
        self._users = {}
        self._datasets = {}

    def add(self, filespec):
        self._total.add(1, filespec.size)
        if self._users.has_key(filespec.user):
            user = self._users[filespec.user]
        else:
            user = FilesetInfo()
            self._users[filespec.user] = user
        user.add(1, filespec.size)
        if self._datasets.has_key(filespec.dataset):
            dataset = self._datasets[filespec.dataset]
        else:
            dataset = FilesetInfo()
            self._datasets[filespec.dataset] = dataset
        dataset.add(1, filespec.size)

    def accumulate(self, info, sel):
        self._total.add(info.nFiles, info.totalSize)
        if sel.owner is not None:
            if not self._users.has_key(sel.owner):
                user0 = FilesetInfo()
                self._users[sel.owner] = user0
            else:
                user0 = self._users[sel.owner]
            user0.add(info.nFiles, info.totalSize)
        if sel.dataset is not None:
            if not self._datasets.has_key(sel.dataset):
                dataset0 = FilesetInfo()
                self._datasets[sel.dataset] = dataset0
            else:
                dataset0 = self._datasets[sel.dataset]
            dataset0.add(info.nFiles, info.totalSize)

    def decumulate(self, info, sel):
        self._total.remove(info.nFiles, info.totalSize)
        if sel.owner is not None:
            if self._users.has_key(sel.owner):
                user0 = self._users[sel.owner]
                user0.remove(info.nFiles, info.totalSize)
                if user0.nFiles == 0:
                    # remove user, since no files left
                    self._users.pop(sel.owner, None)
        if sel.dataset is not None:
            if self._datasets.has_key(sel.dataset):
                dataset0 = self._datasets[sel.dataset]
                dataset0.remove(info.nFiles, info.totalSize)
                if dataset0.nFiles == 0:
                    # remove dataset, since no files left
                    self._datasets.pop(sel.dataset, None)

    def fmt_total(self):
        return "total %s" % str(self._total)

    def fmt_users(self):
        lines = [self.fmt_total()]
        for user in sorted(self._users.items(), key=lambda u: u[1].totalSize, reverse=True):
            name = user[0]
            info = user[1]
            # exclude trivial small stuff
            if info.totalSize > 1024:
                lines.append("%s %s" % (name, str(info)))
        return '\n'.join(lines)

    def iterusers(self):
        return self._users.iteritems()

    def fmt_datasets(self):
        lines = [self.fmt_total()]
        for dataset in sorted(self._datasets.items(), key=lambda u: u[1].totalSize, reverse=True):
            name = dataset[0]
            info = dataset[1]
            # exclude trivial small stuff
            if info.totalSize > 1024:
                lines.append("%s %s" % (name, str(info)))
        return '\n'.join(lines)
