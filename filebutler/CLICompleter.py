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

from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from builtins import (
    bytes, dict, int, list, object, range, str,
    ascii, chr, hex, input, next, oct, open,
    pow, round, super,
    filter, map, zip)

import os
import readline

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
        with open("/home/guestsi/junk/completer.log", "a") as logf:
            try:
                logf.write("CLI::_completer '%s' %s\n" % (text, state))
                if state == 0:
                    line = readline.get_line_buffer().lstrip()
                    self._toks = line.split()
                    logf.write("line '%s': %s\n" % (line, str(self._toks)))
                    if line == self._text:
                        logf.write("calling _complete_cmd\n")
                        self._complete_cmd()
                    else:
                        completer = "_complete_%s_cmd" % self._toks[0].replace('-', '_')
                        if hasattr(self, completer):
                            logf.write("calling %s\n" % completer)
                            getattr(self, completer)()
                        else:
                            logf.write("not calling %s\n" % completer)
                            self._completions = None
                    logf.write("completions %s\n" % str(self._completions))
                if self._completions is None:
                    result = None
                elif state >= len(self._completions):
                    result = None
                else:
                    result = self._completions[state] + ' '
                logf.write("result %s\n" % str(result))
            except Exception as e:
                logf.write("Exception %s\n" % str(e))
                raise e
        return result

    def _complete_cmd(self):
        self._completions = [cmd for cmd in self._cli.commands if cmd.startswith(self._text)]
        #privileged = cmd['privileged'] if 'privileged' in cmd else False
        #        if privileged and os.geteuid() != 0:

    def _complete_fileset_cmd(self):
        result = []
        return result

    def _complete_info_cmd(self):
        return None

    def _complete_print_cmd(self):
        self._completions = []
        if len(self._toks) == 1 or len(self._toks) == 2 and self._toks[1] == self._text:
            self._append_fileset_completions()

    def _complete_delete_cmd(self):
        return None

    def _complete_update_cache_cmd(self):
        return None

    def _append_fileset_completions(self):
        return self._completions.extend([fileset for fileset in self._cli.filesetNames if fileset.startswith(self._text)])
