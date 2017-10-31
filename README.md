# Filebutler

Filebutler is a utility for managing large directory structures.  It is focused
on finding and removing old files.  The motivation is that find is far too slow
on directory trees with several million files.  Even using the cache output of find
can be rather slow for interactive queries.  Filebutler improves on this by
structuring filelists by age, and by user.

*This is a work-in-progress.  Documentation remains to be fleshed out.*

