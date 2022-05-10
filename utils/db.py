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
    if seqs is None:
        return
    for seq in seqs:
        if seq is not None and seq != "" and "id" in seq and "name" in seq:
            seq_id = seq["id"]
            seq_name = seq["name"]
            seq_num = 0
            if "num" in seq:
                seq_num = seq["num"]
            REQ = 'SELECT count(*) FROM sequences WHERE id = "%s"' % seq_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                seq_data = [seq_id, seq_name, ""]
                cur.execute("INSERT INTO sequences VALUES (?, ?, ?)", (seq_data))
            REQ = 'SELECT count(*) FROM seq_books WHERE '
            REQ = REQ + 'seq_id = "%s" AND zipfile = "%s" AND filename = "%s";' % (
                seq_id,
                zip_file,
                filename
            )
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                seq_data = [seq_id, zip_file, filename, seq_num]
                cur.execute("INSERT INTO seq_books VALUES (?, ?, ?, ?)", (seq_data))
        else:
            print("Bad seq info in: %s/%s, seq info:" % (zip_file, filename), str(seq))


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


def bookinfo2db(cur, book_id, book_title, annotation):
    b_title = ""
    if book_title is not None:
        b_title = str(book_title)
    descr = ""
    if annotation is not None:
        descr = str(annotation)
    if book_id is not None:
        book_data = [book_id, b_title, descr]
        cur.execute("SELECT * FROM books_descr WHERE book_id = '%s'" % book_id)
        rows = cur.fetchall()
        if len(rows) > 0:
            cur.execute("DELETE FROM books_descr WHERE book_id = '%s'" % book_id)
        cur.execute("INSERT INTO books_descr VALUES (?, ?, ?)", (book_data))
