import datetime

class CollationStack(object):
    def __init__(self, filelists, level=0):
        self._filelists = filelists
        self._level = level

    def next(self):
        if self._level < len(self._filelists):
            return self.__class__(self._filelists, self._level + 1)
        else:
            return self

    def filelist(self, path):
        if self._level < len(self._filelists):
            return self._filelists[self._level](path, self.next())
        else:
            return SimpleFilelist(path, self)
