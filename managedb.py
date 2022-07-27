#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import sqlite3
import json
import logging

from app import create_app
from utils import ziplist, booklist2db
from utils.consts import INPX, CREATE_REQ
from utils.db import unicode_nocase_collation, clean_authors, clean_sequences, vacuum_db, clean_genres

DEBUG = True  # default, configure in app/config.py
DBLOGLEVEL = logging.DEBUG


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
    logging.info("removing %s" % dbfile)
    os.remove(dbfile)


def newdb():
    dbfile = app.config['DBSQLITE']
    if os.path.exists(dbfile):
        dropdb()
    logging.info("creating %s" % dbfile)
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    cur = con.cursor()
    for req in CREATE_REQ:
        logging.debug('REQ: %s' % req)
        cur.execute(req)
    con.commit()
    con.close()


def create_booklist(inpx_data, zip_file):
    booklist = zip_file + ".list"
    list = ziplist(inpx_data, zip_file)
    bl = open(booklist, 'w')
    bl.write(json.dumps(list, ensure_ascii=False))
    bl.close()


def update_booklist(inpx_data, zip_file):
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
    create_booklist(inpx_data, zip_file)
    return True


def fillall():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        create_booklist(inpx_data, zip_file)
        booklist = zip_file + ".list"
        if os.path.exists(booklist):
            booklist2db(booklist, dbfile, DEBUG)


def fillnew():
    zipdir = app.config['ZIPS']
    dbfile = app.config['DBSQLITE']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        booklist = zip_file + ".list"
        if update_booklist(inpx_data, zip_file):
            booklist2db(booklist, dbfile, DEBUG)


def fill_lists():
    dbfile = app.config['DBSQLITE']
    zipdir = app.config['ZIPS']
    i = 0
    for booklist in glob.glob(zipdir + '/*.zip.list'):
        i += 1
        logging.info("[" + str(i) + "] ")
        booklist2db(booklist, dbfile, DEBUG)


def renew_lists():
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        create_booklist(inpx_data, zip_file)


def new_lists():
    zipdir = app.config['ZIPS']
    inpx_data = zipdir + "/" + INPX
    i = 0
    for zip_file in glob.glob(zipdir + '/*.zip'):
        i += 1
        logging.info("[" + str(i) + "] ")
        update_booklist(inpx_data, zip_file)


def db_fsck():
    dbfile = app.config['DBSQLITE']
    clean_authors(dbfile, DEBUG)
    clean_sequences(dbfile, DEBUG)
    clean_genres(dbfile, DEBUG)
    vacuum_db(dbfile, DEBUG)


if __name__ == "__main__":
    app = create_app()
    DEBUG = app.config['DEBUG']
    DBLOGLEVEL = app.config['DBLOGLEVEL']
    DBLOGFORMAT = app.config['DBLOGFORMAT']
    logging.basicConfig(level=DBLOGLEVEL, format=DBLOGFORMAT)
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
