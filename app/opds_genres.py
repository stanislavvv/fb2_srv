# -*- coding: utf-8 -*-

from flask import current_app
from .opds_internals import get_db_connection, get_dtiso, sizeof_fmt
from .opds_internals import get_book_authors, get_genres_names, get_book_seqs


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
            SELECT id, description
            FROM genres
            WHERE meta_id = "%s"
            ORDER BY description;
        ''' % meta_id
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
    ret["feed"]["title"] = "Books in genre: " + genre + " by aplhabet"
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
        book_title,
        lang,
        size,
        date_time,
        annotation
    FROM books, books_descr
    WHERE
        books.book_id = books_descr.book_id
        AND (genres = '%s'
            OR genres LIKE '%s|%%'
            OR genres LIKE '%%|%s'
            OR genres LIKE '%%|%s|%%'
        )
        ORDER BY book_title
        LIMIT "%s"
        OFFSET "%s";
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
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
        size = row["size"]
        date_time = row["date_time"]
        annotation = row["annotation"]

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
            links.append(
                {
                    "@href": approot + "/opds/sequencebooks/" + k,
                    "@rel": "related",
                    "@title": "All books in sequence '" + v + "'",
                    "@type": "application/atom+xml"
                }
            )

        links.append(
            {
                "@href": approot + "/fb2/" + zipfile + "/" + filename,
                "@rel": "http://opds-spec.org/acquisition/open-access",
                "@title": "Download",
                "@type": "application/fb2+zip"
            }
        )
        links.append(
            {
                "@href": approot + "/read/" + zipfile + "/" + filename,
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
