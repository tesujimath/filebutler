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

import os
import pwd
import readline

from .util import verbose_stderr #, debug_log

class CLICompleter(object):

    def __init__(self, cli):
        self._cli = cli
        readline.set_completer(self._completer)
        readline.set_completer_delims(" ")
        readline.parse_and_bind("tab: complete")

    def _completer(self, text, state):
        result = None
        self._text = text
        self._state = state
        if state == 0:
            self._completions = []
            line = readline.get_line_buffer().lstrip()
            self._toks = line.split()
            if text != '':
                self._toks = self._toks[:-1] # don't include the current text
            if not self._toks:
                self._complete_cmd()
            else:
                completer = "_complete_%s_cmd" % self._toks[0].replace('-', '_')
                if hasattr(self, completer):
                    getattr(self, completer)()
                else:
                    self._completions = None
        if self._completions is None:
            result = None
        elif state >= len(self._completions):
            result = None
        else:
            result = self._completions[state] + ' '
        #debug_log('_completer(%s, %d): "%s"\n' % (text, state, result))
        return result

    def _complete_cmd(self):
        if os.geteuid() != 0:
            cmds = [cmd for cmd in self._cli.commands if 'privileged' not in self._cli.commands[cmd]]
        else:
            cmds = [cmd for cmd in self._cli.commands]
        self._append_matching(cmds, sort=True)

    def _complete_fileset_cmd(self):
        if self._append_option_parameters():
            return
        n = len(self._toks)
        if n == 1:
            # next param is new fileset name, can't complete this
            pass
        elif n == 2:
            self._append_matching(['find.gnu.out','find','filter','union'])
        elif self._toks[2] == 'filter':
            if n == 3:
                self._append_filesets()
            else:
                self._append_options(filter=True)
        elif self._toks[2] == 'union':
            self._append_filesets()

    def _complete_info_cmd(self):
        if self._append_option_parameters():
            return
        n = len(self._toks)
        if n == 1:
            self._append_filesets()
        else:
            self._append_options(filter=True)

    def _complete_print_cmd(self):
        if self._append_option_parameters():
            return
        n = len(self._toks)
        if n == 1:
            self._append_filesets()
        else:
            self._append_options(filter=True, sorter=True, grouper=True)

    def _complete_delete_cmd(self):
        if self._append_option_parameters():
            return
        n = len(self._toks)
        if n == 1:
            self._append_filesets()
        else:
            self._append_options(filter=True)

    def _complete_source_cmd(self):
        n = len(self._toks)
        if n == 1:
            self._append_filenames()

    def _complete_symlinks_cmd(self):
        n = len(self._toks)
        #verbose_stderr("_complete_symlinks_cmd %d %s '%s'\n" % (n, str(self._toks), self._text))
        if n == 1:
            self._append_matching(['-r'])
        if n == 1 or n == 2 and self._toks[1] == '-r':
            self._completions.extend(sorted(self._cli.completeSymlinks(self._text)))

    def _complete_update_cache_cmd(self):
        self._append_filesets()

    def _append_filesets(self):
        self._append_matching(self._cli.filesetNames)

    def _append_filenames(self):
        def isdir(path):
            "Return whether expanduser of path is a directory."
            return os.path.isdir(os.path.expanduser(path))

        def listdirx(root):
            "List directory 'root' appending the path separator to subdirs."
            paths = []
            for name in os.listdir(os.path.expanduser(root)):
                path = os.path.join(root, name)
                if isdir(path):
                    name += os.sep
                paths.append(name)
            return paths

        def complete_path(path):
            if not path:
                return listdirx('.')
            dirname, rest = os.path.split(path)
            tmp = dirname if dirname else '.'
            paths = [os.path.join(dirname, p) for p in listdirx(tmp) if p.startswith(rest)]
            # more than one match, or single match which does not exist (typo)
            if len(paths) != 1:
                #debug_log('len %d\n' % len(paths))
                return paths
            # resolved to a single directory, so return list of files below it
            path = paths[0]
            if isdir(path):
                #debug_log('is a directory: "%s"\n' % path)
                return [os.path.join(path, p) for p in listdirx(path)]
            # exact file match terminates this completion
            #debug_log('not a directory: "%s"\n' % path)
            return [path + ' ']

        paths = sorted(complete_path(self._text))
        #debug_log('CLI::_append_filenames(%s): %s\n' % (self._text, ', '.join(['"%s"' % path for path in paths])))
        self._completions.extend(paths)

    def _append_options(self, filter=False, sorter=False, grouper=False):
        if filter:
            self._append_matching(['-user','-dataset','-size','-mtime','! -path','-regex'])
        if sorter:
            self._append_matching(['-by-size'])
        if grouper:
            self._append_matching(['-depth'])

    def _append_option_parameters(self):
        lasttok = self._toks[-1]
        if lasttok == '-user':
            self._append_users()
            return True
        if lasttok == '-dataset':
            self._append_datasets()
            return True
        return False

    def _append_users(self):
        self._append_matching([pwent[0] for pwent in pwd.getpwall() if pwent[2] >= 500 and pwent[2] < 3000], sort=True)

    def _append_datasets(self):
        self._append_matching([pwent[0] for pwent in pwd.getpwall() if pwent[2] >= 3000 and pwent[2] < 4000], sort=True)

    def _append_matching(self, xs, sort=False):
        matching = [x for x in xs if x.startswith(self._text)]
        self._completions.extend(sorted(matching) if sort else matching)
