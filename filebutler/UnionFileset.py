class UnionFileset(object):

    def __init__(self, filesets):
        self._filesets = filesets

    def select(self, filter=None):
        for fileset in self._filesets:
            for filespec in fileset.select(filter):
                yield filespec
