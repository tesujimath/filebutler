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

import calendar
import datetime
import os
import re

from .Fileset import Fileset
from .Filespec import Filespec
from .Localtime import Localtime
from .PercentageProgress import PercentageProgress
from .CLIError import CLIError
from .util import warning, verbose_stderr

class GnuFindOutFileset(Fileset):

    @classmethod
    def parse(cls, ctx, name, toks):
        if len(toks) != 3:
            raise CLIError("find.gnu.out requires path, match-re, replace-str")
        path = toks[0]
        match = toks[1]
        replace = toks[2]
        return cls(ctx, name, path, match, replace)

    def __init__(self, ctx, name, path, match, replace):
        #print("GnuFindOutFileset init %s %s %s" % (path, match, replace))
        super(self.__class__, self).__init__()
        self._ctx = ctx
        self.name = name
        self._path = path
        self._match = match
        self._replace = replace
        self._dateParser = self.__class__._dateParser()

    def description(self):
        return "%s filelist %s" % (self.name, self._path)

    class _dateParser(object):
        """Converts find format dates into time since epoch."""
        def __init__(self):
            self._localtime = Localtime()
            self._monthNumbers = {}  # indexed by month_abbr, of 1 to 12
            for i in range(12):
                #print calendar.month_abbr[i + 1], i + 1
                self._monthNumbers[calendar.month_abbr[i + 1]] = i + 1
            self._today = datetime.datetime.today()
            #print "today", self._today.year, self._today.month, self._today.day

        def t(self, fields): # fields are as returned by find -ls, so date is in 7, 8, 9.
            month = self._monthNumbers[fields[7]]
            #print "month", month
            if len(fields[9]) == 4:
                #print "third field is year"
                year = int(fields[9])
            else:
                #print "third field is time-of-day"
                if month <= self._today.month:
                    #print "this year"
                    year = self._today.year
                else:
                    #print "last year"
                    year = self._today.year - 1
            #print "year", year
            return self._localtime.t(year, month, int(fields[8]))

    def select(self, filter=None):
        verbose_stderr("fileset %s reading from filelist %s\n" % (self.name, self._path))
        try:
            filesize = os.stat(self._path).st_size
        except OSError as e:
            warning("fileset %s ignoring unreadable filelist %s: %s" % (self.name, self._path, e.strerror))
            return
        progress = PercentageProgress("reading %s" % self._path)
        n_read = 0
        with open(self._path) as f:
            for line in f:
                n_read += len(line)
                progress.report(n_read * 1.0 / filesize)
                fields = line.rstrip().split(None, 10)
                if len(fields) > 10:
                    path = re.sub(self._match, self._replace, fields[10])
                    # strip out symlink destination
                    symlink = path.find(' -> ')
                    if symlink >= 0:
                        path = path[:symlink]
                    filespec = Filespec(fileset=self,
                                        dataset=self._ctx.pathway.datasetFromPath(path),
                                        path=path,
                                        user=self._ctx.mapper.usernameFromString(fields[4]),
                                        group=self._ctx.mapper.groupnameFromString(fields[5]),
                                        size=int(fields[6]),
                                        mtime=self._dateParser.t(fields),
                                        perms=fields[2])
                    if (filter == None or filter.selects(filespec)) and not self._ctx.pathway.ignored(filespec.path):
                        #print("GnuFindOutFileset read from file %s" % filespec)
                        yield filespec
        progress.complete()
