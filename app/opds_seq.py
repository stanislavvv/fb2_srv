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
                },
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/",
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
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/authorsindex",
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
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/sequencesindex",
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
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/genres",
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
    if seq_root is None or seq_root == "" or seq_root == "/" or not isinstance(seq_root, str):
        ALL_SEQUENCES = '''
        SELECT U_UPPER(name) as name
        FROM sequences
        GROUP BY name
        ORDER BY name;
        '''
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
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/sequences/" + urllib.parse.quote(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(seq_root) < 2:
        REQ = '''
        SELECT U_UPPER(name) as seq
        FROM sequences
        WHERE
            U_UPPER(name) like '%s%%'
            OR U_UPPER(name) like '%%|%s%%'
        GROUP BY seq
        ORDER BY seq;
        ''' % (seq_root, seq_root)
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:sequences:" + urllib.parse.quote(seq_root, encoding='utf-8')
        for ch in any2alphabet("seq", rows, 3):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequences:" + urllib.parse.quote(ch, encoding='utf-8'),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + ch + "'"
                    },
                    "link": {
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/sequences/" + urllib.parse.quote(ch, encoding='utf-8'),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        REQ = '''
        SELECT id, name
        FROM sequences
        WHERE
            U_UPPER(name) like '%s%%'
            OR U_UPPER(name) like '%%|%s%%'
        GROUP BY name
        ORDER BY name;
        ''' % (seq_root, seq_root)
        ret["feed"]["id"] = "tag:root:sequences:" + urllib.parse.quote(seq_root, encoding='utf-8')
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seq_name = row["name"]
            seq_id = row["id"]
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:sequence:" + urllib.parse.quote(seq_name, encoding='utf-8'),
                    "title": seq_name,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + seq_name + "'"
                    },
                    "link": {
                        "@href": current_app.config['APPLICATION_ROOT'] + "/opds/sequencebooks/" + seq_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return ret


def get_books_in_seq(seq_id):
    dtiso = get_dtiso()
    REQ = 'SELECT id, name FROM sequences WHERE id = "%s"' % seq_id
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
    REQ = '''
    SELECT
        books.zipfile as zipfile,
        books.filename as filename,
        books.genres as genres,
        books.author_ids as author_ids,
        books.seq_ids as sequence_ids,
        books.book_id as book_id,
        book_title,
        lang,
        size,
        date_time,
        annotation,
        seq_books.seq_num as s_num
    FROM books, books_descr, seq_books
    WHERE
        seq_books.seq_id = '%s'
        AND books.zipfile = seq_books.zipfile
        AND books.filename = seq_books.filename
        AND books_descr.book_id = books.book_id
        AND (sequence_ids = "%s"
            OR sequence_ids like '%%|%s'
            OR sequence_ids like '%s|%%'
            OR sequence_ids like '%%|%s|%%'
        )
        ORDER BY s_num, book_title;
    ''' % (seq_id, seq_id, seq_id, seq_id, seq_id)
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
        seq_num = row["s_num"]

        authors = []
        links = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": current_app.config['APPLICATION_ROOT'] + "/opds/author/" + k,
                    "name": v
                }
            )
            links.append(
                {
                    "@href": current_app.config['APPLICATION_ROOT'] + "/opds/author/" + k,
                    "@rel": "related",
                    "@title": v,
                    "@type": "application/atom+xml"
                }
            )

        seq_data = get_seqs(seq_ids)
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
        Size: %s<br/>Sequence: %s, Number: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq, str(seq_num))
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
