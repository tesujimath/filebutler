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

import errno
import os
import time

from .CLIError import CLIError
from .util import date2str, debug_log

class DeletionLog(object):
    """A logfile for deleted files/directories."""

    def __init__(self, attrs):
        # first try the syslogdir, if we have permission
        if 'syslogdir' not in attrs:
            raise CLIError("missing attr syslogdir")
        syslogdirs = attrs['syslogdir']
        if len(syslogdirs) != 1:
            raise CLIError("botched attr syslogdir")
        syslogdir = syslogdirs[0]
        if 'userlogdir' not in attrs:
            raise CLIError("missing attr userlogdir")
        userlogdirs = attrs['userlogdir']
        if len(userlogdirs) != 1:
            raise CLIError("botched attr userlogdir")
        userlogdir = userlogdirs[0]
        try:
            os.makedirs(syslogdir)
        except:
            # ignore errors, we'll catch it in a moment
            pass
        datestamp = date2str(time.time())
        try:
            self._file = open(os.path.join(syslogdir, datestamp), 'a')
        except IOError as e:
            if e.errno == errno.EACCES or e.errno == errno.EPERM or e.errno == errno.ENOENT:
                # syslogdir no good, try userlogdir
                try:
                    os.makedirs(userlogdir)
                except OSError as e:
                    if e.errno != errno.EEXIST:
                        raise
                self._file = open(os.path.join(userlogdir, datestamp), 'a')
            else:
                raise

    def __enter__(self):
        return self._file

    def __exit__(self, exc_type, exc_value, traceback):
        self._file.close()
