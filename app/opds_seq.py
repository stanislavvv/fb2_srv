# -*- coding: utf-8 -*-

import urllib.parse
from flask import current_app

from .opds_internals import get_db_connection, get_dtiso, any2alphabet, get_genres_names, sizeof_fmt
from .opds_internals import get_book_authors, get_book_seqs, get_seq_books, get_books_info
from .opds_internals import get_seq_link, get_book_link, get_book_entry


def main_opds():
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
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
                    # "@href": approot + "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                {
                    "@href": approot + "/opds/search?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": approot + "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                },
                {
                    "@href": approot + "/opds/",
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
                        "#text": "По авторам"
                    },
                    "link": {
                        "@href": approot + "/opds/authorsindex",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:root:sequences",
                    "title": "По сериям",
                    "content": {
                        "@type": "text",
                        "#text": "По сериям"
                    },
                    "link": {
                        "@href": approot + "/opds/sequencesindex",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:root:genre",
                    "title": "По жанрам",
                    "content": {
                        "@type": "text",
                        "#text": "По жанрам"
                    },
                    "link": {
                        "@href": approot + "/opds/genres",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:root:zips",
                    "title": "По архивам",
                    "content": {
                        "@type": "text",
                        "#text": "По архивам"
                    },
                    "link": {
                        "@href": approot + "/opds/zips",
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
    approot = current_app.config['APPLICATION_ROOT']
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:sequences",
            "title": "Серии книг",
            "updated": dtiso,  # 2022-04-06T23:54:23+02:00
            "icon": "/favicon.ico",
            "link": [
                # {
                    # "@href": approot + "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                {
                    "@href": approot + "/opds/search?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": approot + "/opds/",
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
                        "#text": "Серии на '" + ch + "'"
                    },
                    "link": {
                        "@href": approot + "/opds/sequences/" + urllib.parse.quote(ch),
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
        ret["feed"]["title"] = "Серии книг на '" + seq_root + "'"
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
                        "@href": approot + "/opds/sequences/" + urllib.parse.quote(ch, encoding='utf-8'),
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
        GROUP BY U_UPPER(name)
        ORDER BY U_UPPER(name);
        ''' % (seq_root, seq_root)
        ret["feed"]["id"] = "tag:root:sequences:" + urllib.parse.quote(seq_root, encoding='utf-8')
        ret["feed"]["title"] = "Серии книг на '" + seq_root + "'"
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
                        "@href": approot + "/opds/sequencebooks/" + seq_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return ret


def get_books_in_seq(seq_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
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
                    # "@href": approot + "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                {
                    "@href": approot + "/opds/search?searchTerm={searchTerms}",
                    "@rel": "search",
                    "@type": "application/atom+xml"
                },
                {
                    "@href": approot + "/opds/",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }
    books = get_seq_books(seq_id)
    book_ids = []
    books_seq_num = {}
    for book in books:
        book_ids.append(book["book_id"])
        books_seq_num[book["book_id"]] = book["seq_num"]
    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]
    REQ = '''
    SELECT
        books.zipfile as zipfile,
        books.filename as filename,
        books.genres as genres,
        books.book_id as book_id,
        lang,
        size,
        date_time
    FROM books
    WHERE
        book_id IN ("%s")
    ''' % '","'.join(book_ids)
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    data = []
    for row in rows:
        book_id = row["book_id"]
        data.append(
            {
                "zipfile": row["zipfile"],
                "filename": row["filename"],
                "genres": row["genres"],
                "book_id": row["book_id"],
                "lang": row["lang"],
                "size": row["size"],
                "date_time": row["date_time"],
                "book_title": book_titles[book_id],
                "annotation": book_anno[book_id],
                "seq_num": books_seq_num[book_id],
            }
        )

    for d in sorted(data, key=lambda s: s['seq_num'] or -1):
        book_id = d["book_id"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]
        lang = d["lang"]
        size = d["size"]
        date_time = d["date_time"]
        book_title = d["book_title"]
        annotation = d["annotation"]
        seq_num = d["seq_num"]

        authors = []
        links = []
        authors_data = get_book_authors(book_id)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
            links.append(
                {
                    "@href": approot + "/opds/author/" + k,
                    "@rel": "related",
                    "@title": v,
                    "@type": "application/atom+xml"
                }
            )

        seq_data = get_book_seqs(book_id)
        for k, v in seq_data.items():
            links.append(get_seq_link(approot, k, v))

        links.append(get_book_link(approot, zipfile, filename, 'dl'))
        links.append(get_book_link(approot, zipfile, filename, 'read'))

        category = []
        category_data = get_genres_names(genres)
        for k, v in category_data.items():
            category.append(
                {
                    "@label": v,
                    "@term": k
                }
            )
        if seq_num is None:
            s_num = ""
        else:
            s_num = str(seq_num)
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>Серия: %s, номер: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq, s_num)
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    conn.close()
    return ret
