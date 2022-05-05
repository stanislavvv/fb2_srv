# BUGS:

  * [minor] duplicate links in entries to authors in /html/authorsequence/<auth_id>/<seq_id>
  * [normal] fb2parse() generate new authors from scratch (from name 'aaa & bbb' generate 'aaa' + 'bbb') -- need testing

# ToDo:

  * sequences with numbers in annotation and sort by sequence numbers in sequence view -- in progress
  * refactor utils/__init__.py and managedb,py - too many functions in one file -- in progress (stalled)
  * replace 'H' (latin) to 'Н' (cyrillic) in cyrillic names

# ToDo sometime:

  * chunk fb2 downloads (for memory economy, but it will not work in /read)
  * filter non-fb2 files in zip -- may be does not needed
