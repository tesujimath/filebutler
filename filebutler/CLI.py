# Copyright 2017 Simon Guest
#
# This file is part of filebutler.
#
# Filebutler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Filebutler is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with filebutler.  If not, see <http://www.gnu.org/licenses/>.

import os
import os.path
import re
import readline
import shlex
import string
import time

from CLIError import CLIError
from Cache import Cache
from FilterFileset import FilterFileset
from FindFileset import FindFileset
from GnuFindOutFileset import GnuFindOutFileset
from UnionFileset import UnionFileset
from util import stderr

class CLI:

    def __init__(self, args):
        self._args = args
        self._attrs = {}
        self._filesets = {}
        self._caches = {}
        self._now = time.time() # for consistency between all filters

    def _cached(self, name, fileset):
        if not self._attrs.has_key('cachedir'):
            raise CLIError("missing attr cachedir")
        cache = Cache(name, fileset, os.path.join(self._attrs['cachedir'], name))
        self._caches[name] = cache
        return cache

    def _updateCache(self):
        for name in self._caches.keys():
            #print("updating cache %s" % name)
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

    def _fileset(self, name):
        if not self._filesets.has_key(name):
            raise CLIError("no such fileset %s" % name)
        return self._filesets[name]

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
                    fileset = GnuFindOutFileset.parse(toks[1], toks[3:])
                    self._filesets[name] = self._cached(name, fileset)
                elif type == "find":
                    fileset = FindFileset.parse(toks[1], toks[3:])
                    self._filesets[name] = self._cached(name, fileset)
                elif type == "filter":
                    if len(toks) < 4:
                        raise CLIError("filter requires fileset, criteria")
                    filesetName = toks[3]
                    filter = FilterFileset.parse(self._fileset(filesetName), self._now, toks[4:])
                    self._filesets[name] = filter
                elif type == "union":
                    if len(toks) < 4:
                        raise CLIError("union requires at least two filesets")
                    filesets = []
                    for filesetName in toks[3:]:
                        filesets.append(self._fileset(filesetName))
                    union = UnionFileset(filesets)
                    self._filesets[name] = union
                else:
                    raise CLIError("unknown fileset type %s" % type)
            elif cmd == "info":
                if len(toks) < 2 or len(toks) > 3 or len(toks) == 3 and toks[1] != '--users':
                    raise CLIError("usage: %s [--users] <fileset>" % cmd)
                if len(toks) == 2:
                    print(self._fileset(toks[1]).info())
                else:
                    print(self._fileset(toks[2]).info().users())
            elif cmd == "print":
                if len(toks) != 2:
                    raise CLIError("usage: %s <fileset>" % cmd)
                name = toks[1]
                for filespec in self._fileset(name).select():
                    print(filespec)
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
            stderr("ERROR %s\n" % e.msg)

    def startup(self):
        for rc in ["/etc/filebutlerrc",
                   os.path.expanduser("~/.filebutlerrc"),
                   os.path.expanduser("~/projects/filebutler/examples/dotfilebutlerrc")]:
            try:
                with open(rc) as f:
                    for line in f:
                        self._handleProcess(line)
            except IOError:
                pass

    def commands(self, cmds):
        for cmd in cmds:
            self._handleProcess(cmd)

    def interact(self):
        done = False
        while not done:
            try:
                line = raw_input("fb: ")
                self._handleProcess(line)
            except EOFError:
                print("bye")
                done = True
