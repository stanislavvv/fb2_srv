#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
import sys
import codecs


# table in database:
"""
CREATE TABLE "books" (
	"zipfile"	TEXT NOT NULL,
	"filename"	TEXT NOT NULL,
	"genres"	TEXT,
	"authors"	TEXT,
	"sequence"	TEXT,
	"book_title"	TEXT,
	"lang"	TEXT,
	"annotation"	INTEGER,
	PRIMARY KEY("zipfile","filename","authors","book_title")
);
CREATE INDEX "search" ON "books" (
	"genres",
	"authors",
	"sequence",
	"book_title",
	"annotation"
);
"""
DB = "../fb_data.sqlite"


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


# main function
def iterate_list(blist):
    data = open(blist, 'r')
    zipfile = os.path.basename(rchop(blist, '.list'))
    con = sqlite3.connect(DB)
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE zipfile = ?", [zipfile])
    #con.commit()
    while True:
        insdata = []
        line = data.readline()
        # if line is empty
        # end of file is reached
        if not line:
            break
        insdatat = line.strip('\n').split('|')
        insdata = insdatat[:9]
        if len(insdata) != len(insdatat):  # something strange in description
            insdata[8] = "".join(insdatat[8:])
        # print(insdata)  # debug
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (insdata))
    con.commit()
    con.close()
    data.close()


if __name__ == '__main__':
    booklist = sys.argv[1]
    iterate_list(booklist)
