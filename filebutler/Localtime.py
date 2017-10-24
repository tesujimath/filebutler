import datetime
import pytz
import tzlocal

class Localtime(object):
    def __init__(self):
        self._epoch = datetime.datetime.utcfromtimestamp(0)
        self._localtimezone = pytz.timezone(str(tzlocal.get_localzone()))

    def datetime(self, *args):
        return datetime.datetime(*args)

    def t(self, *args):
        dt = self.datetime(*args)
        return (dt - self._epoch).total_seconds()
