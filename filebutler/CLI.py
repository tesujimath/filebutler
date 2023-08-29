# Copyright 2017-2018 Simon Guest
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
import email.mime.text
import errno
import os
import os.path
import pstats
import re
import shlex
import smtplib
import string
import sys
import time
import traceback

from .CLICompleter import CLICompleter
from .CLIError import CLIError
from .CondaEnvCounter import CondaEnvCounter
from .ConfigError import ConfigError
from .Cache import Cache
from .Context import Context
from .DeletionLog import DeletionLog
from .Filter import Filter
from .FilterFileset import FilterFileset
from .FindFileset import FindFileset
from .GnuFindOutFileset import GnuFindOutFileset
from .Grouper import Grouper
from .Pager import Pager
from .UnionFileset import UnionFileset
from .aliases import read_etc_aliases
from .options import parseCommandOptions
from .util import stderr, debug_log, initialize, profile, unix_time, yes_or_no, daystart

class CLI(object):

    def __init__(self, args):
        self._attrs = {}
        self._filesetNames = [] # in order of creation
        self._filesets = {}
        self._caches = {}
        self._daystart = daystart() # for consistency between all filters
        self._ctx = Context()
        self._aliases = read_etc_aliases()
        self._commandLoc = None
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
                               'usage': 'fileset <name> find.gnu.out|find|filter|union <spec>',
                               'method': self._filesetCmd,
            },
            'info':          { 'desc': 'show summary information for a fileset',
                               'usage': 'info [-u|-d|-e|-s] <fileset> [<filter-params>]',
                               'method': self._infoCmd,
            },
            'print':         { 'desc': 'print files in a fileset, optionally filtered, via $PAGER',
                               'usage': 'print <fileset> [<filter-params>] [-by-size] [-depth <depth>]',
                               'method': self._printCmd,
            },
            'dump-conda':    { 'desc': 'dump conda environments in a fileset into file',
                               'usage': 'dump-conda <fileset> <file>',
                               'method': self._dumpCondaCmd,
            },
            'delete':        { 'desc': 'delete all files in a fileset, optionally filtered',
                               'usage': 'delete <fileset> [<filter-params>] [-y]',
                               'method': self._deleteCmd,
            },
            'source':        { 'desc': 'source commands from given file',
                               'usage': 'source <filepath>',
                               'method': self._sourceCmd,
            },
            'symlinks':      { 'desc': 'print symlinks pointing at target path, optionally recursively',
                               'usage': 'symlinks [-r] <target-path>',
                               'method': self._symlinksCmd,
            },
            'update-cache':  { 'desc': 'update all or named caches, by rescanning source filelists',
                               'usage': 'update-cache [<fileset> ...]',
                               'method': self._updateCacheCmd,
            },
            'send-emails':   { 'privileged': True,
                               'desc': 'send emails to owners in fileset, using named template',
                               'usage': 'send-emails <fileset> <email-template> [<override-recipient>]',
                               'method': self._sendEmailsCmd,
            },
        }
        initialize(args)
        self._config = args.config
        self._completer = CLICompleter(self)

    @property
    def filesetNames(self):
        return self._filesets.keys()

    def _cached(self, name, fileset):
        if 'cachedir' not in self._attrs:
            raise CLIError("missing attr cachedir")
        cachedirs = self._attrs['cachedir']
        if len(cachedirs) != 1:
            raise CLIError("botched attr cachedir")
        cachedir = cachedirs[0]
        if 'deltadir' not in self._attrs:
            raise CLIError("missing attr deltadir")
        deltadirs = self._attrs['deltadir']
        if len(deltadirs) != 1:
            raise CLIError("botched attr deltadir")
        deltadir = deltadirs[0]
        cache = Cache(name, fileset,
                      os.path.join(cachedir, name),
                      os.path.join(deltadir, name),
                      self._ctx,
                      self._attrs)
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
                    if name in os.environ:
                        val = os.environ[name]
                    else:
                        val = ""
                    toks[i] = toks[i].replace("$%s" % name, val)
                    #print("matched env var %s, val='%s', token now '%s'" % (name, val, toks[i]))

    def _fileset(self, name):
        if name not in self._filesets:
            raise CLIError("no such fileset %s" % name)
        return self._filesets[name]

    def _cache(self, name):
        if name not in self._caches:
            raise CLIError("no such cache %s" % name)
        return self._caches[name]

    def _process(self, line):
        done = False
        toks = shlex.split(line, comments=True)
        self._expandVars(toks)
        if len(toks) >= 1:
            timeCommand = toks[0] == 'time'
            if timeCommand:
                toks = toks[1:]
            cmdName = toks[0]
            if cmdName in self.commands:
                cmd = self.commands[cmdName]
                method = cmd['method']
                usage = cmd['usage']
                privileged = cmd['privileged'] if 'privileged' in cmd else False
                if privileged and os.geteuid() != 0:
                    raise CLIError("attempt to use privileged command %s" % toks[0])
                if profile():
                    pr = cProfile.Profile()
                    pr.enable()
                if timeCommand:
                    t = unix_time(method, (toks, usage))
                    print("time: real %.2fs, user %.2fs, sys %.2fs" % (t['real'], t['user'], t['sys']))
                else:
                    method(toks, usage)
                if profile():
                    pr.disable()
                    ps = pstats.Stats(pr).sort_stats('cumulative')
                    ps.print_stats()
                done = method == self._quitCmd
            else:
                if self._commandLoc is None:
                    raise CLIError("unknown command %s, try help" % cmdName)
                else:
                    raise CLIError("unknown command %s at %s" % (cmdName, self._commandLoc))
        return done

    def _handleProcess(self, line):
        done = False
        try:
            done = self._process(line)
        except CLIError as e:
            stderr("ERROR %s\n" % e.msg)
        except ConfigError as e:
            stderr("CONFIGURATION ERROR %s - abort\n" % e.msg)
            sys.exit(1)
        except KeyboardInterrupt:
            stderr("\n")
        except ValueError as e:
            traceback.print_exc()
            stderr("%s\n" % str(e))
        return done

    def startup(self):
        if self._config:
            for line in self._config:
                self._handleProcess(line)
        else:
            for rc in ["/etc/filebutlerrc",
                       os.path.expanduser("~/.filebutlerrc")]:
                try:
                    with open(rc) as f:
                        count = 0
                        for line in f:
                            count += 1
                            self._commandLoc = "%s:%d" % (rc, count)
                            self._handleProcess(line)
                except IOError:
                    pass
                finally:
                    self._commandLoc = None

    def execute(self, cmds):
        for cmd in cmds:
            self._handleProcess(cmd)

    def interact(self):
        done = False
        while not done:
            try:
                line = input("fb: ")
                done = self._handleProcess(line)
            except EOFError:
                print("bye")
                done = True
            except KeyboardInterrupt:
                stderr("^C\n")

    def _helpCmd(self, toks, usage):
        for cmdname in sorted(self.commands.keys()):
            cmd = self.commands[cmdname]
            privileged = cmd['privileged'] if 'privileged' in cmd else False
            if not privileged or os.geteuid() == 0:
                print("%-12s - %s\n               %s\n" % (cmdname, cmd['desc'], cmd['usage']))
        cmdname = 'time'
        cmd = { 'desc': 'time a command',
                'usage': 'time <cmd> <args>' }
        print("%-12s - %s\n               %s\n" % (cmdname, cmd['desc'], cmd['usage']))

    def _quitCmd(self, toks, usage):
        pass

    def _echoCmd(self, toks, usage):
        print(' '.join(toks[1:]))

    def _setCmd(self, toks, usage):
        if len(toks) < 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        values = toks[2:]
        self._attrs[name] = values
        if name == 'dataset':
            if len(values) != 2:
                raise CLIError("botched attr %s" % name)
            self._ctx.pathway.setDatasetRegex(values[0], values[1])
        if name == 'ignorepathsfrom':
            if len(values) != 1:
                raise CLIError("botched attr %s" % name)
            self._ctx.pathway.setIgnorePathsFrom(values[0])

    def _clearCmd(self, toks, usage):
        if len(toks) != 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        del self._attrs[name]
        if name == 'dataset':
            self._ctx.pathway.clearDatasetRegex()

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
            if name in self._caches:
                print(self._filesets[name].description())

    def _filesetCmd(self, toks, usage):
        if len(toks) < 3:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        type = toks[2]
        if name in self._filesets:
            raise CLIError("duplicate fileset %s" % name)
        if type == "find.gnu.out":
            fileset = self._cached(name, GnuFindOutFileset.parse(self._ctx, name, toks[3:]))
        elif type == "find":
            fileset = self._cached(name, FindFileset.parse(self._ctx, name, toks[3:]))
        elif type == "filter":
            if len(toks) < 4:
                raise CLIError("filter requires fileset, criteria")
            filter, _, _, _ = parseCommandOptions(self._daystart, toks[4:], filter=True)
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
        if len(toks) < 2:
            raise CLIError("usage: %s" % usage)
        if toks[1] == '-u' or toks[1] == '-d' or toks[1] == '-e' or toks[1] == '-s':
            mode = toks[1][1]
            i_fileset = 2
        else:
            mode = 'a'          # all
            i_fileset = 1
        if len(toks) <= i_fileset:
            raise CLIError("usage: %s" % usage)
        name = toks[i_fileset]
        if len(toks) > i_fileset:
            filter, _, _, _ = parseCommandOptions(self._daystart, toks[i_fileset + 1:], filter=True)
        else:
            filter = None
        info = self._fileset(name).info(self._attrs, filter)
        if mode == 'a':
            lines = info.fmt_total()
        elif mode == 'u':
            lines = info.fmt_users()
        elif mode == 'd':
            lines = info.fmt_datasets()
        elif mode == 'e':
            lines = []
            for user, userinfo in info.iterusers():
                if user not in self._aliases:
                    lines.append("%-13s %s" % (user, str(userinfo)))
        elif mode == 's':
            lines = info.fmt_sizes()
        else:
            raise CLIError("usage: %s" % usage)
        _, terminal_lines = os.get_terminal_size() # requires Python 3.3
        if len(lines) < terminal_lines:
            print('\n'.join(lines))
        else:
            pager = Pager()
            try:
                pager.file.write("%s\n" % '\n'.join(lines))
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
                else:
                    raise
            finally:
                pager.close()

    def _printCmd(self, toks, usage):
        if len(toks) < 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        fileset = self._fileset(name)
        if 'print-options' in self._attrs:
            printOptions = toks[2:] + self._attrs['print-options']
        else:
            printOptions = toks[2:]
        if printOptions != []:
            filter, sorter, grouper, _ = parseCommandOptions(self._daystart, printOptions, filter=True, sorter=True, grouper=True)
        else:
            filter, sorter, grouper = None, None, Grouper()

        pager = Pager()
        grouper.setOutput(pager.file)
        try:
            for filespec in fileset.sorted(filter, sorter):
                grouper.write(filespec)
            grouper.flush()
        except IOError as e:
            if e.errno == errno.EPIPE:
                pass
            else:
                raise
        finally:
            pager.close()

    def _dumpCondaCmd(self, toks, usage):
        if len(toks) != 3:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        outpath = toks[2]
        fileset = self._fileset(name)
        with open(outpath, "w") as outfile:
            condaEnvCounter = CondaEnvCounter()
            try:
                for filespec in fileset.select():
                    condaEnvCounter.add(filespec)
                condaEnvCounter.dump(outfile)
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
                else:
                    raise

    def _deleteCmd(self, toks, usage):
        if len(toks) < 2:
            raise CLIError("usage: %s" % usage)
        name = toks[1]
        fileset = self._fileset(name)
        deleteOptions = toks[2:]
        if deleteOptions != []:
            filter, _, _, y = parseCommandOptions(self._daystart, deleteOptions, filter=True, confirm=True)
        else:
            filter, y = None, False

        # get confirmation
        info = fileset.info(self._attrs, filter)
        if not y and not yes_or_no('Really delete %s' % ' '.join(info.fmt_total())):
            return

        # do it
        description = name if filter is None else '%s %s' % (name, str(filter))
        print('... deleting %s' % description)
        with DeletionLog(self._attrs) as logf:
            # delete directories after their contents
            dirs = []
            mtimes = {}
            for filespec in fileset.select(filter):
                # preserve mtime for parent directory
                parent = os.path.dirname(filespec.path)
                if parent not in mtimes:
                    try:
                        mtimes[parent] = os.stat(parent).st_mtime
                    except OSError as e:
                        if e.errno == errno.ENOENT:
                            pass
                        else:
                            raise
                if filespec.isdir():
                    dirs.append(filespec)
                else:
                    filespec.delete(logf)
            for filespec in sorted(dirs, key=lambda d: d.path, reverse=True):
                filespec.delete(logf)
        # now reset mtimes of anything that's left
        for path, mtime in mtimes.items():
            try:
                os.utime(path, (mtime, mtime))
            except OSError as e:
                if e.errno == errno.ENOENT:
                    # silently do nothing if there's no directory left
                    pass
                elif e.errno == errno.EACCES or e.errno == errno.EPERM:
                    # silently do nothing if we don't have permission to fix mtime
                    pass
                else:
                    raise
        # finally save deletions lists for all caches affected by this deletion
        for cache in self._ctx.pendingCaches:
            cache.saveDeletions()
        self._ctx.pendingCaches.clear()

    def _sourceCmd(self, toks, usage):
        if len(toks) != 2:
            raise CLIError("usage: %s" % usage)
        path = toks[1]
        try:
            with open(os.path.expanduser(path)) as f:
                count = 0
                for line in f:
                    count += 1
                    self._commandLoc = "%s:%d" % (path, count)
                    self._handleProcess(line)
        except OSError:
            raise CLIError("can't read file: %s" % path)
        finally:
            self._commandLoc = None

    def _symlinksFileset(self):
        symlinksfileset = self._attrs.get('symlinksfileset')
        if symlinksfileset is None:
            raise CLIError("missing attr symlinksfileset")
        if len(symlinksfileset) != 1:
            raise CLIError("botched attr symlinksfileset")
        return self._fileset(symlinksfileset[0])

    def _symlinksCmd(self, toks, usage):
        fileset = self._symlinksFileset()
        if len(toks) == 2:
            target = toks[1]
            recursive = False
        elif len(toks) == 3 and toks[1] == '-r':
            target = toks[2]
            recursive = True
        else:
            raise CLIError("usage: %s" % usage)
        sources = fileset.symlinkSources(target, recursive)
        _, terminal_lines = os.get_terminal_size() # requires Python 3.3
        if len(sources) < terminal_lines:
            print('\n'.join(sources))
        else:
            pager = Pager()
            try:
                pager.file.write("%s\n" % '\n'.join(sources))
            except IOError as e:
                if e.errno == errno.EPIPE:
                    pass
                else:
                    raise
            finally:
                pager.close()

    def completeSymlinks(self, prefix):
        fileset = self._symlinksFileset()
        return fileset.completeSymlinks(prefix)

    def _updateCacheCmd(self, toks, usage):
        if len(toks) == 1:
            for name in sorted(list(self._caches.keys())):
                #print("updating cache %s" % name)
                self._caches[name].update()
        else:
            for name in toks[1:]:
                self._cache(name).update()

    def _attrsAsStringMap(self):
        s = {}
        for key, values in self._attrs.items():
            s[key] = ' '.join(values)
        return s

    def _sendEmailsCmd(self, toks, usage):
        if len(toks) < 3 or len(toks) > 4:
            raise CLIError("usage: %s" % usage)
        if 'emailfrom' not in self._attrs:
            raise CLIError("missing attr emailfrom")
        if 'templatedir' not in self._attrs:
            raise CLIError("missing attr templatedir")
        templatedirs = self._attrs['templatedir']
        if len(templatedirs) != 1:
            raise CLIError("botched attr templatedir")
        templatedir = templatedirs[0]
        emailonly = self._attrs['emailonly'] if 'emailonly' in self._attrs else None
        name = toks[1]
        template = toks[2]
        override_recipient = None if len(toks) == 3 else toks[3]
        subject_path = os.path.join(templatedir, "%s.subject" % template)
        with open(subject_path, 'r') as f:
            subject_template = string.Template(f.read().replace('\n', '').strip())
        body_path = os.path.join(templatedir, "%s.body" % template)
        with open(body_path, 'r') as f:
            body_template = string.Template(f.read())
        fileset = self._fileset(name)
        m = self._attrsAsStringMap()
        m['fileset'] = name
        m['fileset_descriptor'] = str(fileset.description())
        s = smtplib.SMTP('localhost')
        sender = ' '.join(self._attrs['emailfrom'])
        for user, userfileinfo in fileset.info(self._attrs).iterusers():
            if user in self._aliases and (emailonly is None or user in emailonly):
                recipient = self._aliases[user] if override_recipient is None else override_recipient
                user_fileset = FilterFileset("%s-%s" % (name, user), fileset, Filter(owner=user))
                user_info = user_fileset.info(self._attrs)
                m['username'] = user
                m['info'] = '\n'.join(user_info.fmt_total())
                m['info_datasets'] = '\n'.join(user_info.fmt_datasets())
                #print("==================== %s %s\n\n%s" % (user_email, subject, body))
                msg = email.mime.text.MIMEText(body_template.substitute(m))
                msg['Subject'] = subject_template.substitute(m)
                msg['From'] = sender
                msg['To'] = recipient
                s.sendmail(sender, [recipient], msg.as_string())
        s.quit()
