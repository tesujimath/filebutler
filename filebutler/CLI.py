import os
import os.path
import re
import readline
import shlex
import string
import sys

from Cache import Cache
from CLIError import CLIError
from GnuFindOutFileset import GnuFindOutFileset
from FilterFileset import FilterFileset
from UnionFileset import UnionFileset

class CLI:

    def __init__(self):
        self._attrs = {}
        self._filesets = {}
        self._caches = {}

    def _cached(self, name, fileset):
        if not self._attrs.has_key('cachedir'):
            raise CLIError("missing attr cachedir")
        cache = Cache(fileset, os.path.join(self._attrs['cachedir'], name))
        self._caches[name] = cache
        return cache.fileset()

    def _updateCache(self):
        for name in self._caches.keys():
            print("updating cache %s" % name)
            self._caches[name].update()

    def _expandVars(self, toks):
        """Expand environment variables in tokens."""
        for i in range(len(toks)):
            m = True
            while m:
                m = re.search(r"""\$([a-zA-Z]\w*)""", toks[i])
                if m:
                    name = m.group(1)
                    if os.environ.has_key(name):
                        val = os.environ[name]
                    else:
                        val = ""
                    toks[i] = string.replace(toks[i], "$%s" % name, val)
                    #print("matched env var %s, val='%s', token now '%s'" % (name, val, toks[i]))

    def _process(self, line):
        toks = shlex.split(line, comments=True)
        self._expandVars(toks)
        if len(toks) >= 1:
            cmd = toks[0]
            if cmd == "echo":
                print(' '.join(toks[1:]))
            elif cmd == "set":
                if len(toks) != 3:
                    raise CLIError("usage: %s <attr> <value>" % cmd)
                name = toks[1]
                value = toks[2]
                self._attrs[name] = value
            elif cmd == "ls-attrs":
                if len(toks) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._attrs.keys()):
                    print("%s=%s" % (name, self._attrs[name]))
            elif cmd == "ls-filesets":
                if len(toks) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._filesets.keys()):
                    print(name)
            elif cmd == "ls-caches":
                if len(toks) != 1:
                    raise CLIError("usage: %s" % cmd)
                for name in sorted(self._caches.keys()):
                    print(name)
            elif cmd == "fileset":
                if len(toks) < 3:
                    raise CLIError("usage: %s <name> <spec>" % cmd)
                name = toks[1]
                type = toks[2]
                if self._filesets.has_key(name):
                    raise CLIError("duplicate fileset %s" % name)
                if type == "find.gnu.out":
                    fileset = GnuFindOutFileset.parse(toks[3:])
                    self._filesets[name] = self._cached(name, fileset)
                elif type == "filter":
                    if len(toks) < 4:
                        raise CLIError("filter requires fileset, criteria")
                    filesetName = toks[3]
                    if not self._filesets.has_key(filesetName):
                        raise CLIError("no such fileset %s" % filesetName)
                    fileset = self._filesets[filesetName]
                    filter = FilterFileset.parse(fileset, toks[4:])
                    self._filesets[name] = filter
                elif type == "union":
                    if len(toks) < 4:
                        raise CLIError("union requires at least two filesets")
                    filesets = []
                    for filesetName in toks[3:]:
                        if not self._filesets.has_key(filesetName):
                            raise CLIError("no such fileset %s" % filesetName)
                        filesets.append(self._filesets[filesetName])
                    union = UnionFileset(filesets)
                    self._filesets[name] = union
            elif cmd == "print":
                if len(toks) != 2:
                    raise CLIError("usage: %s <fileset>" % cmd)
                name = toks[1]
                if not self._filesets.has_key(name):
                    raise CLIError("no such fileset %s" % name)
                fileset = self._filesets[name]
                for filespec in fileset.select():
                    print("%s" % filespec)
            elif cmd == "update-caches":
                if len(toks) != 1:
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
