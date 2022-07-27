# -*- coding: utf-8 -*-

import logging
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


# def author2db(cur, authors):
    # for author in authors.split("|"):
        # if author is not None and author != "":
            # author_id = make_id(author)
            # REQ = 'SELECT count(*) FROM authors WHERE id = "%s"' % author_id
            # cur.execute(REQ)
            # rows = cur.fetchall()
            # cnt = rows[0][0]
            # if cnt == 0:
                # author_data = [author_id, author, ""]
                # cur.execute("INSERT INTO authors VALUES (?, ?, ?)", (author_data))


def author4db(cur, authors):
    ret = []
    for author in authors.split("|"):
        if author is not None and author != "":
            author_id = make_id(author)
            REQ = 'SELECT count(*) FROM authors WHERE id = "%s"' % author_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                ret.append((author_id, author, ""))
    return ret


# def auth_ref2db(cur, authors, book_id):
    # if book_id is not None and book_id != "":
        # for author in authors.split("|"):
            # if author is not None and author != "":
                # author_id = make_id(author)
                # REQ = '''
                # SELECT count(*)
                # FROM books_authors
                # WHERE
                    # author_id = "%s" AND
                    # book_id = "%s"
                # ''' % (author_id, book_id)
                # cur.execute(REQ)
                # rows = cur.fetchall()
                # cnt = rows[0][0]
                # if cnt == 0:
                    # ref_data = [book_id, author_id]
                    # cur.execute("INSERT INTO books_authors(book_id, author_id) VALUES (?, ?)", (ref_data))


def auth_ref4db(cur, authors, book_id):
    ret = []
    if book_id is not None and book_id != "":
        for author in authors.split("|"):
            if author is not None and author != "":
                author_id = make_id(author)
                REQ = '''
                SELECT count(*)
                FROM books_authors
                WHERE
                    author_id = "%s" AND
                    book_id = "%s"
                ''' % (author_id, book_id)
                cur.execute(REQ)
                rows = cur.fetchall()
                cnt = rows[0][0]
                if cnt == 0:
                    ret.append((book_id, author_id))
    return ret

# def seq2db(cur, seqs, book_id, zip_file, filename):
    # if seqs is None:
        # return
    # for seq in seqs:
        # if seq is not None and seq != "" and "id" in seq and "name" in seq:
            # seq_id = seq["id"]
            # seq_name = seq["name"]
            # seq_num = None
            # if "num" in seq:
                # seq_num = seq["num"]
            # REQ = 'SELECT count(*) FROM sequences WHERE id = "%s"' % seq_id
            # cur.execute(REQ)
            # rows = cur.fetchall()
            # cnt = rows[0][0]
            # if cnt == 0:
                # seq_data = [seq_id, seq_name, ""]
                # cur.execute("INSERT INTO sequences VALUES (?, ?, ?)", (seq_data))
            # REQ = 'SELECT count(*) FROM seq_books WHERE '
            # REQ = REQ + 'seq_id = "%s" AND book_id = "%s";' % (
                # seq_id,
                # book_id
            # )
            # cur.execute(REQ)
            # rows = cur.fetchall()
            # cnt = rows[0][0]
            # if cnt == 0:
                # seq_data = [seq_id, book_id, seq_num]
                # cur.execute("INSERT INTO seq_books VALUES (?, ?, ?)", (seq_data))
        # else:
            # logging.error("Bad seq info in: %s/%s, seq info: %s" % (zip_file, filename, str(seq)))


def seqs4db(cur, seqs, book_id, zip_file, filename):
    ret = []
    if seqs is None:
        return ret
    for seq in seqs:
        if seq is not None and seq != "" and "id" in seq and "name" in seq:
            seq_id = seq["id"]
            seq_name = seq["name"]
            REQ = 'SELECT count(*) FROM sequences WHERE id = "%s"' % seq_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                ret.append((seq_id, seq_name, ""))
        else:
            logging.error("Bad seq info in: %s/%s, seq info: %s" % (zip_file, filename, str(seq)))
    return ret


def seq_ref4db(cur, seqs, book_id, zip_file, filename):
    ret = []
    if seqs is None:
        return ret
    for seq in seqs:
        if seq is not None and seq != "" and "id" in seq and "name" in seq:
            seq_id = seq["id"]
            seq_name = seq["name"]
            seq_num = None
            if "num" in seq:
                seq_num = seq["num"]
            REQ = 'SELECT count(*) FROM seq_books WHERE '
            REQ = REQ + 'seq_id = "%s" AND book_id = "%s";' % (
                seq_id,
                book_id
            )
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                ret.append((seq_id, book_id, seq_num))
        else:
            logging.error("Bad seq info in: %s/%s, seq info: %s" % (zip_file, filename, str(seq)))
    return ret


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


def genres4db(cur, genrs):
    ret = []
    for genre_id in genrs.split("|"):
        if genre_id is not None and genre_id != "":
            genre = get_genre_name(genre_id)
            genre_meta = get_genre_meta(genre_id)
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                ret.append((genre_id, genre_meta, genre))
    return ret


def genres_meta4db(cur, genrs):
    ret = []
    for genre_id in genrs.split("|"):
        if genre_id is not None and genre_id != "":
            genre = get_genre_name(genre_id)
            genre_meta = get_genre_meta(genre_id)
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                REQ = 'SELECT count(*) from genres_meta WHERE meta_id = "%s"' % genre_meta
                cur.execute(REQ)
                rows = cur.fetchall()
                cnt = rows[0][0]
                if cnt == 0:
                    meta_name = get_meta_name(genre_meta)
                    ret.append((genre_meta, meta_name))
    return ret

# def bookinfo2db(cur, book_id, book_title, annotation):
    # b_title = ""
    # if book_title is not None:
        # b_title = str(book_title)
    # descr = ""
    # if annotation is not None:
        # descr = str(annotation)
    # if book_id is not None:
        # book_data = [book_id, b_title, descr]
        # cur.execute("SELECT * FROM books_descr WHERE book_id = '%s'" % book_id)
        # rows = cur.fetchall()
        # if len(rows) > 0:
            # cur.execute("DELETE FROM books_descr WHERE book_id = '%s'" % book_id)
        # cur.execute("INSERT INTO books_descr VALUES (?, ?, ?)", (book_data))


def bookinfo4db(cur, book_id, book_title, annotation):
    ret = []
    b_title = ""
    if book_title is not None:
        b_title = str(book_title)
    descr = ""
    if annotation is not None:
        descr = str(annotation)
    if book_id is not None:
        ret.append((book_id, b_title, descr))
    return ret

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
    logging.info("Authors total: %s" % len(rows))
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
            if row2[0] == 0:
                authors4del.append(id)
                authors_names4del.append(name)
                logging.debug("DEL: %s" % name)
    if len(authors4del) > 0:
        logging.info("delete authors: " + ", ".join(authors_names4del))
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
    logging.info("Sequences total: %s               " % len(rows))
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
            if row2[0] == 0:
                seqs4del.append(id)
                seq_names4del.append(name)
                logging.debug("DEL: %s" % name)
    if len(seqs4del) > 0:
        logging.info("delete sequences:", ", ".join(seq_names4del))
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
    logging.info("Genres total: %s                    " % len(rows))
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
            if row2[0] == 0:
                genres4del.append(id)
                logging.debug("DEL:", id, "                     ")  # debug
    if len(genres4del) > 0:
        logging.info("delete genres:", ", ".join(genres4del))
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
    logging.info("VACUUM begin                 ")
    cur.execute(REQ)
    logging.info("VACUUM end")
    con.commit()
    con.close()
