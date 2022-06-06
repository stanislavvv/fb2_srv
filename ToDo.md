# BUGS:

  * [minor] generate correct html description from existing data (close open tags and so on) -- need testing

# ToDo:

  * search must ignore similar letters (like cyrillic 'е' and 'ё' or diacritic symbols) -- testing
  * genres from MyHomeLib and hierarchical sort with subheaders
  * check interface speed in case annotations was taken directly from zip/fb2
  * add command for removal of authors/sequences without books. Call it `managedb.py` fsck. Use 'vacuum' as last SQL command. -- stalled

# ToDo sometime:

  * add configurable logging in `managedb.py` with levels:
    - DEBUG -- current zip, current book, may be show some fields of metadata + INFO
    - INFO  -- current zip + WARN
    - WARN  -- show wrong formatted, but readable fb2 in from zipfile/filename.fb2 + ERR
    - ERR   -- only real errors (i/o error, parse error and such other)
  * filter non-fb2 files in zip -- may be does not needed
