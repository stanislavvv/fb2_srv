# -*- coding: utf-8 -*-

# import xmltodict
# import datetime
# import sqlite3
import urllib.parse
# import hashlib
from flask import current_app

from .opds_internals import get_db_connection, get_dtiso, any2alphabet, get_authors, get_genres_names, sizeof_fmt
from .opds_internals import get_seqs


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
                    "@href": "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                },
                {
                    "@href": "/opds/",
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
    return ret


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
                    "@href": "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }
    if seq_root is None or seq_root == "" or seq_root == "/" or not isinstance(seq_root, str):
        ALL_SEQUENCES = 'SELECT name FROM sequences GROUP BY name ORDER BY name;'
        conn = get_db_connection()
        rows = conn.execute(ALL_SEQUENCES).fetchall()
        for ch in any2alphabet("name", rows, 1):
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
        REQ1 = 'SELECT name as seq FROM sequences WHERE UPPER(name) like "'
        REQ2 = '%" GROUP BY seq ORDER BY seq;'
        REQ = REQ1 + seq_root + REQ2
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
        REQ2 = '%" OR name like "%|'
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
            "id": "tag:sequence:" + seq_id + ":",
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
                    "@href": "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }
    REQ1 = 'SELECT zipfile, filename, genres, author_ids, sequence_ids,'
    REQ1 = REQ1 + ' book_id, book_title, lang, size, date_time, annotation'
    REQ1 = REQ1 + ' FROM books WHERE sequence_ids = "'  # fix E501 line too long
    REQ2 = '" OR sequence_ids like "%|'
    REQ3 = '" OR sequence_ids like "'
    REQ4 = '|%" OR sequence_ids like "%|'
    REQ5 = '%" GROUP BY authors, book_title ORDER BY authors, book_title'
    REQ = REQ1 + seq_id + REQ2 + seq_id + REQ3 + seq_id + REQ4 + seq_id + REQ5
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        seq_ids = row["sequence_ids"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
        size = row["size"]
        date_time = row["date_time"]
        annotation = row["annotation"]

        authors = []
        links = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": "/opds/author/" + k,
                    "name": v
                }
            )
            links.append(
                {
                    "@href": "/opds/author/" + k,
                    "@rel": "related",
                    "@title": v,
                    "@type": "application/atom+xml"
                }
            )

        seq_data = get_seqs(seq_ids)
        for k, v in seq_data.items():
            links.append(
                {
                    "@href": "/opds/sequencebooks/" + k,
                    "@rel": "related",
                    "@title": "All books in sequence '" + v + "'",
                    "@type": "application/atom+xml"
                }
            )

        links.append(
            {
                "@href": "/fb2/" + zipfile + "/" + filename,
                "@rel": "http://opds-spec.org/acquisition/open-access",
                "@title": "Download",
                "@type": "application/fb2+zip"
            }
        )
        links.append(
            {
                "@href": "/read/" + zipfile + "/" + filename,
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
                    "@term": v
                }
            )
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>Lang: ru<br/>
        Size: %s<br/>Sequence: %s"<br/>
        """ % (annotation, sizeof_fmt(size), seq)
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
