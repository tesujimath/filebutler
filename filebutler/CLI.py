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

import cProfile
import errno
import os
import os.path
import pstats
import re
import readline
import shlex
import string
import time

from CLIError import CLIError
from Cache import Cache
from Filter import Filter
from FilterFileset import FilterFileset
from FindFileset import FindFileset
from GnuFindOutFileset import GnuFindOutFileset
from Mapper import Mapper
from Pager import Pager
from UnionFileset import UnionFileset
from options import parseCommandOptions
from util import stderr, verbose_stderr, debug_stderr, initialize, profile

class CLI:

    def __init__(self, args):
        self._attrs = {}
        self._filesetNames = [] # in order of creation
        self._filesets = {}
        self._caches = {}
        self._now = time.time() # for consistency between all filters
        self._mapper = Mapper()
        self.commands = {
            'help':          { 'desc': 'provide help',
                               'usage': 'help',
                               'method': self._helpCmd,
            },
            'quit':          { 'desc': 'finish filebutler session',
                               'usage': 'quit (or Ctrl-D)',
                               'method': self._quitCmd,
            },
            'echo':          { 'desc': 'echo parameters after expansion',
                               'usage': 'echo <args>',
                               'method': self._echoCmd,
            },
            'set':           { 'desc': 'set attribute, e.g. cachedir',
                               'usage': 'set <attr> <values>',
                               'method': self._setCmd,
            },
            'clear':         { 'desc': 'clear attribute, e.g. print-options',
                               'usage': 'clear <attr>',
                               'method': self._clearCmd,
            },
            'ls-attrs':      { 'desc': 'list attributes',
                               'usage': 'ls-attrs',
                               'method': self._lsAttrsCmd,
            },
            'ls':            { 'desc': 'list filesets',
                               'usage': 'ls',
                               'method': self._lsCmd,
            },
            'ls-caches':     { 'desc': 'list caches',
                               'usage': 'ls-caches',
                               'method': self._lsCachesCmd,
            },
            'fileset':       { 'desc': 'define a fileset',
                               'usage': 'fileset find.gnu.out|find|filter|union <name> <spec>',
                               'method': self._filesetCmd,
            },
            'info':          { 'desc': 'show summary information for a fileset',
                               'usage': 'info <fileset> [-u|-d]',
                               'method': self._infoCmd,
            },
            'print':         { 'desc': 'print files in a fileset, optionally filtered, via $PAGER',
                               'usage': 'print <fileset> [<filter-params>] [-by-path|-by-size]',
                               'method': self._printCmd,
            },
            'delete':        { 'desc': 'delete all files in a fileset',
                               'usage': 'delete <fileset>',
                               'method': self._deleteCmd,
            },
            'update-cache':  { 'desc': 'update all caches, by rescanning source filelists',
                               'usage': 'update-cache',
                               'method': self._updateCacheCmd,
            },
        }
        initialize(args)

    def _cached(self, name, fileset):
        if not self._attrs.has_key('cachedir'):
            raise CLIError("missing attr cachedir")
        cachedirs = self._attrs['cachedir']
        if len(cachedirs) != 1:
            raise CLIError("botched attr cachedir")
        cachedir = cachedirs[0]
        if not self._attrs.has_key('logdir'):
            raise CLIError("missing attr logdir")
        logdirs = self._attrs['logdir']
        if len(logdirs) != 1:
            raise CLIError("botched attr logdir")
        logdir = logdirs[0]
        cache = Cache(name, fileset,
                      os.path.join(cachedir, name),
                      os.path.join(logdir, name))
        self._caches[name] = cache
        return cache

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

    def _cache(self, name):
        if not self._caches.has_key(name):
            raise CLIError("no such cache %s" % name)
        return self._caches[name]

    def _process(self, line):
        done = False
        toks = shlex.split(line, comments=True)
        self._expandVars(toks)
        if len(toks) >= 1:
            cmdName = toks[0]
            if self.commands.has_key(cmdName):
                cmd = self.commands[cmdName]
                method = cmd['method']
                usage = cmd['usage']
                if profile():
                    pr = cProfile.Profile()
                    pr.enable()
                method(toks, usage)
                if profile():
                    pr.disable()
                    ps = pstats.Stats(pr).sort_stats('cumulative')
                    ps.print_stats()
                done = method == self._quitCmd
            else:
                raise CLIError("unknown command %s, try help" % cmdName)
        return done

    def _handleProcess(self, line):
        done = False
        try:
            done = self._process(line)
        except CLIError as e:
            stderr("ERROR %s\n" % e.msg)
        except KeyboardInterrupt:
            stderr("\n")
        return done

    def startup(self):
        for rc in ["/etc/filebutlerrc",
                   os.path.expanduser("~/.filebutlerrc")]:
            try:
                with open(rc) as f:
                    for line in f:
                        self._handleProcess(line)
            except IOError:
                pass

    def execute(self, cmds):
        for cmd in cmds:
            self._handleProcess(cmd)

    def interact(self):
        done = False
        while not done:
            try:
                line = raw_input("fb: ")
                done = self._handleProcess(line)
            except EOFError:
                print("bye")
                done = True
            except KeyboardInterrupt:
                stderr("^C\n")

    def _helpCmd(self, toks, usage):
        for cmdname in sorted(self.commands.keys()):
            cmd = self.commands[cmdname]
            print("%-10s - %s\n               %s\n" % (cmdname, cmd['desc'], cmd['usage']))

    def _quitCmd(self, toks, usage):
        pass

    def _echoCmd(self, toks, usage):
        print(' '.join(toks[1:]))

    def _setCmd(self, toks, usage):
        if len(toks) < 3:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        values = toks[2:]
        self._attrs[name] = values
        if name == 'dataset':
            if len(values) != 2:
                raise CLIError("botched attr dataset")
            self._mapper.setDatasetRegex(values[0], values[1])

    def _clearCmd(self, toks, usage):
        if len(toks) != 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        del self._attrs[name]
        if name == 'dataset':
            self._mapper.clearDatasetRegex()

    def _lsAttrsCmd(self, toks, usage):
        if len(toks) != 1:
            raise CLIError("usage: %s" % usage)
        for name in sorted(self._attrs.keys()):
            print("%s = %s" % (name, ' '.join(self._attrs[name])))

    def _lsCmd(self, toks, usage):
        if len(toks) != 1:
            raise CLIError("usage: %s" % usage)
        for name in self._filesetNames:
            print(self._filesets[name].description())

    def _lsCachesCmd(self, toks, usage):
        if len(toks) != 1:
            raise CLIError("usage: %s" % usage)
        for name in self._filesetNames:
            if self._caches.has_key(name):
                print(self._filesets[name].description())

    def _filesetCmd(self, toks, usage):
        if len(toks) < 3:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        type = toks[2]
        if self._filesets.has_key(name):
            raise CLIError("duplicate fileset %s" % name)
        if type == "find.gnu.out":
            fileset = self._cached(name, GnuFindOutFileset.parse(self._mapper, name, toks[3:]))
        elif type == "find":
            fileset = self._cached(name, FindFileset.parse(self._mapper, name, toks[3:]))
        elif type == "filter":
            if len(toks) < 4:
                raise CLIError("filter requires fileset, criteria")
            filter, _ = parseCommandOptions(self._now, toks[4:], filter=True)
            fileset = FilterFileset(name, self._fileset(toks[3]), filter)
        elif type == "union":
            if len(toks) < 4:
                raise CLIError("union requires at least two filesets")
            filesets = []
            for filesetName in toks[3:]:
                filesets.append(self._fileset(filesetName))
            fileset = UnionFileset(name, filesets)
        else:
            raise CLIError("unknown fileset type %s" % type)
        self._filesets[name] = fileset
        self._filesetNames.append(name)

    def _infoCmd(self, toks, usage):
        if len(toks) < 2 or len(toks) > 3:
            raise CLIError("usage: %s" % usage)
        if len(toks) == 2:
            print(self._fileset(toks[1]).info())
        elif toks[1] == '-u':
            print(self._fileset(toks[2]).info().users())
        elif toks[1] == '-d':
            print(self._fileset(toks[2]).info().datasets())
        else:
            raise CLIError("usage: %s" % usage)

    def _printCmd(self, toks, usage):
        if len(toks) < 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        fileset = self._fileset(name)
        if self._attrs.has_key('print-options'):
            printOptions = toks[2:] + self._attrs['print-options']
        else:
            printOptions = toks[2:]
        if printOptions != []:
            filter, sorter = parseCommandOptions(self._now, printOptions, filter=True, sorter=True)
        else:
            filter, sorter = None, None
        pager = Pager()
        width = 0
        try:
            for filespec in fileset.sorted(filter, sorter):
                s, width = filespec.format(width)
                pager.file.write("%s\n" % s)
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
            else:
                raise
        finally:
            pager.close()

    def _deleteCmd(self, toks, usage):
        if len(toks) != 2 :
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        fileset = self._fileset(name)
        # delete directories after their contents
        dirs = []
        mtimes = {}
        for filespec in fileset.select():
            # preserve mtime for parent directory
            parent = os.path.dirname(filespec.path)
            if not mtimes.has_key(parent):
                mtimes[parent] = os.stat(parent).st_mtime
            if filespec.isdir():
                dirs.append(filespec)
            else:
                filespec.delete()
        for filespec in sorted(dirs, key=lambda d: d.path, reverse=True):
            filespec.delete()
        # now reset mtimes of anything that's left
        for path, mtime in mtimes.iteritems():
            try:
                os.utime(path, (mtime, mtime))
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # silently do nothing if there's no directory left
                    pass
                elif e.errno == errno.EACCES:
                    # silently do nothing if we don't have permission to fix mtime
                    pass
                else:
                    raise
        # finally save deletions lists for all caches
        for name in self._caches:
            self._caches[name].saveDeletions()

    def _updateCacheCmd(self, toks, usage):
        if len(toks) == 1:
            for name in self._caches.keys():
                #print("updating cache %s" % name)
                self._caches[name].update()
        else:
            for name in toks[1:]:
                self._cache(name).update()
