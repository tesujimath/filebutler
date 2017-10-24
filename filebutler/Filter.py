import datetime

class Filter(object):
    def __init__(self, owner=None, sizeGeq=None, mtimeBefore=None):
        self.owner = owner
        self.sizeGeq = sizeGeq
        self.mtimeBefore = mtimeBefore

    def selects(self, filespec):
        if self.owner is not None and filespec.user != self.owner:
            return False
        if self.sizeGeq is not None and filespec.size < self.sizeGeq:
            return False
        if self.mtimeBefore is not None and filespec.mtime >= self.mtimeBefore:
            return False
        return True
