# -*- coding: utf-8 -*-

# import sqlite3
from .strings import get_genre_name
from .data import make_id


# Custom collation, maybe it is more efficient
# to store strings
def unicode_nocase_collation(a: str, b: str):
    if a.casefold() == b.casefold():
        return 0
    if a.casefold() < b.casefold():
        return -1
    return 1


def author2db(cur, authors):
    global genres
    for author in authors.split("|"):
        if author is not None and author != "":
            author = author
            author_id = make_id(author)
            REQ = 'SELECT count(*) FROM authors WHERE id = "%s"' % author_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                author_data = [author_id, author, ""]
                cur.execute("INSERT INTO authors VALUES (?, ?, ?)", (author_data))


def seq2db(cur, seqs, zip_file, filename):
    for seq in seqs.split("|"):
        if seq is not None and seq != "":
            seq_id = make_id(seq)
            REQ = 'SELECT count(*) FROM sequences WHERE id = "%s"' % seq_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                seq_data = [seq_id, seq, ""]
                cur.execute("INSERT INTO sequences VALUES (?, ?, ?)", (seq_data))
            #REQ = 'SELECT count(*) FROM seq_books WHERE seq_id = "%s" AND ' % (seq_id, zip_file, filename)


def genres2db(cur, genrs):
    for genre_id in genrs.split("|"):
        if genre_id is not None and genre_id != "":
            genre = get_genre_name(genre_id)
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                genre_data = [genre_id, genre, ""]
                cur.execute("INSERT INTO genres VALUES (?, ?, ?)", (genre_data))
