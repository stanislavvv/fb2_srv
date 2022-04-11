# -*- coding: utf-8 -*-

import xmltodict
import datetime
import sqlite3
import urllib.parse
import hashlib
from flask import current_app


def get_db_connection():
    conn = sqlite3.connect(current_app.config['DBSQLITE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_dtiso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def main_opds():
    dtiso = get_dtiso()
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root",
            "title": current_app.config['TITLE'],
            "updated": dtiso,  # 2022-04-06T23:54:23+02:00
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
                },
                {
                    "@href": "/opds",
                    "@rel": "self",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": [
                {
                    "updated": dtiso,
                    "id": "tag:root:authors",
                    "title": "По авторам",
                    "content": {
                        "@type": "text",
                        "#text": "Поиск книг по авторам"
                    },
                    "link": {
                        "@href": "/opds/authorsindex",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:root:sequences",
                    "title": "По сериям",
                    "content": {
                        "@type": "text",
                        "#text": "Поиск книг по сериям"
                    },
                    "link": {
                        "@href": "/opds/sequencesindex",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:root:genre",
                    "title": "По жанрам",
                    "content": {
                        "@type": "text",
                        "#text": "Поиск книг по жанрам"
                    },
                    "link": {
                        "@href": "/opds/genres",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
        }
    }
    return xmltodict.unparse(ret, pretty=True)


def any2alphabet(field, sq3_rows, num):
    alphabet = {}
    for i in sq3_rows:
        s = i[field]
        alphabet[s[:num]] = 1
    return sorted(list(alphabet))


# seq_root - /opds/sequencesindex/(.*)
#   may be None, "" or / for /opds/sequencesindex
def get_sequences(seq_root):
    dtiso = get_dtiso()
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:sequences",
            "title": "Books by series",
            "updated": dtiso,  # 2022-04-06T23:54:23+02:00
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
    if seq_root is None or seq_root == "" or seq_root == "/" or not isinstance(seq_root, str):
        ALL_SEQUENCES = 'SELECT sequence FROM books GROUP BY sequence ORDER BY sequence;'
        conn = get_db_connection()
        rows = conn.execute(ALL_SEQUENCES).fetchall()
        for ch in any2alphabet("sequence", rows, 1):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequences:" + urllib.parse.quote(ch),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/sequences/" + urllib.parse.quote(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(seq_root) < 2:
        REQ1 = 'SELECT sequence_names as seq FROM books WHERE UPPER(sequence_names) like "'
        REQ2 = '%" OR sequence_names like "%,'
        REQ3 = '%" GROUP BY seq ORDER BY seq;'
        REQ = REQ1 + seq_root + REQ2 + seq_root + REQ3
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:sequences:" + urllib.parse.quote_plus(seq_root, encoding='utf-8')
        for ch in any2alphabet("seq", rows, 3):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequences:" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/sequences/" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        REQ1 = 'SELECT id, name FROM sequences WHERE name like "'
        REQ2 = '%" OR name like ",'
        REQ3 = '%" GROUP BY name ORDER BY name;'
        REQ = REQ1 + seq_root + REQ2 + seq_root + REQ3
        ret["feed"]["id"] = "tag:root:sequences:" + urllib.parse.quote_plus(seq_root, encoding='utf-8')
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seq_name = row["name"]
            seq_id = row["id"]
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequence:" + urllib.parse.quote_plus(seq_name, encoding='utf-8'),
                    "title": seq_name,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + seq_name + "'"
                    },
                    "link": {
                        "@href": "/opds/sequencebooks/" + seq_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return xmltodict.unparse(ret, pretty=True)


def get_authors(ids):
    ret = {}
    selector = []
    for i in ids.split(","):
        selector.append("'" + i + "'")
    REQ = "SELECT id, name FROM authors WHERE id IN (" + ",".join(selector) + ");"
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (author_id, name) = (row[0], row[1])
        ret[author_id] = name
    conn.close()
    return ret


def get_genres_names(genres_ids):
    ret = {}
    selector = []
    for i in genres_ids.split(","):
        selector.append("'" + i + "'")
    REQ = "SELECT id, description FROM genres WHERE id IN (" + ",".join(selector) + ");"
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (genre_id, description) = (row[0], row[1])
        ret[genre_id] = description
    conn.close()
    return ret


def get_books_in_seq(seq_id):
    dtiso = get_dtiso()
    REQ = 'SELECT id, name FROM sequences WHERE id = "' + seq_id + '"'
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    seq = rows[0][1]
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:sequence:" + urllib.parse.quote_plus(seq_id) + ":",
            "title": "Books in series: '" + seq + "'",
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
    REQ1 = 'SELECT zipfile, filename, genres, author_ids, book_title, lang, annotation FROM books WHERE sequence_ids = "'
    REQ2 = '" OR sequence_ids like "%,'
    REQ3 = '" OR sequence_ids like "'
    REQ4 = ',%" OR sequence_ids like "%,'
    REQ5 = '%" GROUP BY authors, book_title ORDER BY authors, book_title'
    REQ = REQ1 + seq_id + REQ2 + seq_id + REQ3 + seq_id + REQ4 + seq_id + REQ5
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    print(REQ)
    for row in rows:
        print(row)
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        book_title = row["book_title"]
        lang = row["lang"]
        annotation = row["annotation"]
        print(zipfile, filename)

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
        """ % (annotation, "0k", seq)
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:book:" + hashlib.md5(book_title.encode('utf-8')).hexdigest(),
                "title": book_title,
                "author": authors,
                "link": links,
                "category": category,
                "dc:language": lang,
                "dc:format": "fb2+zip",
                "content": {
                    "@type": "text/html",
                    "#text": annotext
                },

            }
        )
    conn.close()
    return xmltodict.unparse(ret, pretty=True)
