Filebutler is a utility for managing old files in huge directory trees.  Huge means of the order of 100 million files.  The motivation is that find is far too slow on directory trees with this many files.  Even working with filelists generated offline by find can be rather slow for interactive use.  Filebutler improves on this by structuring filelists by age, by owner, and by dataset.

For the full documentation, see README.md, and the man page.
