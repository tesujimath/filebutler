import os.path

class SimpleFilelist(object):

    def __init__(self, path, stack):
        self._path = path
        self._filespecs = None

    def select(self, filter):
        if self._filespecs is None:
            self._filespecs = []
            with open(self._path, 'r') as f:
                for filespec in Filespec.fromFile(f):
                    self._filespecs.append(filespec)
                    yield filespec
        else:
            for filespec in self._filespecs:
                if filter.selects(filespec):
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
