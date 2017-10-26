import calendar
import datetime
import re

from Filespec import Filespec
from Localtime import Localtime

class GnuFindOutFileset(object):

    @classmethod
    def parse(cls, toks):
        if len(toks) != 3:
            raise CLIError("find.gnu.out requires path, match-re, replace-str")
        path = toks[0]
        match = toks[1]
        replace = toks[2]
        return cls(path, match, replace)

    def __init__(self, path, match, replace):
        #print("GnuFindOutFileset init %s %s %s" % (path, match, replace))
        self._path = path
        self._match = match
        self._replace = replace
        self._dateParser = self.__class__._dateParser()

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
        #print("GnuFindOutFileset %s select %s" % (self._path, filter))
        with open(self._path) as f:
            for line in f:
                fields = line.rstrip().split(None, 10)
                filespec = Filespec(path=re.sub(self._match, self._replace, fields[10]),
                                    user=fields[4],
                                    group=fields[5],
                                    size=int(fields[6]),
                                    mtime=self._dateParser.t(fields),
                                    perms=fields[2])
                if filter == None or filter.selects(filespec):
                    #print("GnuFindOutFileset read from file %s" % filespec)
                    yield filespec
