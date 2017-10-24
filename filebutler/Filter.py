import datetime

class Filter(object):
    def __init__(self):
        self.owner = None
        self.mtimeBefore = None

    def selectMtimeBefore(self, t):
        self.mtimeBefore = t

    def selectOwner(self, owner):
        self.owner = owner
