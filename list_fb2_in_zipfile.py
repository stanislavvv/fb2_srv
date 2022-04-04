#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import xmltodict

# True for debug json output
DEBUG = False

if DEBUG:
    import json  # debug

READ_SIZE = 10240


# show headers for pipe-separated output
def show_headers():
    print("filename|genre|author_first|author_middle|author_last|author_id|book_title|lang|annotation_text")


# pass over nested dict and return all values as single text string
def recursive_text(data):
    ret = ""
    if isinstance(data, list):
        for li in data:
            ret += recursive_text(li)
            if isinstance(li, dict):
                ret += recursive_text(li)
    elif isinstance(data, dict):
        for k, v in data.items():
            ret += recursive_text(v)
    else:
        ret += str(data)
    return ret


# return comma-separated string of genres from input struct
def get_genre(genr):
    genre = ""  # default
    g = []
    if isinstance(genr, dict):
        for k, v in genr.items():
            if type(v) is str:
                g.append(v)
            elif isinstance(v, dict):
                for k, v2 in v.items():
                    g.append(v2)
            elif isinstance(v, list):
                for v2 in v:
                    g.append(v2)
        genre = ",".join(g)
    elif isinstance(genr, list):
        for i in genr:
            if type(i) is str:
                g.append(i)
            elif isinstance(i, dict):
                for k, v in i.items():
                    g.append(v)
            elif isinstance(i, list):
                for v in i:
                    g.append(v)
        genre = ",".join(g)
    else:
        genre = str(genr)
    return genre


# get filename in zip, print some data
def fb2parse(filename):
    fb2 = z.open(filename)
    doc = fb2.read()
    data = xmltodict.parse(doc, xml_attribs=False)
    info = data['FictionBook']['description']['title-info']
    if DEBUG:
        print(json.dumps(info, indent=2))  # debug
    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author_first = ''
    author_middle = ''
    author_last = ''
    author_id = ''
    if 'author' in info and info['author'] is not None:
        if 'first-name' in info['author']:
            author_first = info['author']['first-name']
        if 'middle-name' in info['author']:
            author_middle = info['author']['middle-name']
        if 'last-name' in info['author']:
            author_last = info['author']['last-name']
        if 'id' in info['author']:
            author_id = info['author']['id']
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = info['book-title']
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = info['lang']
    annotext = ''
    if 'annotation' in info:
        annotext = recursive_text(info['annotation'])
    out = [
        filename,
        genre,
        str(author_first),
        str(author_middle),
        str(author_last),
        str(author_id),
        str(book_title),
        str(lang),
        annotext.replace('\n', " ")
    ]
    # print(json.dumps(out, indent=2))  # debug
    print('|'.join(out))


# main proc
def iterate_zip(z):
    show_headers()
    for filename in z.namelist():
        if not os.path.isdir(filename):
            try:
                fb2parse(filename)
            except Exception as e:
                print("ERR: " + str(z.filename) + "/" + str(filename) + ": " + str(e), file=sys.stderr)


if __name__ == '__main__':
    z = zipfile.ZipFile(sys.argv[1])  # Flexibility with regard to zipfile
    iterate_zip(z)
