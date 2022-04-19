#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import sqlite3
import json

from app import create_app
from utils import ziplist, booklist2db

CREATE_REQ = [
    """
    CREATE TABLE 'books' (
        'zipfile'	TEXT NOT NULL,
        'filename'	TEXT NOT NULL,
        'genres'	TEXT,
        'authors'	TEXT COLLATE NOCASE,
        'author_ids'	NUMERIC,
        'sequence'	TEXT,
        'sequence_names'	TEXT COLLATE NOCASE,
        'sequence_ids'	TEXT,
        'book_title'	TEXT COLLATE NOCASE,
        'book_id'	TEXT,
        'lang'	TEXT,
        'date_time'	TEXT,
        'size'	INTEGER,
        'annotation'	TEXT COLLATE NOCASE,
        PRIMARY KEY('zipfile','filename','authors','book_title')
    );
    """,
    """
    CREATE TABLE 'authors' (
        'id'    TEXT UNIQUE,
        'name'  TEXT COLLATE NOCASE,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'sequences' (
        'id'    TEXT UNIQUE,
        'name'  TEXT COLLATE NOCASE,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'genres' (
        'id'	TEXT UNIQUE,
        'description'	TEXT COLLATE NOCASE,
        'group'	TEXT,
        PRIMARY KEY('id')
    );
    """
]


def usage():
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" dropdb     -- remove database from disk")
    print(" cleandb    -- clean database tables content (not recreate db)", " NOT IMPLEMENTED")
    print(" newdb      -- [re]create database from scratch")
    print(" fillnew    -- add new data to database")
    print(" refillall  -- pass over all zips, del from db, recreate file lists and fill them to db")
    print(" fill_lists -- as refillall, but does not recreate lists, only refill data to db", " UNIMPLEMENTED")


def dropdb():
    dbfile = app.config['DBSQLITE']
    print("removing", dbfile)
    os.remove(dbfile)


def newdb():
    dbfile = app.config['DBSQLITE']
    if os.path.exists(dbfile):
        dropdb()
    print("creating ", dbfile)
    con = sqlite3.connect(dbfile)
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
    if os.path.exists(booklist):
        ziptime = os.path.getmtime(zip_file)
        listtime = os.path.getmtime(booklist)
        if ziptime < listtime:
            return False
    create_booklist(zip_file)
    if os.path.exists(booklist):
        booklist2db(booklist, app.config['DBSQLITE'])
        return True
    else:
        return False


def fillall():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    for zip_file in glob.glob(zipdir + '/*.zip'):
        create_booklist(zip_file)
        booklist = zip_file + ".list"
        if os.path.exists(booklist):
            booklist2db(booklist, dbfile)


def fillnew():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    for zip_file in glob.glob(zipdir + '/*.zip'):
        booklist = zip_file + ".list"
        if update_booklist(zip_file) and os.path.exists(booklist):
            booklist = zip_file + ".list"
            booklist2db(booklist, dbfile)


def fill_lists():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    for booklist in glob.glob(zipdir + '/*.zip.list'):
        booklist2db(booklist, dbfile)


if __name__ == "__main__":
    app = create_app()
    if len(sys.argv) > 1:
        if sys.argv[1] == "dropdb":
            dropdb()
        elif sys.argv[1] == "cleandb":
            print("clean:", app.config['DBSQLITE'])
        elif sys.argv[1] == "newdb":
            newdb()
        elif sys.argv[1] == "fillnew":
            fillnew()
        elif sys.argv[1] == "refillall":
            fillall()
        elif sys.argv[1] == "fill_lists":
            fill_lists()
        else:
            usage()
    else:
        usage()
