# Filebutler

Filebutler is a utility for managing large directory structures.  It is focused on finding and removing old files.

## Commands

A line starting with a hash is a comment, and is ignored.

### fileset

Define a fileset with given name and type.  Subsequent parameters are dependent on the type.

#### find.gnu.out

Parameters: `<pathname> <regex-match> <regex-replace>`

Example:
```
fileset some-files find.gnu.out $HOME/junk/some-files ^ /full/path/prefix/
fileset some-scratch find.gnu.out $HOME/junk/some-scratch-files ^([^/]*) /dataset/\\1/scratch
```

This is a file containing output from GNU find -ls, with relative pathnames.
The first parameter is the full pathname to the file in question.  The other
parameters are used to turn the relative paths in the find output into absolute
paths in the filesystem.

The reason for regex support here is to cater for any path munging required, if for
example filebutler is run on a different server, with multiple filesystems being
automounted in different places.  Usually, the first example is sufficient.

#### filter

Parameters: `<fileset> [-user <username] [-mtime +<n>]`

Example:
```
fileset old-scratch filter some-scratch -mtime +180
fileset my-old-scratch filter old-scratch -user $USER
```
