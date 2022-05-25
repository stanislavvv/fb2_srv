# -*- coding: utf-8 -*-

from .opds_internals import get_db_connection, get_dtiso, get_authors, get_genres_names
from .opds_internals import get_seqs, sizeof_fmt, unurl
from flask import current_app


def ret_hdr_search():  # python does not have constants
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "updated": "0000-00-00_00:00",
            "title": "Books by authors",
            "icon": "/favicon.ico",
            "link": [
                # {
                    # "@href": current_app.config['APPLICATION_ROOT'] + "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/search?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/",
                    "@rel": "up",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }


def get_search_main(s_term):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    if s_term is None:
        ret = ret_hdr_search()
        ret["feed"]["updated"] = dtiso
        ret["feed"]["id"] = "tag:search::"
    else:
        s_raw = unurl(s_term)
        ret = ret_hdr_search()
        ret["feed"]["id"] = "tag:search::%s" % s_raw
        ret["feed"]["updated"] = dtiso
        ret["feed"]["link"].append(
          {
            "updated": dtiso,
            "id": "tag:search:authors::",
            "title": "Search in authors names",
            "content": {
              "@type": "text",
              "#text": "Search in authors names"
            },
            "link": {
              "@href": approot + "/opds/search-authors?searchTerm=%s" % s_term,
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
        ret["feed"]["link"].append(
          {
            "updated": "2022-05-25T07:26:50+02:00",
            "id": "tag:search:title",
            "title": "Search in book titles",
            "content": {
              "@type": "text",
              "#text": "Поиск книг по названию"
            },
            "link": {
              "@href": "/opds/search-books?searchTerm=%s" % s_term,
              "@type": "application/atom+xml;profile=opds-catalog"
            }
          }
        )
    print(ret)
    return ret


def get_search_authors(s_term):
    dtiso = get_dtiso()
    s_raw = unurl(s_term)
    print(s_raw)
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_search()
    ret["feed"]["updated"] = dtiso
    REQ = '''
    SELECT id, name
    FROM authors
    WHERE U_UPPER(name) LIKE "%%%s%%"
    ORDER BY U_UPPER(name);
    ''' % s_raw.replace('"', '\"')  # simple quote: ToDo - change to more sophistic
    ret["feed"]["id"] = "tag:search::%s" % s_raw
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        auth_name = row["name"]
        auth_id = row["id"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:authors:" + auth_id,
                "title": auth_name,
                "content": {
                    "@type": "text",
                    "#text": "Books of author: " + auth_name
                },
                "link": {
                    "@href": approot + "/opds/author/" + auth_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    conn.close()
    return ret


def get_search_books(s_term):
    s_raw = unurl(s_term)
    ret = ret_hdr_search()
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_search()
    ret["feed"]["id"] = "tag:search:books::"
    ret["feed"]["title"] = "Search books by: '" + s_raw + "'"
    ret["feed"]["updated"] = dtiso

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        author_ids,
        seq_ids as sequence_ids,
        books.book_id as book_id,
        book_title,
        lang,
        size,
        date_time,
        annotation
    FROM books, books_descr
    WHERE
        books.book_id = books_descr.book_id
        AND U_UPPER(book_title) LIKE "%%%s%%"
        ORDER BY book_title;
    """ % s_raw.replace('"', '\"')  # simple quote: ToDo - change to more sophistic
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
        size = row["size"]
        date_time = row["date_time"]
        seq_ids = row["sequence_ids"]
        annotation = row["annotation"]

        authors = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
        seq_data = get_seqs(seq_ids)
        links = []
        for k, v in seq_data.items():
            links.append(
                {
                    "@href": approot + "/opds/sequencebooks/" + k,
                    "@rel": "related",
                    "@title": "All books in sequence '" + v + "'",
                    "@type": "application/atom+xml"
                }
            )

        links.append(
            {
                "@href": approot + "/fb2/" + zipfile + "/" + filename,
                "@rel": "http://opds-spec.org/acquisition/open-access",
                "@title": "Download",
                "@type": "application/fb2+zip"
            }
        )
        links.append(
            {
                "@href": approot + "/read/" + zipfile + "/" + filename,
                "@rel": "alternate",
                "@title": "Read in browser",
                "@type": "text/html"
            }
        )

        category = []
        category_data = get_genres_names(genres)
        for k, v in category_data.items():
            category.append(
                {
                    "@label": v,
                    "@term": k
                }
            )
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>
        Size: %s<br/>
        """ % (annotation, sizeof_fmt(size))
        ret["feed"]["entry"].append(
            {
                "updated": date_time,
                "id": "tag:book:" + book_id,
                "title": book_title,
                "author": authors,
                "link": links,
                "category": category,
                "dc:language": lang,
                "dc:format": "fb2",
                "content": {
                    "@type": "text/html",
                    "#text": annotext
                },
            }
        )
    conn.close()
    return ret
