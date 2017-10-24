import datetime
import pytz
import tzlocal

class Localtime(object):
    def __init__(self):
        self._localtimezone = pytz.timezone(str(tzlocal.get_localzone()))

    def datetime(self, *args):
        return datetime.datetime(*args)
