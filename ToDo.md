# BUGS:

  * [minor] generate correct html description from existing data (close open tags and so on) -- need testing
  * [normal] fb2parse() generate new authors from scratch (from name 'aaa & bbb' generate 'aaa' + 'bbb') -- need testing
  * [normal] quote /'"`/ and similar symbols -- symbols stripped or replaced, need testing

# ToDo:

  * add command for removal of authors/sequences without books. Call it `managedb.py` fsck. Use 'vacuum' as last SQL command.` -- in progress
  * search must ignore similar letters (like cyrillic 'е' and 'ё' or diacritic symbols)
  * add special cases for parsing wrong formatted sequence info from form: '<sequence number="« name=»Эссе"/>'
  * replace 'H' (latin) to 'Н' (cyrillic) in cyrillic seq/author names
  * input fields validation
  * check interface speed in case annotations was taken directly from zip/fb2

# ToDo sometime:

  * add configurable logging in `managedb.py` with levels:
    - DEBUG -- current zip, current book, may be show some fields of metadata + INFO
    - INFO  -- current zip + WARN
    - WARN  -- show wrong formatted, but readable fb2 in from zipfile/filename.fb2 + ERR
    - ERR   -- only real errors (i/o error, parse error and such other)
  * filter non-fb2 files in zip -- may be does not needed
