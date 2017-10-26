import datetime
import os.path
import re
import shutil
import sys

class WeeklyFilesetCache(object):

    @classmethod
    def week(cls, t):
        """Return time t as an integer valued week YYYYWW."""
        dt = datetime.datetime.fromtimestamp(t)
        isoyear,isoweek,isoweekday = dt.isocalendar()
        return isoyear * 100 + isoweek

    def __init__(self, path, next):
        self._path = path
        self._next = next
        self._weeks = {}        # of fileset, indexed by integer week

        # load stubs for all weeks found
        if os.path.exists(self._path):
            for wstr in os.listdir(self._path):
                w = int(wstr)
                self._weeks[w] = None # stub

    def _subpath(self, w):
        return os.path.join(self._path, str(w))

    def _fileset(self, w):
        """On demand creation of child filesets."""
        if self._weeks.has_key(w):
            fileset = self._weeks[w]
        else:
            fileset = None
        if fileset is None:
            fileset = self._next(self._subpath(w))
            self._weeks[w] = fileset
        return fileset

    def select(self, filter=None):
        weeks = sorted(self._weeks.keys())
        for w in weeks:
            if filter is None or filter.mtimeBefore is None or w <= self.__class__.week(filter.mtimeBefore):
                # no yield from in python 2, so:
                for filespec in self._fileset(w).select(filter):
                    yield filespec

    def save(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        for fileset in self._weeks.values():
            fileset.save()

    def add(self, filespec):
        w = self.__class__.week(filespec.mtime)
        fileset = self._fileset(w)
        fileset.add(filespec)

    def purge(self):
        """Delete all cache files from disk."""
        # For safety in case of misconfiguration, we only delete directories in the format YYYYWW
        YYYYWW = re.compile(r"""^\d\d\d\d\d\d$""")
        for x in os.listdir(self._path):
            px = os.path.join(self._path, x)
            if YYYYWW.match(x):
                shutil.rmtree(px)
            else:
                sys.stderr.write("WARNING: cache purge ignoring %s\n" % px)
