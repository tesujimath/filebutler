Filebutler
==========

Filebutler is a utility for managing old files in huge directory trees.
Huge means of the order of 100 million files. The motivation is that
find is far too slow on directory trees with this many files. Even
working with filelists generated offline by find can be rather slow for
interactive use. Filebutler improves on this by structuring filelists by
age, by size, by owner, and by dataset (see below).

Installation
------------

Filebutler is now on PyPI, so may be installed using pip, preferably in
a virtualenv.

::

    $ pip install filebutler

Alternatively, filebutler is also on conda-forge.

::

    $ conda install filebutler

Installing filebutler from RPM is now deprecated, and the spec file has therefore
been removed from the repo.

Example Use
-----------

::

    $ filebutler
    fb: ls
    gypsy-scratch filelist /mirror/gypsy/z202/scratch/all-scratch-files cached on 2017-12-22
    infernal-scratch filelist /mirror/infernal/z302/scratch/all-scratch-files cached on 2017-12-22
    integrity-scratch filelist /mirror/integrity/z102/scratch/all-scratch-files cached on 2017-12-22
    ivy-scratch filelist /mirror/ivy/z101/scratch/all-scratch-files cached on 2017-12-22
    scratch union gypsy-scratch infernal-scratch integrity-scratch ivy-scratch
    old-scratch filter scratch older:2015-12-23
    my-old-scratch filter old-scratch owner:will
    very-old-scratch filter old-scratch older:2009-10-05
    big-old-scratch filter old-scratch size:+1G

    fb: time info -s scratch
    total 139.8T in  62306443 files
       0 -   1k     10G in  32652282 files
      1k -  10k     55G in  18798049 files
     10k - 100k    196G in   6735931 files
    100k -   1M   1012G in   3096409 files
      1M -  10M    2.5T in    698040 files
     10M - 100M    7.3T in    218382 files
    100M -   1G   28.0T in     90412 files
      1G -  10G   32.4T in     14142 files
     10G - 100G   58.6T in      2733 files
    100G +         9.7T in        63 files
    time: real 0.00s, user 0.00s, sys 0.00s

    fb: time info -u old-scratch
    total 34.2T in 7138319 files
    captainjack 9.8T in 122775 files
    will 6.3T in 197499 files
    barbossa 3.8T in 121977 files
    elizabeth 3.5T in 1686 files
    bootstrap 3.3T in 2532542 files
    calypso 1.2T in 551088 files
    norrington 1.1T in 41961 files
    <snip>
    time: real 8.22s, user 3.00s, sys 1.26s

    fb: time info -u very-old-scratch
    total 12G in 52759 files
    barbossa 11G in 47262 files
    salazar 127M in 296 files
    gibbs 28M in 5101 files
    will 27M in 58 files
    time: real 0.06s, user 0.04s, sys 0.01s

    fb: print very-old-scratch
    -rw-r--r-- 2005-02-20 743k /dataset/blackpearl/scratch/maker_AR501/GeneMark.ES/mtx/human_00_43.mtx  will:crew
    -rw-r--r-- 2005-02-20 743k /dataset/blackpearl/scratch/maker_AR501/GeneMark.ES/mtx/human_43_49.mtx  will:crew
    -rw-r--r-- 2005-02-20 621k /dataset/blackpearl/scratch/maker_AR501/GeneMark.ES/mtx/wheat.mtx        will:crew
    -rw-r--r-- 2005-02-20 621k /dataset/blackpearl/scratch/maker_AR501/GeneMark.ES/mtx/barley.mtx       will:crew
    -rw-r--r-- 2005-02-20 621k /dataset/blackpearl/scratch/maker_AR501/GeneMark.ES/mtx/corn.mtx         will:crew
    <snip>

    fb: delete very-old-scratch

Concepts
--------

Filebutler's main concept is the *fileset*. The supported fileset types
are as follows.

+----------------+----------------------------------------------------------------+
| Type           | Description                                                    |
+================+================================================================+
| find.gnu.out   | List of files generated offline by GNU ``find -ls``            |
+----------------+----------------------------------------------------------------+
| find           | List of files found by filebutler walking the filesystem       |
+----------------+----------------------------------------------------------------+
| union          | Union of specified filesets                                    |
+----------------+----------------------------------------------------------------+
| filter         | Any existing fileset filtered by age, owner, file size, etc.   |
+----------------+----------------------------------------------------------------+

Filebutler generates on-disk structured caches for both the
``find.gnu.out`` and ``find`` filesets, as described in the next
section. It is these caches which enable it to process queries over
millions of files in reasonable time.

Cache Structure
~~~~~~~~~~~~~~~

Filebutler's main value add is to process very large filelists, and
structure them into its cache, by age, dataset, and owner. Interactive
queries are greatly accelerated by scanning over just those portions of
the overall filelist that match the filter criteria.

The top level cache structuring is by week number, that is YYYYWW, where
WW is the ISO week number. This results in 52 directories per year. On
the author's fileservers (half a petabyte or so, with 100 million files
dating back over 20 years or so), there are around 1000 such directories
across the filesets.

The second level cache structuring is by dataset. A dataset is a way of
grouping files. The simplest definition would be, top-level directory on
a fileserver, but filebutler supports arbitrary definition of dataset,
by means of regular expression matching of pathnames. Datasets are
optional.

The third level cache structuring is by owner. Most users are interested
only in files they own, and by scanning only such portions of filelists,
queries are greatly accelerated.

At the bottom level of the cache structure, within each owner directory,
filebutler uses two files: ``filelist`` and ``info``. The former is
simply a list of the files last modified in that week, in that dataset,
owned by that user, with their attributes. The latter is summary
information of the number of these files and their total size.

Features
--------

Filebutler has two main uses:

-  unprivileged users wanting (or requested) to be good citizens, and
   delete old files they no longer need
-  privileged users, for deleting such users' files automatically, and
   emailing warnings in advance

The `manpage <doc/filebutler.rst>`__ lists the commands available for
both types of user.

Unprivileged Users
~~~~~~~~~~~~~~~~~~

Unprivileged users require to select a set of files, check that these
are in fact unwanted, and delete them.

Existing filesets may be refined, by defining new filters on them, for
example:

::

    fb: ls
    fb: print very-old-scratch
    fb: print very-old-scratch ! -path *important*
    fb: fileset unimportant filter very-old-scratch ! -path *important*
    fb: info very-old-scratch
    total 12G in 52759 files
    fb: info unimportant
    total 12G in 52433 files
    fb: delete unimportant

Privileged Users
~~~~~~~~~~~~~~~~

It is expected that privileged users will install cron jobs to enforce
file deletion policies. Warning emails may be generated, to the owners
of files in selected filesets. For example:

::

    fb: fileset warn-old-scratch filter scratch -mtime +730
    fb: fileset delete-old-scratch filter scratch -mtime +737
    fb: send-emails warn-old-scratch deletion-warning
    fb: delete delete-old-scratch

See the next section for the configuration required to support warning
emails.

Configuration
-------------

/etc/filebutlerrc
~~~~~~~~~~~~~~~~~

The main configuration is simply a command file, which sets attributes
and defines filesets. The command set for the startup file is identical
to the interactive command set.

Usually, startup commands are read from both ``/etc/filebutlerrc`` and
``~/.filebutlerrc``.  This may be overriden using the command line argument
``--config``, in which case, neither of the default configuration files are
read.

See the `example filebutlerrc <examples/filebutlerrc>`__ file.

The commands and attributes available are defined on the
`manpage <doc/filebutler.rst>`__.

Email Templates
~~~~~~~~~~~~~~~

The attribute ``templatedir`` defines the location of the directory
containing email templates. For example, to send emails using the
``deletion-warning`` template, that directory must contain both the
subject and body files, called respectively ``deletion-warning.subject``
and ``deletion-warning.body``.

See the example
`subject <examples/templates/deletion-warning.subject>`__ and
`body <examples/templates/deletion-warning.body>`__ templates.

Ignore Paths
~~~~~~~~~~~~

Certain files can be flagged to be ignored by filebutler. This is done
by means of a list of Python-style regular expressions in the file named
by the attribute ``ignorepathsfrom``. Any file matching one of these
regular expressions will be ignored.

Note that the ignoring is done when generating the filebutler cache,
when scanning the actual filesystem, or the output file list of
``find -ls``. If desired, different ignore files may be used for
different filesets, by setting the attribute just before the line
defining the fileset.

See the example `ignore paths file <examples/ignorepaths>`__

Cron
~~~~

Cron jobs are recommended for regenerating the caches overnight,
deleting old files, and sending warning emails.

For example:

::

    0 5 * * * filebutler -c update-cache --batch
    0 7 * * 1 filebutler -c 'send-emails warn-old-scratch; delete delete-old-scratch' --batch

See the `manpage <doc/filebutler.rst>`__ for further details.
