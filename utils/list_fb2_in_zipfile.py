#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import xmltodict
import hashlib
from bs4 import BeautifulSoup
from datetime import datetime


# True for debug json output
# DEBUG = True
DEBUG = False

if DEBUG:
    import json  # debug

READ_SIZE = 40960  # description in 20kb...


# show headers for pipe-separated output
def show_headers():
    print("zip|filename|genre|authors|author_ids|sequence|sequence_names|sequence_ids|book_title|book_id|lang|date_time|annotation_text")


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


# return comma-separated string of authors from input struct
def get_author_ids(author):
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
            a_tmp2 = " ".join(a_tmp)
            g.append(hashlib.md5(a_tmp2.encode('utf-8')).hexdigest())
        ret = ",".join(g)
    else:
        a_tmp = []
        if 'last-name' in author and author['last-name'] is not None:
            a_tmp.append(strlist(author['last-name']))
        if 'first-name' in author and author['first-name'] is not None:
            a_tmp.append(strlist(author['first-name']))
        if 'middle-name' in author and author['middle-name'] is not None:
            a_tmp.append(strlist(author['middle-name']))
        r = " ".join(a_tmp)
        ret = hashlib.md5(r.encode('utf-8')).hexdigest()
    return ret


def get_sequence(seq):
    if isinstance(seq, str):
        return seq, ""
    if isinstance(seq, dict):
        name = None
        num = None
        if '@name' in seq:
            name = seq['@name']
        if '@number' in seq:
            num = seq['@number']
        if name is not None and num is not None:
            return "%s:%s" % (name, num)
        elif name is not None:
            return "%s" % name
        elif num is not None:
            return ":%s" % num
        return ""
    elif isinstance(seq, list):
        ret = []
        for s in seq:
            name = None
            num = None
            if '@name' in s:
                name = s['@name']
            if '@number' in s:
                num = s['@number']
            if name is not None and num is not None:
                ret.append("%s:%s" % (name, num))
            elif name is not None:
                ret.append("%s" % name)
            elif num is not None:
                ret.append(":%s" % num)
        return ",".join(ret)
    return str(seq)


def get_sequence_names(seq):
    if isinstance(seq, str):
        return seq, ""
    if isinstance(seq, dict):
        name = None
        if '@name' in seq:
            name = seq['@name']
            r = "%s" % name
            return r
        return ""
    elif isinstance(seq, list):
        ret = []
        for s in seq:
            name = None
            if '@name' in s:
                name = s['@name']
                r = "%s" % name
                ret.append(r)
        return ",".join(ret)
    return str(seq)


def get_sequence_ids(seq):
    if isinstance(seq, str):
        return seq, ""
    if isinstance(seq, dict):
        name = None
        if '@name' in seq:
            name = seq['@name']
            r = "%s" % name
            return hashlib.md5(r.encode('utf-8')).hexdigest()
        return ""
    elif isinstance(seq, list):
        ret = []
        for s in seq:
            name = None
            if '@name' in s:
                name = s['@name']
                r = "%s" % name
                ret.append(hashlib.md5(r.encode('utf-8')).hexdigest())
        return ",".join(ret)
    return str(seq)

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
    file_info = z.getinfo(filename)
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
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
    author_ids = ''
    if 'author' in info and info['author'] is not None:
        author_ids = get_author_ids(info['author'])
    sequence = ''
    if 'sequence' in info and info['sequence'] is not None:
        sequence = get_sequence(info['sequence'])
    sequence_names = ''
    if 'sequence' in info and info['sequence'] is not None:
        sequence_names = get_sequence_names(info['sequence'])
    sequence_ids = ''
    if 'sequence' in info and info['sequence'] is not None:
        sequence_ids = get_sequence_ids(info['sequence'])
    book_title = ''
    if 'book-title' in info and info['book-title'] is not None:
        book_title = info['book-title']
    lang = ''
    if 'lang' in info and info['lang'] is not None:
        lang = get_lang(info['lang'])
    annotext = ''
    if 'annotation' in info:
        annotext = recursive_text(info['annotation'])
    book_path = str(os.path.basename(z.filename)) + "/" + filename
    book_id = hashlib.md5(book_path.encode('utf-8')).hexdigest()
    out = [
        str(os.path.basename(z.filename)),
        filename,
        genre,
        author.strip(),
        author_ids,
        sequence,
        sequence_names,
        sequence_ids,
        str(book_title),
        book_id,
        str(lang),
        date_time,
        str(size),
        str(annotext.replace('\n', " ").replace('|', " "))
    ]
    # print(json.dumps(out, indent=2))  # debug
    print('|'.join(out))


# main proc
def iterate_zip(z):
    # show_headers()
    for filename in z.namelist():
        if not os.path.isdir(filename):
            #try:
                fb2parse(filename)
            #except Exception as e:
            #    print("ERR: " + str(z.filename) + "/" + str(filename) + ": " + str(e), file=sys.stderr)


if __name__ == '__main__':
    z = zipfile.ZipFile(sys.argv[1])  # Flexibility with regard to zipfile
    iterate_zip(z)
