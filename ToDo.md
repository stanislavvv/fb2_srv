# BUGS:

  * duplicate links in entries to authors in /html/authorsequence/<auth_id>/<seq_id>
  * fb2parse() generate new authors from scratch

# ToDo:

  * sequences with numbers in annotation and sort by sequence numbers in sequence view
  * replace empty author to 'unknown' -- in progress
  * better show authors with quotes in name like 'Аквариум' (may be strip quotes from begin and end) -- in progress
  * utf8-ignore case in authors and sequences (sqlite comparation in python)
  * refactor utils/__init__.py and managedb,py - too many functions in one file -- in progress

# ToDo sometime:

  * full book metadata replacement list (json like `[ "zipfile/filename": { "authors": "....", ...}, ...]`)
  * chunk fb2 downloads (for memory economy, but it will not work in /read)
  * filter non-fb2 files in zip -- may be does not needed
