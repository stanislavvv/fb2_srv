# BUGS:

  * [minor] duplicate links in entries to authors in /html/authorsequence/<auth_id>/<seq_id> -- in html mode only. won't fix?
  * [minor] set nickname to author without brackets, if other fields empty
  * [minor] strip leading spaces from authors/sequences/book titles before placing to database (may be after id calculation)
  * [normal] fb2parse() generate new authors from scratch (from name 'aaa & bbb' generate 'aaa' + 'bbb') -- need testing
  * [normal] quote /'"`/ and similar symbols -- in progress
  * [normal] author names in pine-quotes like '«Адам Смит»' must be stripped

# ToDo:

  * refactor utils/__init__.py and managedb,py - too many functions in one file -- in progress (stalled)
  * replace 'H' (latin) to 'Н' (cyrillic) in cyrillic names

# ToDo sometime:

  * filter non-fb2 files in zip -- may be does not needed
