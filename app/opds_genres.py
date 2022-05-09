# -*- coding: utf-8 -*-

# import xmltodict
# import sqlite3
# import urllib.parse
# import hashlib
from flask import current_app
from .opds_internals import BOOKS_LIMIT, get_db_connection, get_dtiso, sizeof_fmt
from .opds_internals import get_authors, get_genres_names, get_seqs


def ret_hdr_genre():
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:genre",
            "updated": "0000-00-00_00:00",
            "title": "Books by genres",
            "icon": "/favicon.ico",
            "link": [
                # {
                    # "@href": current_app.config['APPLICATION_ROOT'] + "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                # {
                    # "@href": current_app.config['APPLICATION_ROOT'] + "/opds/search?searchTerm={searchTerms}",
                    # "@rel": "search",
                    # "@type": "application/atom+xml"
                # },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }


def get_genres_list():
    dtiso = get_dtiso()
    ret = ret_hdr_genre()
    ret["feed"]["updated"] = dtiso

    REQ = 'SELECT id, description, `group` FROM genres ORDER BY `group`, description;'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        genre = row["description"]
        gen_id = row["id"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:genre:" + gen_id,
                "title": genre,
                "content": {
                    "@type": "text",
                    "#text": "Books in genre '" + genre + "'"
                },
                "link": {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/" + gen_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    conn.close()
    return ret


def get_genre_books(gen_id, page=0):
    dtiso = get_dtiso()
    ret = ret_hdr_genre()

    REQ = 'SELECT id, description FROM genres WHERE id = "' + gen_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    genre = rows[0][1]

    ret["feed"]["id"] = "tag:root:genre:" + gen_id
    ret["feed"]["title"] = "Books in genre: " + genre + " by aplhabet"
    ret["feed"]["updated"] = dtiso
    if page == 0:
        ret["feed"]["link"].append(
            {
                "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/",
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    else:
        if page == 1:
            ret["feed"]["link"].append(
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/" + gen_id,
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        else:
            ret["feed"]["link"].append(
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/" + gen_id + "/" + str(page - 1),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        ret["feed"]["link"].append(
            {
                "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/" + gen_id,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )

    REQ0 = "SELECT zipfile, filename, genres, author_ids, seq_ids as sequence_ids,"
    REQ0 = REQ0 + " book_id, book_title, lang, size, date_time, annotation"
    REQ1 = REQ0 + " FROM books WHERE (genres = '"  # fix E501 line too long
    REQ2 = "' OR genres LIKE '"
    REQ3 = "|%' OR genres LIKE '%|"
    REQ4 = "' OR genres LIKE '%|"
    REQ5 = "|%') ORDER BY book_title LIMIT " + str(BOOKS_LIMIT) + " OFFSET " + str(page * BOOKS_LIMIT) + ";"
    REQ = REQ1 + gen_id + REQ2 + gen_id + REQ3 + gen_id + REQ4 + gen_id + REQ5
    rows = conn.execute(REQ).fetchall()
    rows_count = len(rows)
    if rows_count >= BOOKS_LIMIT:
        ret["feed"]["link"].append(
            {
                "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres/" + gen_id + "/" + str(page + 1),
                "@rel": "next",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
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
                    "uri": "/opds/author/" + k,
                    "name": v
                }
            )
        seq_data = get_seqs(seq_ids)
        links = []
        for k, v in seq_data.items():
            links.append(
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/sequencebooks/" + k,
                    "@rel": "related",
                    "@title": "All books in sequence '" + v + "'",
                    "@type": "application/atom+xml"
                }
            )

        links.append(
            {
                "@href": current_app.config['APPLICATION_ROOT'] + "/fb2/" + zipfile + "/" + filename,
                "@rel": "http://opds-spec.org/acquisition/open-access",
                "@title": "Download",
                "@type": "application/fb2+zip"
            }
        )
        links.append(
            {
                "@href": current_app.config['APPLICATION_ROOT'] + "/read/" + zipfile + "/" + filename,
                "@rel": "alternate",
                "@title": "Read in browser",
                "@type": "text/html"
            }
        )
        # {  # ToDo for over authors
        # "@href": current_app.config['APPLICATION_ROOT'] + "/opds/author/" + author_id,
        # "@rel": "related",
        # "@title": "All books of author: '" + authors,  # ToDo: имя автора
        # "@type": "application/atom+xml"
        # }

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
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>Lang: ru<br/>
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
