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

import errno
import os
import time
from stat import *
import sys

diagnostics = True
progress = True
verbose = True
def initialize(args):
    if args.batch:
        diagnostic_stderr("batch mode\n")
        global progress
        global verbose
        progress = False
        verbose = False

def stderr(msg):
    sys.stderr.write(msg)
def diagnostic_stderr(msg):
    if diagnostics:
        stderr(msg)
def progress_stderr(msg):
    if progress:
        stderr(msg)
def verbose_stderr(msg):
    if verbose:
        stderr(msg)

fbTimeFmt = "%Y%m%d-%H%M%S"

def time2str(t):
    return time.strftime(fbTimeFmt, time.localtime(t))

# stolen from Python 3:
_filemode_table = (
    ((S_IFLNK,         "l"),
     (S_IFREG,         "-"),
     (S_IFBLK,         "b"),
     (S_IFDIR,         "d"),
     (S_IFCHR,         "c"),
     (S_IFIFO,         "p")),

    ((S_IRUSR,         "r"),),
    ((S_IWUSR,         "w"),),
    ((S_IXUSR|S_ISUID, "s"),
     (S_ISUID,         "S"),
     (S_IXUSR,         "x")),

    ((S_IRGRP,         "r"),),
    ((S_IWGRP,         "w"),),
    ((S_IXGRP|S_ISGID, "s"),
     (S_ISGID,         "S"),
     (S_IXGRP,         "x")),

    ((S_IROTH,         "r"),),
    ((S_IWOTH,         "w"),),
    ((S_IXOTH|S_ISVTX, "t"),
     (S_ISVTX,         "T"),
     (S_IXOTH,         "x"))
)

def filemode(mode):
    """Convert a file's mode to a string of the form '-rwxrwxrwx'."""
    perm = []
    for table in _filemode_table:
        for bit, char in table:
            if mode & bit == bit:
                perm.append(char)
                break
        else:
            perm.append("-")
    return "".join(perm)

Kilo = 1024
Mega = 1024 ** 2
Giga = 1024 ** 3
Tera = 1024 ** 4

def size2str(n):
    if n < Kilo:
        return "%d" % n
    elif n < Mega:
        return "%dk" % (n / Kilo)
    elif n < Giga:
        return "%dM" % (n / Mega)
    elif n < Tera:
        return "%dG" % (n / Giga)
    else:
        return "%.1fT" % (n * 1.0 / Tera)

def filetimestr(path):
    try:
        return time2str(os.stat(path).st_mtime)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("stat failed, no such file %s" % path)
            return "missing"
        else:
            raise
