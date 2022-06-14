# BUGS:

  * '' as non-zero sequence name

# ToDo:

  * change "up" links in genres
  * add per-zip view (by authors/sequences/genres) with custom zip sorting (as in torrent description) -- in progress
  * refactor it!

# ToDo sometime:

  * add configurable logging in `managedb.py` with levels:
    - DEBUG -- current zip, current book, may be show some fields of metadata + INFO
    - INFO  -- current zip + WARN
    - WARN  -- show wrong formatted, but readable fb2 in from zipfile/filename.fb2 + ERR
    - ERR   -- only real errors (i/o error, parse error and such other)
