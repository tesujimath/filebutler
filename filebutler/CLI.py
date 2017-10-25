import os.path
import readline
import shlex
import sys

from Cache import Cache
from CLIError import CLIError
from GnuFindOutFileset import GnuFindOutFileset

class CLI:

    def __init__(self):
        self._attrs = {}
        self._filesets = {}
        self._caches = {}

    def _cached(self, name, filelist):
        if not self._attrs.has_key('cachedir'):
            raise CLIError("missing attr cachedir")
        cache = Cache(filelist, os.path.join(self._attrs['cachedir'], name))
        self._caches[name] = cache
        return cache.filelist()

    def _updateCache(self):
        for name in self._caches.keys():
            print("updating cache %s" % name)
            self._caches[name].update()

    def _process(self, line):
        tok = shlex.split(line, comments=True)
        if len(tok) >= 1:
            cmd = tok[0]
            if cmd == "set":
                if len(tok) != 3:
                    raise CLIError("usage: %s <attr> <value>" % cmd)
                name = tok[1]
                value = tok[2]
                self._attrs[name] = value
            elif cmd == "ls-attrs":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._attrs.keys()):
                    print("%s=%s" % (name, self._attrs[name]))
            elif cmd == "ls-filesets":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._filesets.keys()):
                    print(name)
            elif cmd == "ls-caches":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._caches.keys()):
                    print(name)
            elif cmd == "fileset":
                if len(tok) < 3:
                    raise CLIError("usage: %s <name> <spec>" % cmd)
                name = tok[1]
                type = tok[2]
                if type == "find.gnu.out":
                    fileset = GnuFindOutFileset.parse(tok[3:])
                    for filespec in fileset.select():
                        print("%s" % filespec)
                    self._filesets[name] = self._cached(name, fileset)
                # elif type == "filter":
                #     if len(tok) < 4:
                #         raise CLIError("filter requires fileset, criteria")
                #     filterName = tok[2]
                #     filesetName = tok[3]
                #     if not self._filesets.has_key(filesetName):
                #         raise CLIError("no such fileset %s" % filesetName)
                #     fileset = self._filesets[filesetName]
                #     filter = FilterFileset.parse(fileset, tok[4:])
                #     self._filesets[name] = filter
            elif cmd == "update-caches":
                if len(tok) != 1:
                    raise CLIError("usage: %s" % cmd)
                self._updateCache()
            else:
                raise CLIError("unknown command %s" % cmd)

    def _handleProcess(self, line):
        try:
            self._process(line)
        except CLIError as e:
            sys.stderr.write("ERROR %s\n" % e.msg)

    def interact(self):
        # startup files
        for rc in ["/etc/filebutlerrc",
                   os.path.expanduser("~/.filebutlerrc"),
                   os.path.expanduser("~/projects/filebutler/examples/dotfilebutlerrc")]:
            try:
                with open(rc) as f:
                    for line in f:
                        self._handleProcess(line)
            except IOError:
                pass

        done = False
        while not done:
            try:
                line = raw_input("fb: ")
                self._handleProcess(line)
            except EOFError:
                print("bye")
                done = True
