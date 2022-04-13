# -*- coding: utf-8 -*-

import xmltodict
# import sqlite3
import urllib.parse
# import hashlib
# from flask import current_app
from .opds_seq import get_db_connection, get_dtiso, any2alphabet, get_authors, get_genres_names


def get_authors_list(auth_root):
    dtiso = get_dtiso()
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "title": "Books by authors",
            "updated": dtiso,
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
    if auth_root is None or auth_root == "" or auth_root == "/" or not isinstance(auth_root, str):
        ALL_AUTHORS = 'SELECT name FROM authors ORDER BY name;'
        conn = get_db_connection()
        rows = conn.execute(ALL_AUTHORS).fetchall()
        for ch in any2alphabet("name", rows, 1):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + urllib.parse.quote(ch),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Авторы на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/authorsindex/" + urllib.parse.quote(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(auth_root) < 2:
        REQ = 'SELECT name FROM authors WHERE name like "' + auth_root + '%";'
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:authors:" + urllib.parse.quote_plus(auth_root, encoding='utf-8')
        for ch in any2alphabet("name", rows, 3):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Авторы на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/authors/" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        REQ = 'SELECT id, name FROM authors WHERE name LIKE "' + auth_root + '%" ORDER BY name;'
        ret["feed"]["id"] = "tag:root:authors:" + urllib.parse.quote_plus(auth_root, encoding='utf-8')
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
                        "@href": "/opds/author/" + auth_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return xmltodict.unparse(ret, pretty=True)


def get_author_list(auth_id):
    dtiso = get_dtiso()
    REQ = 'SELECT id, name, info FROM authors WHERE id = "' + auth_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    auth_info = rows[0][2]
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:author:" + auth_id,
            "title": "Books of author: " + auth_name + "",
            "updated": dtiso,
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
            "entry": [
                {
                    "updated": dtiso,
                    "id": "tag:author:bio:" + auth_id,
                    "title": "About author",
                    "link": [
                        # {
                        #     "@href": "/a/218498",
                        #     "@rel": "alternate",
                        #     "@title": "Страница автора на сайте",
                        #     "@type": "text/html"
                        # },
                        {
                            "@href": "/opds/authorsequences/218498",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Author books by sequences",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        },
                        {
                            "@href": "/opds/authorsequenceless/218498",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Книги автора вне серий",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    ],
                    "content": {
                        "@type": "text/html",
                        "#text": "<p><span style=\"font-weight:bold\">" + auth_name + "</span></p>" + auth_info
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequences",
                    "title": "Books by sequences",
                    "link": {
                        "@href": "/opds/author/" + auth_id + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequenceless",
                    "title": "Books outside of sequences",
                    "link": {
                        "@href": "/opds/author/" + auth_id + "/authorsequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":alphabet",
                    "title": "Books by alphabet",
                    "link": {
                        "@href": "/opds/author/" + auth_id + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":time",
                    "title": "Books by entry date",
                    "link": {
                        "@href": "/opds/author/" + auth_id + "/time",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
        }
    }
    conn.close()
    return xmltodict.unparse(ret, pretty=True)


# return [ { "name": seq_name, "id": seq_id, "count": books_count }, ...]
def get_auth_seqs(auth_id):
    ret = []
    seq_cnt = {}
    REQ1 = "SELECT book_id, sequence_ids FROM books WHERE length(sequence_ids) > 0 AND author_ids = '"
    REQ2 = "' OR author_ids LIKE '"
    REQ3 = ",%' OR author_ids LIKE '%,"
    REQ4 = "' OR author_ids LIKE '%,"
    REQ5 = ",%' AND sequence_ids != '';"
    REQ = REQ1 + auth_id + REQ2 + auth_id + REQ3 + auth_id + REQ4 + auth_id + REQ5
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) != 0:
        for row in rows:
            # book_id = row["book_id"]
            seq_ids = row["sequence_ids"]
            for seq in seq_ids.split(","):
                if seq is not None and seq != "":
                    if seq not in seq_cnt:
                        seq_cnt[seq] = 1
                    else:
                        seq_cnt[seq] = 1 + seq_cnt[seq]
        selector = []
        for k, v in seq_cnt.items():
            selector.append('"' + k + '"')
        REQ = 'SELECT id, name FROM sequences WHERE id IN (' + ",".join(selector) + ') ORDER BY name;'
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seq_id = row["id"]
            seq_name = row["name"]
            if seq_id in seq_cnt:
                ret.append({"name": seq_name, "id": seq_id, "count": seq_cnt[seq_id]})
    conn.close()
    return ret


def get_author_sequences(auth_id):
    dtiso = get_dtiso()
    REQ = 'SELECT id, name FROM authors WHERE id = "' + auth_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:author:" + auth_id,
            "title": "Books of author: " + auth_name + "",
            "updated": dtiso,
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
    seqs = get_auth_seqs(auth_id)
    for seq in seqs:
        seq_name = seq["name"]
        seq_id = seq["id"]
        seq_cnt = seq["count"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:author:" + auth_id + ":sequence:" + seq_id,
                "title": seq_name,
                "content": {
                    "@type": "text",
                    "#text": str(seq_cnt) + " book(s) in sequence"
                },
                "link": {
                    "@href": "/opds/authorsequence/" + auth_id + "/" + seq_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            },
        )
    conn.close()
    return xmltodict.unparse(ret, pretty=True)


def get_author_sequence(auth_id, seq_id):
    dtiso = get_dtiso()
    REQ = 'SELECT id, name FROM authors WHERE id = "' + auth_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    REQ = 'SELECT id, name FROM sequences WHERE id = "' + seq_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    seq_name = rows[0][1]
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:author:" + auth_id + ":sequence:" + seq_id,
            "title": "Books in sequence: " + seq_name + " by author: " + auth_name,
            "updated": dtiso,
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
    REQ0 = "SELECT zipfile, filename, genres, author_ids, book_id, book_title, lang, annotation"
    REQ1 = REQ0 + " FROM books WHERE (author_ids = '"  # fix E501 line too long
    REQ2 = "' OR author_ids LIKE '"
    REQ3 = ",%' OR author_ids LIKE '%,"
    REQ4 = "' OR author_ids LIKE '%,"
    REQ5 = ",%') AND (sequence_ids = '"
    REQ6 = "' OR sequence_ids LIKE '"
    REQ7 = ",%' OR sequence_ids LIKE '%,"
    REQ8 = "' OR sequence_ids LIKE '%,"
    REQ9 = ",%');"
    REQ = REQ1 + auth_id + REQ2 + auth_id + REQ3 + auth_id + REQ4 + auth_id + REQ5 + seq_id + REQ6 + seq_id + REQ7
    REQ = REQ + seq_id + REQ8 + seq_id + REQ9  # fix E501 line too long
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
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
        """ % (annotation, "0k", seq_name)
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
