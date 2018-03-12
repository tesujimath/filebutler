#!/usr/bin/env python
#
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

import argparse
import os.path
import readline
import sys

from filebutler.CLI import CLI

def main():
    parser = argparse.ArgumentParser(description='View and prune old files.')
    parser.add_argument('--batch', action='store_true', dest='batch', help='batch mode')
    parser.add_argument('--debug', type=argparse.FileType('w'), dest='debug', metavar='FILE', help='debug mode')
    parser.add_argument('--profile', action='store_true', dest='profile', help='profile mode')
    parser.add_argument('-v', action='store_true', dest='verbose', help='verbose mode')
    parser.add_argument('-c', dest='command', help='command to invoke')
    args = parser.parse_args()

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
