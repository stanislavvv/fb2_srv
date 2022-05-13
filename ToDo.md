# BUGS:

  * [minor] duplicate links in entries to authors in /html/authorsequence/<auth_id>/<seq_id> -- in html mode only. won't fix?
  * [minor] set nickname to author without brackets, if other fields empty
  * [minor] strip leading spaces from authors/sequences/book titles before placing to database (may be after id calculation)
  * [minor] join multiline description with spaces as separator (minimum), or process it to `<p>line 1</p><p>line 2</p><p>...` (better)
  * [normal] fb2parse() generate new authors from scratch (from name 'aaa & bbb' generate 'aaa' + 'bbb') -- need testing
  * [normal] quote /'"`/ and similar symbols -- need testing

# ToDo:

  * refactor utils/__init__.py and managedb,py - too many functions in one file -- in progress (stalled)
  * replace 'H' (latin) to 'Н' (cyrillic) in cyrillic seq/author names
  * add command for removal of authors/sequences without books. Call it `managedb.py fsck. Use 'vacuum' as last SQL command.`
  * add logging of wrong-formatted fb2 to `managedb.py`
  * check interface speed in case annotations was taken directly from zip/fb2
  * input fields validation

# ToDo sometime:

  * filter non-fb2 files in zip -- may be does not needed
