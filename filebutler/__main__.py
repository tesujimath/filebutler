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

import argparse
import os.path
import readline
import sys

from filebutler.CLI import CLI
from filebutler.version import get_version

def main():
    parser = argparse.ArgumentParser(description="""filebutler v%s - view and prune old files.""" % get_version())
    parser.add_argument('--batch', action='store_true', dest='batch', help='batch mode')
    parser.add_argument('--config', type=argparse.FileType('r'), dest='config', metavar='FILE', help='config file')
    parser.add_argument('--debug', type=argparse.FileType('w'), dest='debug', metavar='FILE', help='debug mode')
    parser.add_argument('--profile', action='store_true', dest='profile', help='profile mode')
    parser.add_argument('--version', action='store_true', dest='version', help='show version and exit')
    parser.add_argument('-v', action='store_true', dest='verbose', help='verbose mode')
    parser.add_argument('-c', dest='command', help='command to invoke')
    args = parser.parse_args()

    if args.version:
        print('filebutler v%s' % get_version())
        sys.exit(0)

    cli = CLI(args)
    cli.startup()

    if args.command is not None:
        cli.execute(args.command.split(';'))
    else:
        historyFile = os.path.expanduser('~/.filebutler.history')
        if os.path.exists(historyFile):
            readline.read_history_file(historyFile)
        cli.interact()
        readline.write_history_file(historyFile)

if __name__ == '__main__':
    main()
