# NAME

filebutler - utility for managing old files in large directory structures

# SYNOPSIS

**filebutler** [*options*]

# DESCRIPTION

Filebutler is a utility for managing large directory structures.  It is focused on finding and removing old files.  The motivation is that find is far too slow on directory trees with several million files.  Even using the cache output of find can be rather slow for interactive queries.  Filebutler improves on this by structuring filelists by age, by user, and by dataset.

Dataset is an optional concept, which is perhaps most usefully regarded as the top-level directory in any path.  It is defined by the dataset attribute in the config file.

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
info <fileset> [-u|-d] [<filter-params>]
```

With `-u`, shows breakdown by user, sorted by size.

With `-d`, shows breakdown by dataset, sorted by size.

## print

Print files in a fileset, optionally filtered, via `$PAGER`.  If defined, the attribute `print-options` is appended to the command.

Usage:
```
print <fileset> [<filter-params>] [-by-size|-by-path]
```

The `filter-params` are as described for the filter fileset type.

## delete

Delete all files in a fileset.

Usage:
```
delete <fileset>
```

The `filter-params` are as described for the filter fileset type.

## fileset

Define a fileset with given name and type.  Subsequent parameters are dependent on the type.

### fileset type find.gnu.out

Parameters: `<pathname> [<match> <replace>]`

Example:
```
fileset some-files find.gnu.out $HOME/junk/some-files ^ /full/path/prefix/
fileset some-scratch find.gnu.out $HOME/junk/some-scratch-files ^([^/]*) /dataset/\\1/scratch
```

This is a file containing output from GNU find -ls, with relative pathnames.  The first parameter is the full pathname to the file in question.  Optionally, match and replace regular expressions may be used to turn the relative paths in the find output into absolute paths in the filesystem.

The reason for regex support here is to cater for any path munging required, if for example filebutler is run on a different server, with multiple filesystems being automounted in different places.  Usually, the first example is sufficient.

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

Selects a subset of the underlying fileset, according to the filter parameters.  Filter parameter syntax is modeled on find, albeit with very selective support for certain features.

### fileset type union

Parameters: `<fileset> [...]`

Example:
```
fileset scratch union scratch1 scratch2 scratch3
```

Defines a new fileset which is the union of arbitrary many others.

## ls-attrs

List attributes.

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

## clear

Clear attribute, e.g. print-options

Example
```
clear print-options
```

## update-cache

Update all or named caches, by rescanning source filelists

Example
```
update-cache
update-cache old-scratch old-home
```

## quit

Exit filebutler.  Equivalent to C-d.

Example
```
quit
```

## time

Time a command

Example
```
time info old-scratch
```

# PRIVILEGED COMMANDS

Certain commands are available only to root.  As follows.

## send-emails

Send email to each user with files in the named fileset, using the named email template.  Email templates are found in the directory given by the `emaildir` attribute.  The emails are sent via localhost STMP, from the address specified by the `emailfrom` attribute.

The template files for email subject and body use standard Python template syntax.  Any attribute is available as a mapping key, in addition to `fileset`, `fileset_descriptor`.

Example
```
send-emails old-scratch deletion-warning
```

This requires two files in `emaildir`, namely `deletion-warning.subject` and `deletion-warning.body`, whose contents could be as follows.  These files use

deletion-warning.subject:
```
Your files in ${fileset} will be autodeleted soon
```

deletion-warning.body:
```
Please note that your files in $fileset will be automatically deleted in one
week.  These files were selected according to this criterion:
$fileset_descriptor

The following filebutler commands are recommended.
$hostname$$ filebutler
fb: help
fb: ls
fb: info -d $fileset
fb: print $fileset -by-path
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
