#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import xmltodict
from bs4 import BeautifulSoup

# True for debug json output
#DEBUG = True
DEBUG = False

if DEBUG:
    import json  # debug

READ_SIZE = 40960  # description in 20kb...


# show headers for pipe-separated output
def show_headers():
    print("zip|filename|genre|authors|sequence_name|sequence_num|book_title|lang|annotation_text")


# return empty string if None, else return content
def strnull(s):
    if s is None:
        return ""
    return str(s)


# return string or first element of list
def strlist(s):
    if isinstance(s, str):
        return strnull(s)
    if isinstance(s, list):
        return strnull(s[0])
    return strnull(str(s))


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
            if type(v) is str and not v.isdigit() and v != "":
                g.append(v)
            elif isinstance(v, dict):
                for k, v2 in v.items():
                    if not v2.isdigit() and v2 != "":
                        g.append(v2)
            elif isinstance(v, list):
                for v2 in v:
                    if not v2.isdigit() and v2 != "":
                        g.append(v2)
        genre = ",".join(g)
    elif isinstance(genr, list):
        for i in genr:
            if type(i) is str and not i.isdigit() and i != "":
                g.append(i)
            elif isinstance(i, dict):
                for k, v in i.items():
                    if not v.isdigit() and v != "":
                        g.append(v)
            elif isinstance(i, list):
                for v in i:
                    if not v.isdigit() and v != "":
                        g.append(v)
        genre = ",".join(g)
    else:
        genre = str(genr)
    return genre


# return comma-separated string of authors from input struct
def get_authors(author):
    ret = ""  # default
    g = []
    if isinstance(author, list):
        for i in author:
            a_tmp = []
            if 'last-name' in i and i['last-name'] is not None:
                a_tmp.append(strlist(i['last-name']))
            if 'first-name' in i and i['first-name'] is not None:
                a_tmp.append(strlist(i['first-name']))
            if 'middle-name' in i and i['middle-name'] is not None:
                a_tmp.append(strlist(i['middle-name']))
            g.append(" ".join(a_tmp))
        ret = ",".join(g)
    else:
        a_tmp = []
        if 'last-name' in author and author['last-name'] is not None:
            a_tmp.append(strlist(author['last-name']))
        if 'first-name' in author and author['first-name'] is not None:
            a_tmp.append(strlist(author['first-name']))
        if 'middle-name' in author and author['middle-name'] is not None:
            a_tmp.append(strlist(author['middle-name']))
        ret = " ".join(a_tmp)
    return ret


def get_sequence(seq):
    if isinstance(seq, str):
        return seq, ""
    name = ""
    num = ""
    if isinstance(seq, dict):
        if '@name' in seq:
            name = seq['@name']
        if '@number' in seq:
            num = seq['@number']
        return name, num
    return str(seq), "---"

def get_lang(lng):
    ret = ""
    rets = {}
    if isinstance(lng, list):
        for i in lng:
            rets[i] = 1
        ret = ",".join(rets)
    else:
        ret = str(lng)
    return ret

# get filename in zip, print some data
def fb2parse(filename):
    fb2 = z.open(filename)
    bs = BeautifulSoup(fb2.read(READ_SIZE), 'xml')
    doc = bs.prettify()
    # data = xmltodict.parse(doc, xml_attribs=False)
    data = xmltodict.parse(doc)
    info = data['FictionBook']['description']['title-info']
    if DEBUG:
        print(json.dumps(info, indent=2))  # debug
    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author = ''
    if 'author' in info and info['author'] is not None:
        author = get_authors(info['author'])
    sequence_name = ''
    sequence_num = ''
    if 'sequence' in info and info['sequence'] is not None:
        sequence_name, sequence_num = get_sequence(info['sequence'])
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = info['book-title']
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info:
        annotext = recursive_text(info['annotation'])
    out = [
        str(z.filename),
        filename,
        genre,
        author.strip(),
        sequence_name,
        sequence_num,
        str(book_title),
        str(lang),
        str(annotext.replace('\n', " ").replace('|', " "))
    ]
    # print(json.dumps(out, indent=2))  # debug
    print('|'.join(out))


# main proc
def iterate_zip(z):
    # show_headers()
    for filename in z.namelist():
        if not os.path.isdir(filename):
            try:
                fb2parse(filename)
            except Exception as e:
                print("ERR: " + str(z.filename) + "/" + str(filename) + ": " + str(e), file=sys.stderr)


if __name__ == '__main__':
    z = zipfile.ZipFile(sys.argv[1])  # Flexibility with regard to zipfile
    iterate_zip(z)
