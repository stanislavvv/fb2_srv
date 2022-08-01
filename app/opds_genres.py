# -*- coding: utf-8 -*-

from flask import current_app
from .opds_internals import get_db_connection, get_dtiso, sizeof_fmt, get_books_info
from .opds_internals import get_book_authors, get_genres_names, get_book_seqs
from .opds_internals import get_seq_link, get_book_link, get_book_entry


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


def get_genres_list(meta_id=None):
    dtiso = get_dtiso()
    ret = ret_hdr_genre()
    ret["feed"]["updated"] = dtiso
    approot = current_app.config['APPLICATION_ROOT']

    if meta_id is None:
        ret["feed"]["id"] = "tag:root:genre"
        ret["feed"]["title"] = "Группы жанров"
        REQ = '''
            SELECT meta_id, description
            FROM genres_meta
            ORDER BY description;
        '''
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            genre_meta = row["description"]
            meta_id = row["meta_id"]
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:genres:" + str(meta_id),
                    "title": genre_meta,
                    "content": {
                        "@type": "text",
                        "#text": "Genres in group '" + genre_meta + "'"
                    },
                    "link": {
                        "@href": approot + "/opds/genres/" + str(meta_id),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        REQ = '''
            SELECT description
            FROM genres_meta
            WHERE meta_id = "%s"
        ''' % meta_id
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:genre:" + meta_id
        if len(rows) > 0:
            row = rows[0]
            meta_name = row["description"]
            ret["feed"]["title"] = "Жанры группы '" + meta_name + "'"
        REQ = '''
            SELECT id, description
            FROM genres
            WHERE meta_id = "%s"
            ORDER BY description;
        ''' % meta_id
        # conn = get_db_connection()
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
                        "#text": "Поджанры в '" + genre + "'"
                    },
                    "link": {
                        "@href": approot + "/opds/genre/" + gen_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return ret


def get_genre_books(gen_id, page=0):
    dtiso = get_dtiso()
    ret = ret_hdr_genre()
    approot = current_app.config['APPLICATION_ROOT']

    REQ = 'SELECT id, description FROM genres WHERE id = "%s"' % gen_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    genre = rows[0][1]

    ret["feed"]["id"] = "tag:root:genre:" + gen_id
    ret["feed"]["title"] = "Книги в жанре: " + genre
    ret["feed"]["updated"] = dtiso
    if page == 0:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/genres/",
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    else:
        if page == 1:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/genres/" + gen_id,
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        else:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/genres/" + gen_id + "/" + str(page - 1),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/genres/" + gen_id,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )

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
        (genres = '%s'
            OR genres LIKE '%s|%%'
            OR genres LIKE '%%|%s'
            OR genres LIKE '%%|%s|%%'
        )
    ORDER BY zipfile, filename
    LIMIT "%s"
    OFFSET "%s"
    """ % (
        gen_id, gen_id, gen_id, gen_id,
        str(current_app.config['PAGE_SIZE']),
        str(page * current_app.config['PAGE_SIZE'])
    )
    rows = conn.execute(REQ).fetchall()
    rows_count = len(rows)
    if rows_count >= current_app.config['PAGE_SIZE']:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/genres/" + gen_id + "/" + str(page + 1),
                "@rel": "next",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    d1 = []  # tmp data without titles
    book_ids = []
    for row in rows:
        book_id = row["book_id"]
        d1.append(
            {
                "zipfile": row["zipfile"],
                "filename": row["filename"],
                "genres": row["genres"],
                "book_id": row["book_id"],
                "lang": row["lang"],
                "size": row["size"],
                "date_time": row["date_time"],
            }
        )
        book_ids.append(book_id)
    books_info = get_books_info(book_ids)
    book_titles = {}
    book_anno = {}
    for book in books_info:
        book_titles[book["book_id"]] = book["book_title"]
        book_anno[book["book_id"]] = book["annotation"]

    # prepare main data
    data = []
    for d in d1:
        d["book_title"] = book_titles[d["book_id"]]
        data.append(d)

    for d in sorted(data, key=lambda s: s['book_title']):
        book_id = d["book_id"]
        zipfile = d["zipfile"]
        filename = d["filename"]
        genres = d["genres"]
        lang = d["lang"]
        size = d["size"]
        date_time = d["date_time"]
        book_title = d["book_title"]
        annotation = book_anno[book_id]

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
