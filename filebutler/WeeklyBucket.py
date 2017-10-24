import datetime

class WeeklyBucket(object):
    def __init__(self, subBucket):
        self._weeks = {}
        self._subBucket = subBucket
        self.last = None

    @classmethod
    def week(t):
        """Return time t as a week YYYYWW, integer valued."""
        dt = datetime.fromtimestamp(t)
        isoyear,isoweek,isoweekday = dt.isocalendar()
        return isoyear * 100 + isoweek

    def add(self, filespec):
        w = self.__class__.week(filespec.mtime)
        if not self._weeks.has_key(w):
            bucket = self._subBucket()
            self._weeks[w] = bucket
        else:
            bucket = self._weeks[w]
        bucket.add(filespec)

    def get(self, w):
        return self._weeks[w]

    class _iterator(object):
        def __init__(self, bucket):
            self._bucket = bucket
            self._weeks = sorted(bucket.keys())
            self._i = 0

        def next(self):
            """Return the next week's bucket."""
            if self._i >= len(self._weeks):
                return None
            w = self._weeks[self._i]
            self._i += 1
            return self._bucket.get(w)

    def __iter__(self):
        return self.__class__._iterator(self)
