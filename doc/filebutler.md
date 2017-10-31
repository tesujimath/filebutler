# NAME

filebutler - utility for managing old files in large directory structures

# SYNOPSIS

**filebutler** [*options*]

# DESCRIPTION

Filebutler is a utility for managing large directory structures.  It is focused
on finding and removing old files.  The motivation is that find is far too slow
on directory trees with several million files.  Even using the cache output of find
can be rather slow for interactive queries.  Filebutler improves on this by
structuring filelists by age, and by user.

# COMMANDS

A line starting with a hash is a comment, and is ignored.

## help

Show commands available.

## ls

List filesets

Usage:
```
ls
```

## info

Show summary information for a fileset.

Usage:
```
info <fileset>
```

## print

Print files in a fileset, optionally filtered, via `$PAGER`.

Usage:
```
print <fileset> [<filter-params>]
```

## fileset

Define a fileset with given name and type.  Subsequent parameters are dependent on the type.

### fileset type find.gnu.out

Parameters: `<pathname> [<match> <replace>]`

Example:
```
fileset some-files find.gnu.out $HOME/junk/some-files ^ /full/path/prefix/
fileset some-scratch find.gnu.out $HOME/junk/some-scratch-files ^([^/]*) /dataset/\\1/scratch
```

This is a file containing output from GNU find -ls, with relative pathnames.
The first parameter is the full pathname to the file in question.  Optionally,
match and replace regular expressions may be used to turn the relative paths in
the find output into absolute paths in the filesystem.

The reason for regex support here is to cater for any path munging required, if for
example filebutler is run on a different server, with multiple filesystems being
automounted in different places.  Usually, the first example is sufficient.

### fileset type find

Parameters: `<pathname> [<match> <replace>]`

Example:
```
fileset my-home find $HOME
```

This is a directory structure rooted at `pathname`.

Match and replace munging of paths is as for `find.gnu.out`.

### fileset type filter

Parameters: `<fileset> [-user <username] [-mtime +<n>] [-size +<n>G] [! -path <glob>]`

Example:
```
fileset old-scratch filter some-scratch -mtime +180
fileset my-old-scratch filter old-scratch -user $USER
fileset my-big-old-scratch filter my-old-scratch -size +1G
fileset my-junk filter my-old-scratch ! -path *important*
```

Selects a subset of the underlying fileset, according to the filter parameters.
Filter parameter syntax is modeled on find, albeit with very selective support
for certain features.

### fileset type union

Parameters: `<fileset> [...]`

Example:
```
fileset scratch union scratch1 scratch2 scratch3
```

Defines a new fileset which is the union of arbitrary many others.

## ls-attrs

List attributes, of which cachedir is the only one currently supported.

Usage:
```
ls-attrs
```

## ls-caches

List caches

Usage:
```
ls-caches
```

## echo

Echo parameters after expansion.

Usage:
```
echo <args>
```

## set

Set attribute, e.g. cachedir

Example
```
set cachedir $HOME/.filebutler.cache
```

# OPTIONS

`-c` *commands*
Execute commands (semi-colon separated), rather than run interactively

`-v`
Run in verbose mode

`--batch`
Run in batch mode, with no progress feedback

`--debug`
Run in debug mode

# AUTHOR
Simon Guest
