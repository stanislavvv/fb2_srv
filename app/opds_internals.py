# -*- coding: utf-8 -*-

import datetime
import sqlite3
from flask import current_app


# max books on page
BOOKS_LIMIT = 100


# return [ { "name": seq_name, "id": seq_id, "count": books_count }, ...]
def get_auth_seqs(auth_id):
    ret = []
    seq_cnt = {}
    REQ1 = "SELECT book_id, sequence_ids FROM books WHERE length(sequence_ids) > 0 AND author_ids = '"
    REQ2 = "' OR author_ids LIKE '"
    REQ3 = ",%' OR author_ids LIKE '%,"
    REQ4 = "' OR author_ids LIKE '%,"
    REQ5 = ",%' AND sequence_ids != '';"
    REQ = REQ1 + auth_id + REQ2 + auth_id + REQ3 + auth_id + REQ4 + auth_id + REQ5
    conn = get_db_connection()
    rows = conn.execute(REQ).fetchall()
    if len(rows) != 0:
        for row in rows:
            # book_id = row["book_id"]
            seq_ids = row["sequence_ids"]
            for seq in seq_ids.split(","):
                if seq is not None and seq != "":
                    if seq not in seq_cnt:
                        seq_cnt[seq] = 1
                    else:
                        seq_cnt[seq] = 1 + seq_cnt[seq]
        selector = []
        for k, v in seq_cnt.items():
            selector.append('"' + k + '"')
        REQ = 'SELECT id, name FROM sequences WHERE id IN (' + ",".join(selector) + ') ORDER BY name;'
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            seq_id = row["id"]
            seq_name = row["name"]
            if seq_id in seq_cnt:
                ret.append({"name": seq_name, "id": seq_id, "count": seq_cnt[seq_id]})
    conn.close()
    return ret


def get_db_connection():
    conn = sqlite3.connect(current_app.config['DBSQLITE'])
    conn.row_factory = sqlite3.Row
    return conn


def get_dtiso():
    return datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()


def any2alphabet(field, sq3_rows, num):
    alphabet = {}
    for i in sq3_rows:
        s = i[field]
        alphabet[s[:num]] = 1
    return sorted(list(alphabet))


def get_authors(ids):
    ret = {}
    selector = []
    for i in ids.split(","):
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
    for i in genres_ids.split(","):
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
    print(ids)
    for i in ids.split(","):
        selector.append("'" + i + "'")
    REQ = "SELECT id, name FROM sequences WHERE id IN (" + ",".join(selector) + ");"
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
