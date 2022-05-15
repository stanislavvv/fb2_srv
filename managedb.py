#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import sqlite3
import json

from app import create_app
from utils import ziplist, booklist2db
from utils.db import unicode_nocase_collation, clean_authors

DEBUG = True


CREATE_REQ = [
    """
    CREATE TABLE 'books' (
        'zipfile'	TEXT NOT NULL,
        'filename'	TEXT NOT NULL,
        'genres'	TEXT,
        'authors'	TEXT,
        'author_ids'	NUMERIC,
        'seq_names'	TEXT,
        'seq_ids'	TEXT,
        'book_id'	TEXT,
        'lang'	TEXT,
        'date_time'	TEXT,
        'size'	INTEGER,
        PRIMARY KEY('zipfile','filename','author_ids','seq_ids')
    );
    """,
    """
    CREATE TABLE `books_descr` (
        'book_id'    TEXT NOT NULL,
        'book_title' TEXT,
        'annotation' TEXT,
        PRIMARY KEY('book_id')
    )
    """,
    """
    CREATE TABLE 'authors' (
        'id'    TEXT UNIQUE,
        'name'  TEXT,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'sequences' (
        'id'    TEXT UNIQUE,
        'name'  TEXT,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'genres' (
        'id'	TEXT UNIQUE,
        'description'	TEXT,
        'group'	TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'seq_books' (
        'seq_id'	TEXT NOT NULL,
        'zipfile'	TEXT NOT NULL,
        'filename'	TEXT NOT NULL,
        'seq_num'	INTEGER,
        PRIMARY KEY('seq_id', 'zipfile', 'filename')
    );
    """
]


def usage():
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" dropdb      -- remove database from disk")
    print(" newdb       -- [re]create database from scratch")
    print(" fsck        -- remove orphan authors")
    print(" fillnew     -- add new data to database")
    print(" refillall   -- pass over all zips, del from db, recreate file lists and fill them to db")
    print(" fill_lists  -- as refillall, but does not recreate lists, only refill data to db")
    print(" renew_lists -- as refillall, but recreate lists, no refill any data to db")
    print(" new_lists   -- as fillnew, but update lists, no refill any data to db")


def dropdb():
    dbfile = app.config['DBSQLITE']
    print("removing", dbfile)
    os.remove(dbfile)


def newdb():
    dbfile = app.config['DBSQLITE']
    if os.path.exists(dbfile):
        dropdb()
    print("creating", dbfile)
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    cur = con.cursor()
    for req in CREATE_REQ:
        cur.execute(req)
    con.commit()
    con.close()


def create_booklist(zip_file):
    booklist = zip_file + ".list"
    list = ziplist(zip_file)
    bl = open(booklist, 'w')
    bl.write(json.dumps(list, ensure_ascii=False))
    bl.close()


def update_booklist(zip_file):
    booklist = zip_file + ".list"
    replacelist = zip_file + ".replace"
    if os.path.exists(booklist):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklist)
        replacetime = 0
        if os.path.exists(replacelist):
            replacetime = os.path.getmtime(replacelist)
        if ziptime < listtime and replacetime < listtime:
            return False
    create_booklist(zip_file)


def fillall():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        print("[" + str(i) + "] ", end='')
        create_booklist(zip_file)
        booklist = zip_file + ".list"
        if os.path.exists(booklist):
            booklist2db(booklist, dbfile)


def fillnew():
    zipdir = app.config['ZIPS']
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        print("[" + str(i) + "] ", end='')
        update_booklist(zip_file)
        if os.path.exists(booklist):
            booklist2db(booklist, dbfile)


def fill_lists():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    i = 0
    for booklist in glob.glob(zipdir + '/*.zip.list'):
        i += 1
        print("[" + str(i) + "] ", end='')
        booklist2db(booklist, dbfile)


def renew_lists():
    zipdir = app.config['ZIPS']
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        print("[" + str(i) + "] ", end='')
        create_booklist(zip_file)


def new_lists():
    zipdir = app.config['ZIPS']
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        print("[" + str(i) + "] ", end='')
        update_booklist(zip_file)


def db_fsck():
    dbfile = app.config['DBSQLITE']
    clean_authors(dbfile)


if __name__ == "__main__":
    app = create_app()
    DEBUG = app.config['DEBUG']
    if len(sys.argv) > 1:
        if sys.argv[1] == "dropdb":
            dropdb()
        elif sys.argv[1] == "newdb":
            newdb()
        elif sys.argv[1] == "fillnew":
            fillnew()
        elif sys.argv[1] == "refillall":
            fillall()
        elif sys.argv[1] == "fill_lists":
            fill_lists()
        elif sys.argv[1] == "renew_lists":
            renew_lists()
        elif sys.argv[1] == "new_lists":
            new_lists()
        elif sys.argv[1] == "fsck":
            db_fsck()
        else:
            usage()
    else:
        usage()
