# -*- coding: utf-8 -*-

import datetime
import sqlite3
import urllib.parse
import unicodedata as ud
import re

from flask import current_app

alphabet_1 = [  # first letters in main authors/sequences page
    'А', 'Б', 'В', 'Г', 'Д', 'Е', 'Ё', 'Ж', 'З', 'И', 'Й',
    'К', 'Л', 'М', 'Н', 'О', 'П', 'Р', 'С', 'Т', 'У', 'Ф',
    'Х', 'Ц', 'Ч', 'Ш', 'Щ', 'Ъ', 'Ы', 'Ь', 'Э', 'Ю', 'Я'
]

alphabet_2 = [  # second letters in main authors/sequences page
    'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J',
    'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T',
    'U', 'V', 'W', 'X', 'Y', 'Z'
]

# sort zips right
file_pattern = re.compile(r'.*-(\d+)-.*?')


def get_order(file):
    match = file_pattern.match(file)
    if not match:
        return 10000000000000000000
    return int(match.groups()[0])
# /sort zips


# Custom collation, maybe it is more efficient
# to store strings
def unicode_nocase_collation(a: str, b: str):
    if ud.normalize('NFKD', a).casefold() == ud.normalize('NFKD', b).casefold():
        return 0
    if ud.normalize('NFKD', a).casefold() < ud.normalize('NFKD', b).casefold():
        return -1
    return 1


# custom UPPER + normalize for sqlite
def unicode_upper(s: str):
    ret = ud.normalize('NFKD', s)
    ret = ret.upper()
    ret = ret.replace('Ё', 'Е')
    ret = ret.replace('Й', 'И')
    ret = ret.replace('Ъ', 'Ь')
    return ret


def get_db_connection():
    conn = sqlite3.connect(current_app.config['DBSQLITE'])
    conn.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    conn.create_function("U_UPPER", 1, unicode_upper)
    conn.row_factory = sqlite3.Row
    return conn


def get_dtiso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def get_seq_names(seq_ids):
    ret = {}
    REQ = """
    SELECT id, name FROM sequences
    WHERE id in ('%s')
    """ % "','".join(seq_ids)
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        ret[row[0]] = row[1]
    return ret


# return [ { "name": seq_name, "id": seq_id, "count": books_count }, ...]
def get_auth_seqs(auth_id=None, zip_file=None):
    ret = []
    if auth_id is not None and zip_file is None:
        # get book ids for author
        REQ_BOOKS = """
            SELECT book_id, author_id
            FROM books_authors
            WHERE author_id = '%s'
        """ % auth_id
        book_ids = []
        conn = get_db_connection()
        rows = conn.execute(REQ_BOOKS).fetchall()
        for row in rows:
            book_ids.append(row[0])

        # get seq_ids
        REQ_SEQS = """
            SELECT seq_id, book_id FROM seq_books
            WHERE book_id IN ('%s')
        """ % "','".join(book_ids)
        rows = conn.execute(REQ_SEQS).fetchall()
        seq_nums = {}
        for row in rows:  # count books (ToDo: compare time with SELECT count(*))
            seq_id = row[0]
            if seq_id in seq_nums:
                seq_nums[seq_id] = 1 + seq_nums[seq_id]
            else:
                seq_nums[seq_id] = 1
        seq_names = get_seq_names(seq_nums.keys())
        for seq_id in seq_nums.keys():
            ret.append(
                {
                    "name": seq_names[seq_id],
                    "id": seq_id,
                    "count": seq_nums[seq_id]
                }
            )
        conn.close()
    elif auth_id is not None and zip_file is not None:
        # get books of author
        REQ_BOOKS = """
            SELECT book_id, author_id
            FROM books_authors
            WHERE author_id = '%s'
        """ % auth_id
        book_ids = []
        conn = get_db_connection()
        rows = conn.execute(REQ_BOOKS).fetchall()
        for row in rows:
            book_ids.append(row[0])

        # filter books by zipfile
        REQ_BOOKS2 = """
            SELECT book_id FROM books
            WHERE
                zipfile = '%s' AND
                book_id IN ('%s')
        """ % (zip_file, "','".join(book_ids))
        book_ids = []
        rows = conn.execute(REQ_BOOKS2).fetchall()
        for row in rows:
            book_ids.append(row[0])

        # get seq_ids
        REQ_SEQS = """
            SELECT seq_id, book_id FROM seq_books
            WHERE book_id IN ('%s')
        """ % "','".join(book_ids)
        rows = conn.execute(REQ_SEQS).fetchall()
        seq_nums = {}
        for row in rows:  # count books (ToDo: compare time with SELECT count(*))
            seq_id = row[0]
            if seq_id in seq_nums:
                seq_nums[seq_id] = 1 + seq_nums[seq_id]
            else:
                seq_nums[seq_id] = 1
        seq_names = get_seq_names(seq_nums.keys())
        for seq_id in seq_nums.keys():
            ret.append(
                {
                    "name": seq_names[seq_id],
                    "id": seq_id,
                    "count": seq_nums[seq_id]
                }
            )
        conn.close()
    elif auth_id is None and zip_file is not None:
        conn = get_db_connection()
        # filter books by zipfile
        REQ_BOOKS = """
            SELECT book_id FROM books
            WHERE
                zipfile = '%s'
        """ % zip_file
        book_ids = []
        rows = conn.execute(REQ_BOOKS).fetchall()
        for row in rows:
            book_ids.append(row[0])

        # get seq_ids
        REQ_SEQS = """
            SELECT seq_id, book_id FROM seq_books
            WHERE book_id IN ('%s')
        """ % "','".join(book_ids)
        rows = conn.execute(REQ_SEQS).fetchall()
        seq_nums = {}
        for row in rows:  # count books (ToDo: compare time with SELECT count(*))
            seq_id = row[0]
            if seq_id in seq_nums:
                seq_nums[seq_id] = 1 + seq_nums[seq_id]
            else:
                seq_nums[seq_id] = 1
        seq_names = get_seq_names(seq_nums.keys())
        for seq_id in seq_nums.keys():
            ret.append(
                {
                    "name": seq_names[seq_id],
                    "id": seq_id,
                    "count": seq_nums[seq_id]
                }
            )
        conn.close()
    else:
        # return none, as none zipfile
        REQ = """
            SELECT count(*) as cnt, seq_books.seq_id as seq_id, sequences.name as name
            FROM books, books_authors, seq_books, sequences
            WHERE
            books.zipfile = '' AND
            books.book_id = books_authors.book_id AND
            books.book_id = seq_books.book_id AND
            seq_books.seq_id = sequences.id
            GROUP BY seq_id
        """
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        if len(rows) != 0:
            for row in rows:
                name = row["name"]
                seq_id = row["seq_id"]
                count = row["cnt"]
                ret.append({"name": name, "id": seq_id, "count": count})
        conn.close()
    return ret


def get_zips_sorted():
    ret = []
    REQ = """
    SELECT zipfile
    FROM books
    GROUP BY zipfile
    """
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) != 0:
        for row in rows:
            ret.append(row["zipfile"])
    return sorted(ret, key=get_order, reverse=True)


def custom_alphabet_sort(slist):
    ret = []
    for s in sorted(slist):
        if len(s) > 0 and s[0] in alphabet_1:
            ret.append(s)
    for s in sorted(slist):
        if len(s) > 0 and s[0] in alphabet_2:
            ret.append(s)
    for s in sorted(slist):
        if len(s) > 0 and s[0] not in alphabet_1 and s[0] not in alphabet_2:
            ret.append(s)
    return ret


def any2alphabet(field, sq3_rows, num):
    alphabet = {}
    for i in sq3_rows:
        s = i[field]
        alphabet[s[:num]] = 1
    return custom_alphabet_sort(list(alphabet))


def get_authors(ids):
    ret = {}
    selector = []
    for i in ids.split("|"):
        selector.append("'" + i + "'")
    REQ = "SELECT id, name FROM authors WHERE id IN (" + ",".join(selector) + ");"
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (author_id, name) = (row[0], row[1])
        ret[author_id] = name
    conn.close()
    return ret


def get_book_authors(book_id):
    ret = {}
    REQ = """
    SELECT authors.id as id, authors.name as name
    FROM authors, books_authors
    WHERE
        books_authors.book_id = '%s'
        AND authors.id = books_authors.author_id
    ORDER BY name
    """ % book_id
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
    for i in genres_ids.split("|"):
        selector.append("'" + i + "'")
    REQ = "SELECT id, description FROM genres WHERE id IN (" + ",".join(selector) + ");"
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (genre_id, description) = (row[0], row[1])
        ret[genre_id] = description
    conn.close()
    return ret


def get_seqs(ids):
    ret = {}
    selector = []
    for i in ids.split("|"):
        selector.append("'" + i + "'")
    REQ = "SELECT id, name FROM sequences WHERE id IN (" + ",".join(selector) + ") ORDER BY U_UPPER(name);"
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (seq_id, name) = (row[0], row[1])
        ret[seq_id] = name
    conn.close()
    return ret


def get_book_seqs(book_id):
    ret = {}
    REQ = """
    SELECT sequences.id as id, sequences.name as name
    FROM seq_books, sequences
    WHERE
        seq_books.seq_id = sequences.id AND
        seq_books.book_id = '%s'
    """ % book_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (seq_id, name) = (row[0], row[1])
        ret[seq_id] = name
    conn.close()
    return ret


def get_seq_books(seq_id):
    ret = []
    REQ = """
    SELECT book_id, seq_num FROM seq_books
    WHERE seq_id = '%s'
    ORDER BY seq_num
    """ % seq_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (book_id, seq_num) = (row[0], row[1])
        ret.append({"book_id": book_id, "seq_num": seq_num})
    return ret


def get_author_books(auth_id):
    ret = []
    REQ = """
    SELECT book_id, author_id FROM books_authors
    WHERE author_id = '%s'
    """ % auth_id
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        book_id = row[0]
        ret.append(book_id)
    return ret


def get_books_info(book_ids):
    ret = []
    selector = []
    for book_id in book_ids:
        selector.append("\"%s\"" % book_id)
    REQ = """
    SELECT book_id, book_title, annotation
    FROM books_descr
    WHERE book_id IN (%s)
    """ % ",".join(selector)
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    for row in rows:
        (book_id, book_title, annotation) = (row[0], row[1], row[2])
        ret.append(
            {
                "book_id": book_id,
                "book_title": book_title,
                "annotation": annotation
            }
        )
    return ret


# 123456 -> 123k, 1234567 -> 1.23M
def sizeof_fmt(num, suffix="B"):
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return f"{num:3.1f}{unit}{suffix}"
        num /= 1024.0
    return f"{num:.1f}Yi{suffix}"


# urlencode string (quote + replace some characters to %NN)
def url_str(s):
    tr = {
        '"': '%22',
        "'": '%27',
        #'.': '%2E',
        #'/': '%2F'
    }
    ret = ''
    if s is not None:
        for c in s:
            if c in tr:
                c = tr[c]
            ret = ret + c
    return urllib.parse.quote(ret, encoding='utf-8')


def unurl(s):
    tr = {
        '%22': '"',
        '%27': "'",
        '%2E': ".",
        '%2F': '/'
    }
    ret = s
    if ret is not None:
        for r, v in tr.items():
            ret = ret.replace(r, v)
    return ret


def param_to_search(field: str, s: str):
    ret = []
    words = s.split(' ')
    for w in words:
        if w is not None and w != "":
            ret.append('"%%%s%%"' % w)
    f = " AND %s LIKE " % field
    return f.join(ret)


def get_seq_link(approot, seq_id, seq_name):
    ret = {
        "@href": approot + "/opds/sequencebooks/" + seq_id,
        "@rel": "related",
        "@title": "Серия '" + seq_name + "'",
        "@type": "application/atom+xml"
    }
    return ret


# ctype == 'dl' for download
def get_book_link(approot, zipfile, filename, ctype):
    title = "Читать онлайн"
    book_ctype = "text/html"
    rel = "alternate"
    href = approot + "/read/" + zipfile + "/" + url_str(filename)
    if ctype == 'dl':
        title = "Скачать"
        book_ctype = "application/fb2+zip"
        rel = "http://opds-spec.org/acquisition/open-access"
        href = approot + "/fb2/" + zipfile + "/" + url_str(filename)
    ret = {
        "@href": href,
        "@rel": rel,
        "@title": title,
        "@type": book_ctype
    }
    return ret


def get_book_entry(date_time, book_id, book_title, authors, links, category, lang, annotext):
    ret = {
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
    return ret
