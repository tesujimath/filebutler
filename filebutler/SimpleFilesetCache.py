import os.path

from Filespec import Filespec

class SimpleFilesetCache(object):

    def __init__(self, path):
        self._path = path
        self._filespecs = None

    def select(self, filter=None):
        if self._filespecs is None:
            self._filespecs = []
            with open(self._path, 'r') as f:
                for filespec in Filespec.fromFile(f):
                    self._filespecs.append(filespec)
                    #print("SimpleFilesetCache read from file %s" % filespec)
                    yield filespec
        else:
            for filespec in self._filespecs:
                if filter is None or filter.selects(filespec):
                    #print("SimpleFilesetCache read from memory %s" % filespec)
                    yield filespec

    def save(self):
        with open(self._path, 'w') as f:
            if self._filespecs is not None:
                for filespec in self._filespecs:
                    filespec.write(f)

    def add(self, filespec):
        if self._filespecs is None:
            self._filespecs = []
        self._filespecs.append(filespec)
