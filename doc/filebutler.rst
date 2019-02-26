NAME
====

filebutler - utility for managing old files in large directory
structures

SYNOPSIS
========

**filebutler** [*options*\ ]

DESCRIPTION
===========

Filebutler is a utility for managing large directory structures. It is
focused on finding and removing old files. The motivation is that find
is far too slow on directory trees with several million files. Even
using the cache output of find can be rather slow for interactive
queries. Filebutler improves on this by structuring filelists by age, by
user, and by dataset.

Dataset is an optional concept, which is perhaps most usefully regarded
as the top-level directory in any path. It is defined by the dataset
attribute in the config file.

Throughout filebutler commands and auxiliary files, all regular
expressions use standard Python regular expression syntax.

COMMANDS
========

A line starting with a hash is a comment, and is ignored.

help
----

Show commands available.

ls
--

List filesets

Usage:

::

    ls

info
----

Show summary information for a fileset.

Usage:

::

    info [-u|-d|-e|-s] <fileset> [<filter-params>]

With ``-u``, shows breakdown by user, sorted by size.

With ``-d``, shows breakdown by dataset, sorted by size.

With ``-e``, shows breakdown by user, sorted by size, only for users
with no email alias.

With ``-s``, shows breakdown by size, configured by the sizebuckets attribute

print
-----

Print files in a fileset, optionally filtered, via ``$PAGER``. If
defined, the attribute ``print-options`` is appended to the command.

Usage:

::

    print <fileset> [<filter-params>] [-by-size] [-depth <depth>]

The ``filter-params`` are as described for the filter fileset type.

delete
------

Delete all files in a fileset, optionally filtered.

Usage:

::

    delete <fileset> [<filter-params>]

The ``filter-params`` are as described for the filter fileset type.

symlinks
--------

Print all symlinks to the given target.  With ``-r``, do this recursively.

Usage:

::

    symlinks [-r] <target-path>

fileset
-------

Define a fileset with given name and type. Subsequent parameters are
dependent on the type.

fileset type find.gnu.out
~~~~~~~~~~~~~~~~~~~~~~~~~

Parameters: ``<pathname> [<match> <replace>]``

Example:

::

    fileset some-files find.gnu.out $HOME/junk/some-files ^ /full/path/prefix/
    fileset some-scratch find.gnu.out $HOME/junk/some-scratch-files ^([^/]*) /dataset/\\1/scratch

This is a file containing output from GNU find -ls, with relative
pathnames. The first parameter is the full pathname to the file in
question. Optionally, match and replace regular expressions may be used
to turn the relative paths in the find output into absolute paths in the
filesystem.

The reason for regex support here is to cater for any path munging
required, if for example filebutler is run on a different server, with
multiple filesystems being automounted in different places. Usually, the
first example is sufficient.

fileset type find
~~~~~~~~~~~~~~~~~

Parameters: ``<pathname> [<match> <replace>]``

Example:

::

    fileset my-home find $HOME

This is a directory structure rooted at ``pathname``.

Match and replace munging of paths is as for ``find.gnu.out``.

fileset type filter
~~~~~~~~~~~~~~~~~~~

Parameters:
``<fileset> [-user <username] [-mtime +<n>] [-size +<n>[kMGT]] [! -path <glob>] [-regex <path-regex>]``

Example:

::

    fileset old-scratch filter some-scratch -mtime +180
    fileset my-old-scratch filter old-scratch -user $USER
    fileset my-big-old-scratch filter my-old-scratch -size +1G
    fileset my-junk filter my-old-scratch ! -path *important*
    fileset my-isos filter my-home -regex \\.iso$

Selects a subset of the underlying fileset, according to the filter
parameters. Filter parameter syntax is modeled on find, albeit with very
selective support for certain features.

Note that because the input line is read by GNU readline, backslashes must be doubled, alas.

fileset type union
~~~~~~~~~~~~~~~~~~

Parameters: ``<fileset> [...]``

Example:

::

    fileset scratch union scratch1 scratch2 scratch3

Defines a new fileset which is the union of arbitrary many others.

ls-attrs
--------

List attributes.

Usage:

::

    ls-attrs

ls-caches
---------

List caches

Usage:

::

    ls-caches

echo
----

Echo parameters after expansion.

Usage:

::

    echo <args>

set
---

Set attribute, e.g. cachedir

Example

::

    set cachedir $HOME/.filebutler.cache

clear
-----

Clear attribute, e.g. print-options

Example

::

    clear print-options

update-cache
------------

Update all or named caches, by rescanning source filelists

Example

::

    update-cache
    update-cache old-scratch old-home

quit
----

Exit filebutler. Equivalent to C-d.

Example

::

    quit

time
----

Time a command

Example

::

    time info old-scratch

PRIVILEGED COMMANDS
===================

Certain commands are available only to root. As follows.

send-emails
-----------

Send email to each user with files in the named fileset, using the named
email template. Email templates are found in the directory given by the
``templatedir`` attribute. The emails are sent via localhost STMP, from
the address specified by the ``emailfrom`` attribute, and only to users
who have entries in ``/etc/aliases``.

For testing purposes, it is possible to further restrict the list of
users to whom emails may be sent using the attribute ``emailonly``,
whose value is a list of usernames.

The template files for email subject and body use standard Python
template syntax. Any attribute is available as a mapping key, in
addition to ``fileset``, ``fileset_descriptor``, ``info``,
``info_datasets``.

Example

::

    send-emails old-scratch deletion-warning

This requires two files in ``emaildir``, namely
``deletion-warning.subject`` and ``deletion-warning.body``, whose
contents could be as follows. These files use

deletion-warning.subject:

::

    Your files in ${fileset} will be autodeleted soon

deletion-warning.body:

::

    Please note that your files in ${fileset} will be automatically deleted in one
    week.  These files were selected by this filter:
    ${fileset_descriptor}

    The following filebutler commands are recommended.
    ${hostname}$$ filebutler
    fb: help
    fb: ls
    fb: info -d ${fileset}
    fb: print ${fileset} -depth 2

    A summary of the files which will be deleted is as follows.

    ${info_datasets}

Attributes
==========

Attributes may be set at any time, either in the startup file, or as a
command, and generally affect subsequent commands.

cache
-----

List of cache kinds to use, in order.

Example:

::

    set cache weekly size user

If this attribute is not set, the default order is used, which is ``weekly user size dataset``.
The cache order may be tuned to optimize the queries of most interest.

cachedir
--------

Root directory of the filebutler cache tree.

Example:

::

    set cachedir /bifo/support/cache/filebutler

deltadir
--------

Directory where file delta records are written. Must be writable by the
user running filebutler.

Example:

::

    set deltadir $HOME/.filebutler/delta

syslogdir
---------

Directory where file deletions by root are logged.

Example:

::

    set syslogdir /bifo/support/admin/filebutler/log

userlogdir
----------

Directory where file deletions by unprivileged users are logged.

Example:

::

    set userlogdir $HOME/.filebutler/log

templatedir
-----------

Directory containing email templates.

Example:

::

    set templatedir /etc/filebutler/templates

emailfrom
---------

Email address used as sender of filebutler emails.

Example:

::

    set emailfrom Filebutler <admin@mycompany.com>

emailonly
---------

Generally used when testing email facility. Space-separated list of
users to whom filebutler may send emails.

Example:

::

    set emailonly captainjack will

dataset
-------

Regular expression used to extract dataset component from a path.

Example:

::

    set dataset ^/dataset/([^/]*)/.*$ \\1

ignorepathsfrom
---------------

File containing regular expressions of paths which filebutler should
ignore. Within the file, comments begin with a hash character, until
end-of-line, and whitespace around regular expressions is ignored.

Example:

::

    set ignorepathsfrom /etc/filebutler/ignorepaths

sizebuckets
-----------

List of sizes of the buckets to use for the by-size layer of the cache.

Example:

::

    set sizebuckets 1M 10M 100M 1G 10G 100G

In this example, there are separate trees in the cache for files of size
< 1M, files of 1M <= size < 10M, etc. This greatly speeds up filtering
by size.

private
-------

Any cache created when the ``private`` attribute is set is created such
that each user can only read their own filelists.

Example:

::

    set private
    fileset home find /home
    clear private

symlinksfileset
---------------

This is the name of the fileset used to resolve symlink targets.  You
should probably set this to the top-level union fileset, to ensure the
``symlinks`` command covers all filesets.

There is no filtering support for symlinks.

OPTIONS
=======

``-h``, ``--help`` Show help and exit

``--version`` Show version and exit

``-c`` *commands* Execute commands (semi-colon separated), rather than
run interactively

``-v`` Run in verbose mode

``--batch`` Run in batch mode, with no progress feedback

``--debug`` *file* Run in debug mode, with output going to *file*

``--profile`` Run in profile mode

CONFIGURATION
=============

On startup, filebutler reads commands from ``/etc/filebutlerrc`` and
then ``~/.filebutlerrc``. The former enables the system administrator to
define site-wide filesets. The latter enables any user to supplement the
site-wide definitions with their own.

See the README and examples for more details about configuration.

AUTHOR
======

Simon Guest
