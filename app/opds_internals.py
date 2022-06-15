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


# return [ { "name": seq_name, "id": seq_id, "count": books_count }, ...]
def get_auth_seqs(auth_id=None, zip_file=None):
    ret = []
    seq_cnt = {}
    if auth_id is not None and zip_file is None:
        REQ = """
        SELECT
            book_id,
            seq_ids as sequence_ids
        FROM books
        WHERE
            sequence_ids != '' AND
            length(sequence_ids) > 0 AND
            (
                author_ids = '%s' OR
                author_ids LIKE '%s|%%' OR
                author_ids LIKE '%%|%s' OR
                author_ids LIKE '%%|%s|%%'
            )
        """ % (auth_id, auth_id, auth_id, auth_id)
    elif auth_id is not None and zip_file is not None:
        REQ = """
        SELECT
            book_id,
            seq_ids as sequence_ids
        FROM books
        WHERE
            zipfile = %s AND
            sequence_ids != '' AND
            length(sequence_ids) > 0 AND
            (
                author_ids = '%s' OR
                author_ids LIKE '%s|%%' OR
                author_ids LIKE '%%|%s' OR
                author_ids LIKE '%%|%s|%%'
            )
        """ % (zip_file, auth_id, auth_id, auth_id, auth_id)
    elif auth_id is None and zip_file is not None:
        REQ = """
        SELECT
            book_id,
            seq_ids as sequence_ids
        FROM books
        WHERE
            zipfile = '%s' AND
            sequence_ids != '' AND
            length(sequence_ids) > 0
        """ % zip_file
    else:
        # return none
        REQ = """
        SELECT
            book_id,
            seq_ids as sequence_ids
        FROM books
        WHERE
            zipfile = '' AND
            sequence_ids != '' AND
            length(sequence_ids) < 0
        """ % zip_file
    conn = get_db_connection()
    print(REQ)
    rows = conn.execute(REQ).fetchall()
    if len(rows) != 0:
        for row in rows:
            # book_id = row["book_id"]
            seq_ids = row["sequence_ids"]
            for seq in seq_ids.split("|"):
                if seq is not None and seq != "":
                    if seq not in seq_cnt:
                        seq_cnt[seq] = 1
                    else:
                        seq_cnt[seq] = 1 + seq_cnt[seq]
        selector = []
        for k, v in seq_cnt.items():
            selector.append('"' + k + '"')
        REQ = 'SELECT id, name FROM sequences WHERE id IN (' + ",".join(selector) + ') ORDER BY U_UPPER(name);'
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seq_id = row["id"]
            seq_name = row["name"]
            if seq_id in seq_cnt:
                ret.append({"name": seq_name, "id": seq_id, "count": seq_cnt[seq_id]})
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
        '.': '%2E',
        '/': '%2F'
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
