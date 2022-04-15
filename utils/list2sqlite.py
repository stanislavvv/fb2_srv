#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys
import codecs
import hashlib


# table in database:
# author_ids = ",".join([md5(author1), md5(author2), ...])
# sequence_ids = ",",join([md5(seq1)], ...)
# book_id = md5("zipfile/filename")
"""
CREATE TABLE "books" (
	"zipfile"	TEXT NOT NULL,
	"filename"	TEXT NOT NULL,
	"genres"	TEXT,
	"authors"	TEXT COLLATE NOCASE,
	"author_ids"	NUMERIC,
	"sequence"	TEXT,
	"sequence_names"	TEXT COLLATE NOCASE,
	"sequence_ids"	TEXT,
	"book_title"	TEXT COLLATE NOCASE,
	"book_id"	TEXT,
	"lang"	TEXT,
	"date_time"	TEXT,
	"size"	INTEGER,
	"annotation"	TEXT COLLATE NOCASE,
	PRIMARY KEY("zipfile","filename","authors","book_title")
)
CREATE TABLE "authors" (
    "id"    TEXT UNIQUE,
    "name"  TEXT COLLATE NOCASE,
    "info"  TEXT,
    PRIMARY KEY("id")
);
CREATE TABLE "sequences" (
    "id"    TEXT UNIQUE,
    "name"  TEXT COLLATE NOCASE,
    "info"  TEXT,
    PRIMARY KEY("id")
);
CREATE TABLE "genres" (
    "id"    TEXT UNIQUE,
    "description"   TEXT COLLATE NOCASE,
    PRIMARY KEY("id")
);
"""
# global vars

# path to sqlite db file
DB = "fb_data.sqlite"

# genres (see get_genres())
genres = {}

# fix some wrong genres
genres_replacements = {}

# /global vars


# quote string for sql
def quote_identifier(s, errors="strict"):
    encodable = s.encode("utf-8", errors).decode("utf-8")

    nul_index = encodable.find("\x00")

    if nul_index >= 0:
        error = UnicodeEncodeError("NUL-terminated utf-8", encodable,
                                   nul_index, nul_index + 1, "NUL not allowed")
        error_handler = codecs.lookup_error(errors)
        replacement, _ = error_handler(error)
        encodable = encodable.replace("\x00", replacement)

    return "\"" + encodable.replace("\"", "\"\"") + "\""


# remove trailing suffix
def rchop(s, suffix):
    if suffix and s.endswith(suffix):
        return s[:-len(suffix)]
    return s


# init genres dict
def get_genres():
    data = open('genres.list', 'r')
    while True:
        line = data.readline()
        if not line:
            break
        f = line.strip('\n').split('|')
        if len(f) > 1:
            genres[f[0]] = f[1]
    data.close()


# init genres_replace dict
def get_genres_replace():
    data = open('genres_replace.list', 'r')
    while True:
        line = data.readline()
        if not line:
            break
        f = line.strip('\n').split('|')
        if len(f) > 1:
            genres_replacements[f[0]] = f[1]
    data.close()


# print unknown genres
def check_genres(g):
    gg = g[2].split(',')
    for i in gg:
        if i not in genres and i != "":
            print(g[0] + "|" + g[1] + "|" + i)


# DEBUG:
def listdiff(l1, l2):
    max = len(l1)
    if max < len(l2):
        max = len(l2)
    print(max, len(l1), len(l2))
    for i in range(0, max):
        s1 = "%02d<<<<|" % i
        if i < len(l1):
            s1 = s1 + l1[i]
        s2 = "%02d>>>>|" % i
        if i < len(l2):
            s2 = s2 + l2[i]
        print(s1)
        print(s2)


def genres_replace(genrs):
    gg = genrs.split(",")
    ret = []
    for i in gg:
        if i not in genres and i != "":
            if i in genres_replacements:
                if genres_replacements[i] is not None and genres_replacements[i] != "":
                    ret.append(genres_replacements[i])
            else:
                ret.append('other')
        else:
            ret.append(i)
    return ",".join(ret)


def author2db(cur, authors):
    for author in authors.split(","):
        if author is not None and author != "":
            author_id = hashlib.md5(author.encode('utf-8')).hexdigest()
            REQ = 'SELECT count(*) FROM authors WHERE id = "%s"' % author_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                author_data = [author_id, author, ""]
                cur.execute("INSERT INTO authors VALUES (?, ?, ?)", (author_data))


def seq2db(cur, seqs):
    for seq in seqs.split(","):
        if seq is not None and seq != "":
            seq_id = hashlib.md5(seq.encode('utf-8')).hexdigest()
            REQ = 'SELECT count(*) FROM sequences WHERE id = "%s"' % seq_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                seq_data = [seq_id, seq, ""]
                cur.execute("INSERT INTO sequences VALUES (?, ?, ?)", (seq_data))


def genres2db(cur, genrs):
    for genre_id in genrs.split(","):
        if genre_id is not None and genre_id != "":
            genre = genres[genre_id]
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                genre_data = [genre_id, genre]
                cur.execute("INSERT INTO genres VALUES (?, ?)", (genre_data))


# main function
def iterate_list(blist):
    data = open(blist, 'r')
    zipfile = os.path.basename(rchop(blist, '.list'))
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE zipfile = ?", [zipfile])
    # con.commit()
    while True:
        insdata = []
        line = data.readline()
        # if line is empty
        # end of file is reached
        if not line:
            break
        insdatat = line.strip('\n').split('|')
        insdata = insdatat[:14]
        insdata[2] = genres_replace(insdata[2])
        check_genres(insdata[:3])
        genres2db(cur, insdata[2])
        author2db(cur, insdata[3])
        seq2db(cur, insdata[6])
        if len(insdata) != len(insdatat):  # something strange in description
            print(">>>", insdatat)
            print("<<<", insdata)
            insdata[13] = "".join(insdatat[13:])
            insdata[12] = int(insdata[12])
        # print(insdata)  # debug
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (insdata))
    con.commit()
    con.close()
    data.close()


if __name__ == '__main__':
    booklist = sys.argv[1]
    get_genres()
    get_genres_replace()
    iterate_list(booklist)
