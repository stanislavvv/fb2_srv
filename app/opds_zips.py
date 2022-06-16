# -*- coding: utf-8 -*-

from .opds_internals import get_db_connection, get_dtiso, get_authors, get_genres_names, get_seqs
from .opds_internals import get_auth_seqs, get_zips_sorted, sizeof_fmt
from flask import current_app


def ret_hdr_zip():  # python does not have constants
    return {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:zips",
            "updated": "0000-00-00_00:00",
            "title": "Books by zips",
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


def get_zips_list():
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_zip()
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/",
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    zips = get_zips_sorted()
    for zip_file in zips:
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:zips:" + zip_file,
                "title": zip_file,
                "content": {
                    "@type": "text",
                    "#text": "ZIP '" + zip_file + "'"
                },
                "link": {
                    "@href": approot + "/opds/zip/" + zip_file,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            }
        )
    return ret


def get_zip_list(zip_name):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_zip()
    ret["feed"]["id"] = "tag:zip:" + zip_name
    ret["feed"]["title"] = "Books in archive: " + zip_name + ""
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/zips",
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    ret["feed"]["entry"] = [
                {
                    "updated": dtiso,
                    "id": "tag:author:" + zip_name + ":sequences",
                    "title": "Books by sequences",
                    "link": {
                        "@href": approot + "/opds/zip/" + zip_name + "/sequences",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:author:" + zip_name + ":sequenceless",
                    "title": "Books outside of sequences",
                    "link": {
                        "@href": approot + "/opds/zip/" + zip_name + "/sequenceless",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                },
                {
                    "updated": dtiso,
                    "id": "tag:zip:" + zip_name + ":alphabet",
                    "title": "Books by alphabet",
                    "link": {
                        "@href": approot + "/opds/zip/" + zip_name + "/alphabet",
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            ]
    return ret


def get_zip_sequences(zip_name):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_zip()
    ret["feed"]["id"] = "tag:zip:" + zip_name + ":sequcenses"
    ret["feed"]["title"] = "Books in archive: " + zip_name + " by sequence"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/zip/" + zip_name,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )
    seqs = get_auth_seqs(None, zip_name)
    for seq in seqs:
        seq_name = seq["name"]
        seq_id = seq["id"]
        seq_cnt = seq["count"]
        ret["feed"]["entry"].append(
            {
                "updated": dtiso,
                "id": "tag:zip:" + zip_name + ":sequence:" + seq_id,
                "title": seq_name,
                "content": {
                    "@type": "text",
                    "#text": str(seq_cnt) + " book(s) in sequence"
                },
                "link": {
                    "@href": approot + "/opds/zipsequence/" + zip_name + "/" + seq_id,
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            },
        )
    return ret


def get_zip_sequence(zip_name, seq_id):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']

    REQ = 'SELECT id, name FROM sequences WHERE id = "%s"' % seq_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) == 0:
        return ""
    seq_name = rows[0][1]
    ret = ret_hdr_zip()
    ret["feed"]["id"] = "tag:zip:" + zip_name + ":sequence:" + seq_id
    ret["feed"]["title"] = "Books of zip: " + zip_name + " by sequence '" + seq_name + "'"
    ret["feed"]["updated"] = dtiso
    ret["feed"]["link"].append(
        {
            "@href": approot + "/opds/zip/" + zip_name,
            "@rel": "up",
            "@type": "application/atom+xml;profile=opds-catalog"
        }
    )

    REQ = """SELECT
        books.zipfile as zipfile,
        books.filename as filename,
        genres,
        author_ids,
        seq_ids as sequence_ids,
        books.book_id as book_id,
        books_descr.book_title as book_title,
        lang,
        size,
        date_time,
        books_descr.annotation as annotation,
        seq_books.seq_num as s_num
    FROM books, books_descr, seq_books
    WHERE
        books.zipfile = '%s' AND
        seq_books.zipfile = books.zipfile
        AND seq_books.filename = books.filename
        AND books_descr.book_id = books.book_id
        AND (sequence_ids = '%s'
            OR sequence_ids LIKE '%s|%%'
            OR sequence_ids LIKE '%%|%s'
            OR sequence_ids LIKE '%%|%s|%%'
        )
        AND seq_books.seq_id = '%s' ORDER BY s_num, book_title;
    """ % (zip_name, seq_id, seq_id, seq_id, seq_id, seq_id)
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
        seq_data = get_seqs(seq_ids)
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
            },
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
        Size: %s<br/>Sequence: %s, Number: %s<br/>
        """ % (annotation, sizeof_fmt(size), seq_name, str(seq_num))
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


def get_zip_sequenceless(zip_name, page):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_zip()
    ret["feed"]["id"] = "tag:zip:" + zip_name + ":sequenceless:"
    ret["feed"]["title"] = "Books in archive: " + zip_name + ' without sequence'
    ret["feed"]["updated"] = dtiso
    conn = get_db_connection()
    if page == 0:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    else:
        if page == 1:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/zip/" + zip_name + "/sequenceless",
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        else:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/zip/" + zip_name + "/sequenceless/" + str(page - 1),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        author_ids,
        books.book_id as book_id,
        book_title,
        lang,
        size,
        date_time,
        annotation
    FROM books, books_descr
    WHERE
        zipfile = '%s'
        AND seq_ids = ''
        AND books.book_id = books_descr.book_id
        ORDER BY book_title
    LIMIT "%s"
    OFFSET "%s";
    """ % (
        zip_name,
        str(current_app.config['PAGE_SIZE']),
        str(page * current_app.config['PAGE_SIZE'])
    )
    rows = conn.execute(REQ).fetchall()
    rows_count = len(rows)
    if rows_count >= current_app.config['PAGE_SIZE']:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name + "/sequenceless/" + str(page + 1),
                "@rel": "next",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
        size = row["size"]
        date_time = row["date_time"]
        annotation = row["annotation"]

        authors = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )

        links = [
                    {
                        "@href": approot + "/fb2/" + zipfile + "/" + filename,
                        "@rel": "http://opds-spec.org/acquisition/open-access",
                        "@title": "Download",
                        "@type": "application/fb2+zip"
                    },
                    {
                        "@href": approot + "/read/" + zipfile + "/" + filename,
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
                    "@term": k
                }
            )
        annotext = """
        <p class=\"book\"> %s </p>\n<br/>Format: fb2<br/>
        Size: %s<br/>Sequence: %s<br/>
        """ % (annotation, sizeof_fmt(size), "")
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
                }
            }
        )
    conn.close()
    return ret


def get_zip_by_alphabet(zip_name, page):
    dtiso = get_dtiso()
    approot = current_app.config['APPLICATION_ROOT']
    ret = ret_hdr_zip()
    ret["feed"]["id"] = "tag:zip:" + zip_name + ":books:alphabet:"
    ret["feed"]["title"] = "Books in archive: " + zip_name + " by aplhabet"
    ret["feed"]["updated"] = dtiso
    conn = get_db_connection()
    if page == 0:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    else:
        if page == 1:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/zip/" + zip_name + "/alphabet",
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        else:
            ret["feed"]["link"].append(
                {
                    "@href": approot + "/opds/zip/" + zip_name + "/alphabet/" + str(page - 1),
                    "@rel": "prev",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            )
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name,
                "@rel": "up",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )

    REQ = """
    SELECT
        zipfile,
        filename,
        genres,
        author_ids,
        seq_ids as sequence_ids,
        books.book_id as book_id,
        book_title,
        lang,
        size,
        date_time,
        annotation
    FROM books, books_descr
    WHERE
        zipfile = '%s' AND
        books.book_id = books_descr.book_id
        ORDER BY book_title
    LIMIT "%s"
    OFFSET "%s";
    """ % (
        zip_name,
        str(current_app.config['PAGE_SIZE']),
        str(page * current_app.config['PAGE_SIZE'])
    )
    rows = conn.execute(REQ).fetchall()
    rows_count = len(rows)
    if rows_count >= current_app.config['PAGE_SIZE']:
        ret["feed"]["link"].append(
            {
                "@href": approot + "/opds/zip/" + zip_name + "/alphabet/" + str(page + 1),
                "@rel": "next",
                "@type": "application/atom+xml;profile=opds-catalog"
            }
        )
    for row in rows:
        zipfile = row["zipfile"]
        filename = row["filename"]
        genres = row["genres"]
        author_ids = row["author_ids"]
        book_title = row["book_title"]
        book_id = row["book_id"]
        lang = row["lang"]
        size = row["size"]
        date_time = row["date_time"]
        seq_ids = row["sequence_ids"]
        annotation = row["annotation"]

        authors = []
        authors_data = get_authors(author_ids)
        for k, v in authors_data.items():
            authors.append(
                {
                    "uri": approot + "/opds/author/" + k,
                    "name": v
                }
            )
        seq_data = get_seqs(seq_ids)
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
        Size: %s<br/>Sequence: %s<br/>
        """ % (annotation, sizeof_fmt(size), "")
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
