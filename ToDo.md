# BUGS:

  * exists

# ToDo:

  * add command for removal of authors/sequences without books. Call it `managedb.py` fsck. Use 'vacuum' as last SQL command. -- need testing

# ToDo sometime:

  * add configurable logging in `managedb.py` with levels:
    - DEBUG -- current zip, current book, may be show some fields of metadata + INFO
    - INFO  -- current zip + WARN
    - WARN  -- show wrong formatted, but readable fb2 in from zipfile/filename.fb2 + ERR
    - ERR   -- only real errors (i/o error, parse error and such other)
  * filter non-fb2 files in zip -- may be does not needed
