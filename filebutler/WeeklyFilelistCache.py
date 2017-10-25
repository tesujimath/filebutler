import datetime
import os.path

class WeeklyFilelistCache(object):

    @classmethod
    def week(cls, t):
        """Return time t as an integer valued week YYYYWW."""
        dt = datetime.datetime.fromtimestamp(t)
        isoyear,isoweek,isoweekday = dt.isocalendar()
        return isoyear * 100 + isoweek

    def __init__(self, path, next):
        self._path = path
        self._next = next
        self._weeks = {}        # of filelist, indexed by integer week

        # load stubs for all weeks found
        if os.path.exists(self._path):
            for wstr in os.listdir(self._path):
                w = int(wstr)
                self._weeks[w] = None # stub

    def _subpath(self, w):
        return os.path.join(self._path, str(w))

    def _filelist(self, w):
        """On demand creation of child filelists."""
        if self._weeks.has_key(w):
            filelist = self._weeks[w]
        else:
            filelist = None
        if filelist is None:
            filelist = self._next(self._subpath(w))
            self._weeks[w] = filelist
        return filelist

    def select(self, filter):
        weeks = sorted(self._weeks.keys())
        for w in weeks:
            if filter.mtimeBefore is None or w <= self.__class__.week(filter.mtimeBefore):
                # no yield from in python 2, so:
                for filespec in self._filelist(w).select(filter):
                    yield filespec

    def save(self):
        if not os.path.exists(self._path):
            os.makedirs(self._path)
        for filelist in self._weeks.values():
            filelist.save()

    def add(self, filespec):
        w = self.__class__.week(filespec.mtime)
        filelist = self._filelist(w)
        filelist.add(filespec)

