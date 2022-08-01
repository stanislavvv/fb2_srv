# -*- coding: utf-8 -*-

from .opds_internals import get_db_connection, get_dtiso, get_genres_names, get_book_authors
from .opds_internals import get_auth_seqs, sizeof_fmt, url_str, unurl, any2alphabet
from .opds_internals import get_book_seqs, get_books_info, get_author_books, get_seq_books
from .opds_internals import get_seq_link, get_book_link, get_book_entry
from flask import current_app


def ret_hdr_author():  # python does not have constants
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
                }
            ],
            "entry": []
        }
    }


def get_authors_list(auth_root):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    a_root = unurl(auth_root)
    if a_root is None or a_root == "" or a_root == "/" or not isinstance(a_root, str):
        ret = ret_hdr_author()
        ret["feed"]["updated"] = dtiso
        ret["feed"]["title"] = "Авторы"
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/",
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
        ALL_AUTHORS = '''
        SELECT U_UPPER(substr(name, 1, 1)) as nm
        FROM authors
        GROUP BY nm
        ORDER BY nm;'''
        conn = get_db_connection()
        rows = any2alphabet("nm", conn.execute(ALL_AUTHORS).fetchall(), 1)
        for ch in rows:
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + ch,
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Authors beginnging from '" + ch + "'"
                    },
                    "link": {
                        "@href": approot + "/opds/authorsindex/" + url_str(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(a_root) < 2:
        ret = ret_hdr_author()
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/authorsindex/",
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
        ret["feed"]["updated"] = dtiso
        REQ = '''SELECT U_UPPER(substr(name,1,3)) as nm
        FROM authors
        WHERE U_UPPER(name) like "%s%%"
        GROUP BY nm ORDER BY nm;''' % a_root
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["title"] = "Авторы на '" + a_root + "'"
        ret["feed"]["id"] = "tag:root:authors:" + a_root
        for row in rows:
            ch = row["nm"]
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + url_str(ch),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Authors beginnging from '" + ch + "'"
                    },
                    "link": {
                        "@href": approot + "/opds/authorsindex/" + url_str(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        ret = ret_hdr_author()
        ret["feed"]["title"] = "Авторы на '" + a_root + "'"
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/authorsindex/",
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
        ret["feed"]["updated"] = dtiso
        REQ = '''
        SELECT id, name
        FROM authors
        WHERE U_UPPER(name) LIKE "%s%%"
        ORDER BY U_UPPER(name);
        ''' % a_root
        ret["feed"]["id"] = "tag:root:authors:" + url_str(a_root)
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


def get_author_list(auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name, info FROM authors WHERE id = "%s"' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    auth_info = rows[0][2]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id
    ret["feed"]["title"] = "Книги автора '" + auth_name + "'"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/authorsindex/",
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["entry"] = [
                {
                    "updated": dtiso,
                    "id": "tag:author:bio:" + auth_id,
                    "title": "Об авторе",
                    "link": [
                        {
                            "@href": approot + "/opds/author/" + auth_id + "/sequences",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Books of author by sequences",
                            "@type": "application/atom+xml;profile=opds-catalog"
                        },
                        {
                            "@href": approot + "/opds/author/" + auth_id + "/sequenceless",
                            "@rel": "http://www.feedbooks.com/opds/facet",
                            "@title": "Sequenceless books of author",
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
                    "title": "По сериям",
                    "link": {
                        "@href": approot + "/opds/author/" + auth_id + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":sequenceless",
                    "title": "Вне серий",
                    "link": {
                        "@href": approot + "/opds/author/" + auth_id + "/sequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":alphabet",
                    "title": "По алфавиту",
                    "link": {
                        "@href": approot + "/opds/author/" + auth_id + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + auth_id + ":time",
                    "title": "По дате добавления",
                    "link": {
                        "@href": approot + "/opds/author/" + auth_id + "/time",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
    conn.close()
    return ret


def get_author_sequences(auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name FROM authors WHERE id = "%s" ORDER BY U_UPPER(name)' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id
    ret["feed"]["title"] = "Книги автора '" + auth_name + "' по сериям"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/author/" + auth_id,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    seqs = get_auth_seqs(auth_id)
    data = []
    for seq in seqs:
        seq_name = seq["name"]
        seq_id = seq["id"]
        seq_cnt = seq["count"]
        data.append({"name": seq_name, "id": seq_id, "count": seq_cnt})
    for d in sorted(data, key=lambda s: s['name'] or -1):
        seq_name = d["name"]
        seq_id = d["id"]
        seq_cnt = d["count"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:author:" + auth_id + ":sequence:" + seq_id,
                "title": seq_name,
                "content": {
                    "@type": "text",
                    "#text": str(seq_cnt) + " книг(и) в серии"
                },
                "link": {
                    "@href": approot + "/opds/authorsequence/" + auth_id + "/" + seq_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            },
        )
    conn.close()
    return ret


def get_author_sequence(auth_id, seq_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name FROM authors WHERE id = "%s"' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    REQ = 'SELECT id, name FROM sequences WHERE id = "%s"' % seq_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    seq_name = rows[0][1]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id + ":sequence:" + seq_id
    ret["feed"]["title"] = "Книги автора '" + auth_name + "' из серии '" + seq_name + "'"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/author/" + auth_id,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    book_ids_author = get_author_books(auth_id)
    book_ids_seq = get_seq_books(seq_id)
    book_ids = []
    book_seq_nums = {}
    for book in book_ids_seq:
        book_id = book["book_id"]
        book_seq_num = book["seq_num"]
        if book_id in book_ids_author:
            book_ids.append(book_id)
            book_seq_nums[book_id] = book_seq_num

    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        books.book_id as book_id,
        lang,
        size,
        date_time
    FROM books
    WHERE
        books.book_id IN ('%s')
    """ % "','".join(book_ids)
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
                "seq_num": book_seq_nums[book_id]
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
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>Серия: %s, номер: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq_name, str(seq_num))
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    conn.close()
    return ret


def get_author_sequenceless(auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name FROM authors WHERE id = "%s"' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id + ":sequenceless:"
    ret["feed"]["title"] = "Книги автора '" + auth_name + "' вне серий"
    ret["feed"]["updated"] = dtiso

    book_ids = get_author_books(auth_id)

    # filter books in any seq
    REQ_BOOK_INSEQ = """
    SELECT book_id FROM seq_books
    WHERE book_id IN ('%s')
    """ % "','".join(book_ids)
    rows = conn.execute(REQ_BOOK_INSEQ).fetchall()
    for row in rows:
        book_ids.remove(row[0])

    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        books.book_id as book_id,
        lang,
        size,
        date_time
    FROM books
    WHERE
        books.book_id IN ('%s')
    """ % "','".join(book_ids)
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
            }
        )

    for d in sorted(data, key=lambda s: s['book_title']):
        book_id = d["book_id"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]
        lang = d["lang"]
        size = d["size"]
        date_time = d["date_time"]
        book_title = d["book_title"]
        annotation = d["annotation"]

        authors = []
        authors_data = get_book_authors(book_id)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
        links = []
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
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/><br/>
        """ % (annotation, sizeof_fmt(size))
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    conn.close()
    return ret


def get_author_by_alphabet(auth_id):
    ret = ret_hdr_author()
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name FROM authors WHERE id = "%s"' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id + ":books:alphabet:"
    ret["feed"]["title"] = "Books of author: " + auth_name + " by aplhabet"
    ret["feed"]["updated"] = dtiso

    book_ids = get_author_books(auth_id)

    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        books.book_id as book_id,
        lang,
        size,
        date_time
    FROM books
    WHERE
        books.book_id IN ('%s')
    """ % "','".join(book_ids)
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
                "annotation": book_anno[book_id]
            }
        )

    for d in sorted(data, key=lambda s: s['book_title']):
        book_id = d["book_id"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]
        lang = d["lang"]
        size = d["size"]
        date_time = d["date_time"]
        book_title = d["book_title"]
        annotation = d["annotation"]

        authors = []
        authors_data = get_book_authors(book_id)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
        seq_data = get_book_seqs(book_id)
        links = []
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
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>
        """ % (annotation, sizeof_fmt(size))
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    conn.close()
    return ret


def get_author_by_time(auth_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    REQ = 'SELECT id, name FROM authors WHERE id = "%s"' % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    auth_name = rows[0][1]
    ret = ret_hdr_author()
    ret["feed"]["id"] = "tag:author:" + auth_id + ":books:time:"
    ret["feed"]["title"] = "Книги автора '" + auth_name + "' по дате добавления"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/author/" + auth_id,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    book_ids = get_author_books(auth_id)

    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        books.book_id as book_id,
        lang,
        size,
        date_time
    FROM books
    WHERE
        books.book_id IN ('%s')
    """ % "','".join(book_ids)
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
            }
        )

    for d in sorted(data, key=lambda s: s['date_time']):
        book_id = d["book_id"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]
        lang = d["lang"]
        size = d["size"]
        date_time = d["date_time"]
        book_title = d["book_title"]
        annotation = d["annotation"]

        authors = []
        authors_data = get_book_authors(book_id)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
        seq_data = get_book_seqs(book_id)
        links = []
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
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>формат: fb2<br/>
        размер: %s<br/>
        """ % (annotation, sizeof_fmt(size))
        ret["feed"]["entry"].append(
            get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext)
        )
    conn.close()
    return ret
