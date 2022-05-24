# -*- coding: utf-8 -*-

import os
import zipfile
import xmltodict
import sqlite3
import json

from bs4 import BeautifulSoup
from datetime import datetime
from .strings import get_genres, get_genres_replace, genres_replace, check_genres, rchop
from .data import get_genre, get_authors, get_author_ids
from .data import get_sequence, get_sequence_names, get_sequence_ids, get_lang
from .data import get_struct_by_key, make_id, get_replace_list, replace_book
from .data import get_title
from .db import author2db, genres2db, seq2db, unicode_nocase_collation, bookinfo2db
import __main__

READ_SIZE = 20480  # description in 20kb...


# get filename in opened zip (assume filename format as fb2), return book struct
def fb2parse(z, filename, replace_data):
    file_info = z.getinfo(filename)
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
    if size < 1000:
        return None
    fb2 = z.open(filename)
    bs = BeautifulSoup(bytes(fb2.read(READ_SIZE)), 'xml')
    bs_descr = bs.FictionBook.description
    tinfo = bs_descr.find("title-info")
    bs_anno = str(tinfo.annotation)
    bs_anno = bs_anno.replace("<annotation>","").replace("</annotation>","")
    doc = bs.prettify()
    data = xmltodict.parse(doc)
    if 'FictionBook' not in data:  # parse with namespace
        data = xmltodict.parse(
            doc,
            process_namespaces=True,
            namespaces={'http://www.gribuser.ru/xml/fictionbook/2.0': None}
        )
    if 'FictionBook' not in data:  # not fb2
        return None
    fb2data = get_struct_by_key('FictionBook', data)  # data['FictionBook']
    descr = get_struct_by_key('description', fb2data)  # fb2data['description']
    info = get_struct_by_key('title-info', descr)  # descr['title-info']
    if replace_data is not None and filename in replace_data:
        info = replace_book(filename, info, replace_data)

    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author = '--- unknown ---'
    author_ids = make_id(author)
    if 'author' in info and info['author'] is not None:
        author = get_authors(info['author'])
    if 'author' in info and info['author'] is not None:
        author_ids = get_author_ids(info['author'])
    sequence = None
    if 'sequence' in info and info['sequence'] is not None:
        sequence = get_sequence(info['sequence'])
    seq_names = ''
    if 'sequence' in info and info['sequence'] is not None:
        seq_names = get_sequence_names(info['sequence'])
    seq_ids = ''
    if 'sequence' in info and info['sequence'] is not None:
        seq_ids = get_sequence_ids(info['sequence'])
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = get_title(info['book-title'])
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info and info['annotation'] is not None:
        annotext = bs_anno
    book_path = str(os.path.basename(z.filename)) + "/" + filename
    book_id = make_id(book_path)
    out = {
        "zipfile": str(os.path.basename(z.filename)),
        "filename": filename,
        "genres": genre,
        "authors": author,
        "author_ids": author_ids,
        "sequences": sequence,
        "seq_names": seq_names,
        "seq_ids": seq_ids,
        "book_title": str(book_title),
        "book_id": book_id,
        "lang": str(lang),
        "date_time": date_time,
        "size": str(size),
        "annotation": str(annotext.replace('\n', " ").replace('|', " "))
    }
    return out


# iterate over files in zip, return array of book struct
def ziplist(zip_file):
    DEBUG = __main__.DEBUG
    print(zip_file)
    ret = []
    z = zipfile.ZipFile(zip_file)
    replace_data = get_replace_list(zip_file)
    for filename in z.namelist():
        if not os.path.isdir(filename):
            if DEBUG:
                print(zip_file + "/" + filename + "             ")
            res = fb2parse(z, filename, replace_data)
            if res is not None:
                ret.append(res)
    return ret


# iterate over list data, send it to db
def iterate_list(blist, dbfile):
    DEBUG = __main__.DEBUG
    data = open(blist, 'r')
    zip_file = os.path.basename(rchop(blist, '.list'))
    con = sqlite3.connect(dbfile)
    con.create_collation(
        "UNICODE_NOCASE", unicode_nocase_collation
    )
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE zipfile = ?", [zip_file])
    if DEBUG:
        authors_list = blist + ".authors"  # debug
        au = open(authors_list, 'w')  # debug
    books = json.load(data)
    for book in books:
        insdata = [
            book["zipfile"],
            book["filename"],
            book["genres"],
            book["author_ids"],
            book["seq_ids"],
            book["book_id"],
            book["lang"],
            book["date_time"],
            book["size"],
        ]

        insdata[2] = genres_replace(insdata[2])
        check_genres([book["zipfile"], book["filename"], insdata[2]])
        genres2db(cur, insdata[2])
        author2db(cur, book["authors"])
        bookinfo2db(cur, book["book_id"], book["book_title"], book["annotation"])
        seq2db(cur, book["sequences"], insdata[0], insdata[1])
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (insdata))
        if DEBUG:
            for author in book["authors"].split("|"):  # debug
                au.write(author + "|" + book["zipfile"] + "/" + book["filename"] + "\n")  # debug
    con.commit()
    con.close()
    if DEBUG:
        au.close()
    data.close()


# wrapper over iterate_list, get .list, fill some auxiliary structs, pass .list next to iterate_list
def booklist2db(booklist, dbfile):
    print(booklist)
    get_genres()  # official genres from genres.list
    get_genres_replace()  # replacement for unofficial genres from genres_replace.list
    iterate_list(booklist, dbfile)
