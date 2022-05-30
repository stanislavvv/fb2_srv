# BUGS:

  * [minor] generate correct html description from existing data (close open tags and so on) -- need testing

# ToDo:

  * add special cases for parsing wrong formatted sequence info from form: '<sequence number="« name=»Эссе"/>' (same bug in .inp)
  * use field `date` from `.inp` if exists (fb2 date does not correspond with file date)
  * add command for removal of authors/sequences without books. Call it `managedb.py` fsck. Use 'vacuum' as last SQL command. -- in progress
  * search several words in any order
  * search must ignore similar letters (like cyrillic 'е' and 'ё' or diacritic symbols)
  * replace 'H' (latin) to 'Н' (cyrillic) in cyrillic seq/author names before save it to database
  * check interface speed in case annotations was taken directly from zip/fb2

# ToDo sometime:

  * add configurable logging in `managedb.py` with levels:
    - DEBUG -- current zip, current book, may be show some fields of metadata + INFO
    - INFO  -- current zip + WARN
    - WARN  -- show wrong formatted, but readable fb2 in from zipfile/filename.fb2 + ERR
    - ERR   -- only real errors (i/o error, parse error and such other)
  * filter non-fb2 files in zip -- may be does not needed
