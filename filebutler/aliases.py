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

import string

def read_etc_aliases():
    """Read /etc/aliases, and return as a dict."""
    aliases = {}
    with open('/etc/aliases') as f:
        for line in f:
            i_hash = string.find(line, '#')
            if i_hash != -1:
                entry = line[:i_hash]
            else:
                entry = line
            if entry != '':
                toks = string.split(entry, ':', 1)
                if len(toks) == 2:
                    user = string.strip(toks[0])
                    email = string.strip(toks[1])
                    if user != '' and email != '':
                        aliases[user] = email
    return aliases
