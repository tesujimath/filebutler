import calendar
import datetime

import filebutler.Filespec
import filebutler.Localtime

class GnuFindOut(object):
    def __init__(self, filelist, fullpathfn):
        self._filelist = filelist
        self._fullpathfn = fullpathfn
        self._dateParser = self.__class__._dateParser()

    class _dateParser(object):
        """Converts find format dates into time since epoch."""
        def __init__(self):
            self._epoch = datetime.datetime.utcfromtimestamp(0)
            self._localtime = filebutler.Localtime()
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
            dt = self._localtime.datetime(year, month, int(fields[8]))
            return (dt - self._epoch).total_seconds()

    def all(self):
        with open(self._filelist) as f:
            for line in f:
                fields = line.split(None, 10)
                yield filebutler.Filespec(path=fields[10],
                                          user=fields[4],
                                          group=fields[5],
                                          size=int(fields[6]),
                                          mtime=self._dateParser.t(fields),
                                          perms=fields[2])
