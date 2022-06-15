# -*- coding: utf-8 -*-

# import sqlite3
from .strings import get_genre_name, get_genre_meta, get_meta_name
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
            genre_meta = get_genre_meta(genre_id)
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                genre_data = [genre_id, genre_meta, genre]
                cur.execute("INSERT INTO genres VALUES (?, ?, ?)", (genre_data))
                REQ = 'SELECT count(*) from genres_meta WHERE meta_id = "%s"' % genre_meta
                cur.execute(REQ)
                rows = cur.fetchall()
                cnt = rows[0][0]
                if cnt == 0:
                    meta_name = get_meta_name(genre_meta)
                    meta_data = [genre_meta, meta_name]
                    cur.execute("INSERT INTO genres_meta VALUES (?, ?)", (meta_data))


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


def clean_authors(dbfile, DEBUG):
    import sqlite3
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    authors4del = []
    authors_names4del = []
    cur = con.cursor()
    REQ = 'SELECT id, name FROM authors ORDER BY name;'
    cur.execute(REQ)
    rows = cur.fetchall()
    if DEBUG:
        print("Authors total:", len(rows))  # debug
    for row in rows:
        id = row[0]
        name = row[1]
        REQ2 = '''SELECT count(book_id) as cnt
        FROM books
        WHERE
            author_ids = "%s" OR
            author_ids LIKE "%s|%%" OR
            author_ids LIKE "%%|%s" OR
            author_ids LIKE "%%|%s|%%";
        ''' % (id, id, id, id)
        cur.execute(REQ2)
        rows2 = cur.fetchall()
        for row2 in rows2:
            if DEBUG:
                print(name + " :" + str(row2[0]) + "                                     \r", end='')
            if row2[0] == 0:
                authors4del.append(id)
                authors_names4del.append(name)
                if DEBUG:
                    print("DEL:", name, "                     ")  # debug
    if len(authors4del) > 0:
        if DEBUG:
            print("delete authors:", ", ".join(authors_names4del))
        REQ = 'DELETE FROM authors WHERE id IN ("'
        auth_in = '","'.join(authors4del)
        REQ = REQ + auth_in + '");'
        cur.execute(REQ)
    con.commit()
    con.close()


def clean_sequences(dbfile, DEBUG):
    import sqlite3
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    seqs4del = []
    seq_names4del = []
    cur = con.cursor()
    REQ = 'SELECT id, name FROM sequences ORDER BY name;'
    cur.execute(REQ)
    rows = cur.fetchall()
    if DEBUG:
        print("Sequences total: %s               " % len(rows))  # debug
    for row in rows:
        id = row[0]
        name = row[1]
        REQ2 = '''SELECT count(book_id) as cnt
        FROM books
        WHERE
            seq_ids = "%s" OR
            seq_ids LIKE "%s|%%" OR
            seq_ids LIKE "%%|%s" OR
            seq_ids LIKE "%%|%s|%%";
        ''' % (id, id, id, id)
        cur.execute(REQ2)
        rows2 = cur.fetchall()
        for row2 in rows2:
            if DEBUG:
                print(name + " :" + str(row2[0]) + "                                     \r", end='')
            if row2[0] == 0:
                seqs4del.append(id)
                seq_names4del.append(name)
                if DEBUG:
                    print("DEL:", name, "                     ")  # debug
    if len(seqs4del) > 0:
        if DEBUG:
            print("delete sequences:", ", ".join(seq_names4del))
        REQ = 'DELETE FROM sequences WHERE id IN ("'
        auth_in = '","'.join(seqs4del)
        REQ = REQ + auth_in + '");'
        cur.execute(REQ)
    con.commit()
    con.close()


def clean_genres(dbfile, DEBUG):
    import sqlite3
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    genres4del = []
    cur = con.cursor()
    REQ = 'SELECT id FROM genres ORDER BY id;'
    cur.execute(REQ)
    rows = cur.fetchall()
    if DEBUG:
        print("Genres total: %s                    " % len(rows))  # debug
    for row in rows:
        id = row[0]
        REQ2 = '''SELECT count(book_id) as cnt
        FROM books
        WHERE
            genres = "%s" OR
            genres LIKE "%s|%%" OR
            genres LIKE "%%|%s" OR
            genres LIKE "%%|%s|%%";
        ''' % (id, id, id, id)
        cur.execute(REQ2)
        rows2 = cur.fetchall()
        for row2 in rows2:
            if DEBUG:
                print(id + " :" + str(row2[0]) + "                                     \r", end='')
            if row2[0] == 0:
                genres4del.append(id)
                if DEBUG:
                    print("DEL:", id, "                     ")  # debug
    if len(genres4del) > 0:
        if DEBUG:
            print("delete genres:", ", ".join(genres4del))
        REQ = 'DELETE FROM genres WHERE id IN ("'
        auth_in = '","'.join(genres4del)
        REQ = REQ + auth_in + '");'
        cur.execute(REQ)
    con.commit()
    con.close()


def vacuum_db(dbfile, DEBUG):
    REQ = 'VACUUM;'
    import sqlite3
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    cur = con.cursor()
    if DEBUG:
        print("VACUUM begin                 ")
    cur.execute(REQ)
    if DEBUG:
        print("VACUUM end")
    con.commit()
    con.close()
