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

import datetime
import errno
import os
import resource
from stat import *
import sys
import time
import tzlocal

from .CLIError import CLIError

_debug = None
_profile = False
_progress = True
_verbose = False
def initialize(args):
    global _debug
    global _profile
    global _verbose
    global _progress
    if args.verbose:
        _verbose = True
    if args.profile:
        _profile = True
        _verbose = True
    if args.batch:
        _progress = False
    if args.debug:
        _debug = args.debug
        _verbose = True
        verbose_stderr("debug mode\n")

def stderr(msg):
    sys.stderr.write(msg)
def debug_log(msg):
    if _debug is not None:
        _debug.write(msg)
        _debug.flush()
def progress_stderr(msg):
    if _progress:
        stderr(msg)
def verbose_stderr(msg):
    if _verbose or _debug:
        stderr(msg)
def warning(msg):
    stderr("warning: %s\n" % msg)

def profile():
    return _profile

fbTimeFmt = "%Y%m%d-%H%M%S"
fbDateFmt = "%Y-%m-%d"

def time2utcstr(t):
    return time.strftime(fbTimeFmt, time.gmtime(t))

def time2str(t):
    return time.strftime(fbTimeFmt, time.localtime(t))

def date2str(t):
    return time.strftime(fbDateFmt, time.localtime(t))

def week_number(t):
    """Return time t as an integer valued week YYYYWW."""
    dt = datetime.datetime.fromtimestamp(t)
    isoyear,isoweek,isoweekday = dt.isocalendar()
    return isoyear * 100 + isoweek

def daystart():
    """Return start of today in localtime as epoch."""
    localoffset = tzlocal.get_localzone().utcoffset(datetime.datetime.now())
    d0 = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone.utc) - localoffset
    epoch = datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)
    return (d0 - epoch).total_seconds()

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

def size2str0(n):
    if n == 0:
        return "0"
    else:
        return size2str(n)

def size2str(n):
    if n < Kilo:
        return "0k"             # so small we don't care
    elif n < Mega:
        return "%dk" % (n // Kilo)
    elif n < Giga:
        return "%dM" % (n // Mega)
    elif n < Tera:
        return "%dG" % (n // Giga)
    else:
        return "%.1fT" % (n * 1.0 / Tera)

def str2size(s):
    unit = s[-1]
    x = int(s[:-1])
    if unit == 'k':
        return x * Kilo
    elif unit == 'M':
        return x * Mega
    elif unit == 'G':
        return x * Giga
    elif unit == 'T':
        return x * Tera
    else:
        raise CLIError("unsupported filesize %s, must be n[kMGT]" % s)

def filetimestr(path):
    try:
        return time2str(os.stat(path).st_mtime)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return "<missing>"
        else:
            raise

def filedatestr(path):
    try:
        return date2str(os.stat(path).st_mtime)
    except OSError as e:
        if e.errno == errno.ENOENT:
            return "<missing>"
        else:
            raise

# adapted from https://gist.github.com/turicas/5278558
def unix_time(function, args=tuple(), kwargs={}):
    '''Return `real`, `sys` and `user` elapsed time, like UNIX's command `time`
    You can calculate the amount of used CPU-time used by your
    function/callable by summing `user` and `sys`. `real` is just like the wall
    clock.
    Note that `sys` and `user`'s resolutions are limited by the resolution of
    the operating system's software clock (check `man 7 time` for more
    details).
    '''
    start_time, start_resources = time.time(), resource.getrusage(resource.RUSAGE_SELF)
    function(*args, **kwargs)
    end_resources, end_time = resource.getrusage(resource.RUSAGE_SELF), time.time()

    return {'real': end_time - start_time,
            'sys': end_resources.ru_stime - start_resources.ru_stime,
            'user': end_resources.ru_utime - start_resources.ru_utime}

def yes_or_no(prompt, default=False):
    try:
        s = input('%s [yN]? ' % prompt)
        return len(s) >= 1 and s[0] in 'Yy'
    except:
        return default

def liberal(fn, a, b):
    if a is None:
        return b
    elif b is None:
        return a
    else:
        return fn(a, b)
