# -*- coding: utf-8 -*-

import xmltodict
# import sqlite3
import urllib.parse
# import hashlib
# from flask import current_app
from .opds_internals import BOOKS_LIMIT, get_db_connection, get_dtiso, sizeof_fmt, get_authors, get_genres_names


ret_hdr_genre = {
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
                    # "@href": "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                # {
                    # "@href": "/opds/search?searchTerm={searchTerms}",
                    # "@rel": "search",
                    # "@type": "application/atom+xml"
                # },
                {
                    "@href": "/opds",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }


def get_genres_list():
    dtiso = get_dtiso()
    ret = ret_hdr_genre
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
                    "@href": "/opds/genres/" + gen_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    conn.close()
    return xmltodict.unparse(ret, pretty=True)


def get_genre_books(gen_id, page=0):
    dtiso = get_dtiso()
    ret = ret_hdr_genre

    REQ = 'SELECT id, description FROM genres WHERE id = "' + gen_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    genre = rows[0][1]

    ret["feed"]["id"] = "tag:root:genre:" + gen_id
    ret["feed"]["title"] = "Books in genre: " + genre + " by aplhabet"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": "/opds/genres/" + gen_id + "/" + str(page + 1),
            "@rel": "next",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    REQ0 = "SELECT zipfile, filename, genres, author_ids, book_id, book_title, lang, size, annotation"
    REQ1 = REQ0 + " FROM books WHERE (genres = '"  # fix E501 line too long
    REQ2 = "' OR genres LIKE '"
    REQ3 = ",%' OR genres LIKE '%,"
    REQ4 = "' OR genres LIKE '%,"
    REQ5 = ",%') ORDER BY book_title LIMIT " + str(BOOKS_LIMIT) + " OFFSET " + str(page * BOOKS_LIMIT) + ";"
    REQ = REQ1 + gen_id + REQ2 + gen_id + REQ3 + gen_id + REQ4 + gen_id + REQ5
    print(REQ)
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
        annotation = row["annotation"]

        authors = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": "/opds/a/" + k,
                    "name": v
                }
            )

        links = [
                    # {  # ToDo for over authors
                    # "@href": "/opds/author/" + author_id,
                    # "@rel": "related",
                    # "@title": "All books of author: '" + authors,  # ToDo: имя автора
                    # "@type": "application/atom+xml"
                    # }
                    # {  # ToDo for over sequences
                    # "@href": "/opds/sequencebooks/63116",
                    # "@rel": "related",
                    # "@title": "Все книги серии \"AYENA\"",
                    # "@type": "application/atom+xml"
                    # },

                    {
                        "@href": "/fb2/" + zipfile + "/" + filename,
                        "@rel": "http://opds-spec.org/acquisition/open-access",
                        "@type": "application/fb2+zip"
                    },
                    {
                        "@href": "/read/" + zipfile + "/" + filename,
                        "@rel": "alternate",
                        "@title": "Read in browser",
                        "@type": "text/html"
                    }
        ]

        category = []
        category_data = get_genres_names(genres)
        for k, v in category_data.items():
            category.append(
                {
                    "@label": v,
                    "@term": v
                }
            )
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>Lang: ru<br/>
        Size: %s<br/>Sequence: %s"<br/>
        """ % (annotation, sizeof_fmt(size), "")
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
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
    return xmltodict.unparse(ret, pretty=True)

