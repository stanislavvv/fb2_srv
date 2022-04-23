# BUGS:

  * duplicate entries to authors in /html/authorsequence/<auth_id>/<seq_id>
  * must not be added link to next page when count of output data lower than limit

# ToDo:

  * fb2 download
  * read books in browser (simply pass it over xsltproc)
  * links to genres in book entry at /genres/<genre> 
  * sequences with numbers in annotation and sort by sequence numbers in sequence view
  * replace empty author to 'unknown'
  * show authors with short name
  * better show authors with quotes in name like 'Аквариум' (may be strip quotes from begin and end)
  * full book metadata replacement list (json like `[ "zipfile/filename": { "authors": "....", ...}, ...]`)
