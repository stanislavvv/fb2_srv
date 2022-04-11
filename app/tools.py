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
                # {
                    # "updated": dtiso,
                    # "id": "tag:root:authors",
                    # "title": "По авторам",
                    # "content": {
                        # "@type": "text",
                        # "#text": "Поиск книг по авторам"
                    # },
                    # "link": {
                        # "@href": "/opds/authorsindex",
                        # "@type": "application/atom+xml;profile=opds-catalog"
                    # }
                # },
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
        s = i[field].upper()
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
                    "id": "tag:sequences:" + ch,
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/sequences/" + ch,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(seq_root) < 2:
        REQ1 = 'SELECT sequence_names as seq FROM books WHERE sequence_names like "'
        REQ2 = '%" OR sequence_names like ",'
        REQ3 = '%" GROUP BY seq ORDER BY seq;'
        REQ = REQ1 + seq_root + REQ2 + seq_root + REQ3
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:sequences:" + seq_root
        for ch in any2alphabet("seq", rows, 3):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequences:" + ch,
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/sequences/" + ch,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        print(type(seq_root), seq_root)
        REQ1 = 'SELECT sequence_names as seq FROM books WHERE sequence_names like "'
        REQ2 = '%" OR sequence_names like ",'
        REQ3 = '%" GROUP BY seq ORDER BY seq;'
        REQ = REQ1 + seq_root + REQ2 + seq_root + REQ3
        ret["feed"]["id"] = "tag:root:sequences:" + seq_root
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seqs = row["seq"]
            for seqname in seqs.split(","):
                ret["feed"]["entry"].append(
                    {
                        "updated": dtiso,
                        "id": "tag:sequence:" + urllib.parse.quote_plus(seqname),
                        "title": seqname,
                        "content": {
                            "@type": "text",
                            "#text": "книги на '" + seqname + "'"
                        },
                        "link": {
                            "@href": "/opds/sequencebooks/" + urllib.parse.quote_plus(seqname),
                            "@type": "application/atom+xml;profile=opds-catalog"
                        }
                    }
                )
        conn.close()
    return xmltodict.unparse(ret, pretty=True)


def get_books_in_seq(seq):
    dtiso = get_dtiso()
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:sequence:" + urllib.parse.quote_plus(seq) + ":",
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
    REQ = '''
        SELECT zipfile, filename, genres, authors, sequence, book_title, lang, annotation
        FROM books
        WHERE
        sequence = "%s"
        OR sequence like "\%,%s"
        OR sequence like "%s,\%"
        OR sequence like "\%,%s,\%"
        GROUP BY authors, book_title ORDER BY author, book_title
        ''' % (seq, seq, seq, seq)
    print(REQ)
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        authors = row["authors"]
        sequence = row["sequence"]
        book_title = row["book_title"]
        lang = row["lang"]
        annotation = row["annotation"]
        print(zipfile, filename)

        # for over authors
        author = [
            {
                "name": authors # ,
                # "uri": "/a/" + author_id
            }
        ]
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
        category = [  # жанры
            {
                "@label": "Любовное фэнтези, любовно-фантастические романы ",
                "@term": "Любовное фэнтези, любовно-фантастические романы "
            },
            {
                "@label": "Самиздат, сетевая литература",
                "@term": "Самиздат, сетевая литература"
            }
        ],
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>Lang: ru<br/>
        Size: %s<br/>Sequence: %s"<br/>
        """ % (annotation, "0k", seq)
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:book:" + hashlib.md5(book_title.encode('utf-8')).hexdigest(),
                "title": book_title,
                "author": author,
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
