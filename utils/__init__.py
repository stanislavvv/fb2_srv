# -*- coding: utf-8 -*-

import os
import zipfile
import xmltodict
import hashlib
import sqlite3
import codecs
import json

from bs4 import BeautifulSoup
from datetime import datetime


READ_SIZE = 20480  # description in 20kb...


# genres (see get_genres())
genres = {}

# fix some wrong genres
genres_replacements = {}


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


# return pipe-separated string of genres from input struct
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
        genre = "|".join(g)
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
        genre = "|".join(g)
    else:
        genre = str(genr)
    return genre


# return comma-separated string of authors from input struct
def get_authors(author):
    ret = "-"  # default
    g = []
    if isinstance(author, list):
        for i in author:
            a_tmp = []
            if i is not None:
                if 'last-name' in i and i['last-name'] is not None:
                    a_tmp.append(strlist(i['last-name']))
                if 'first-name' in i and i['first-name'] is not None:
                    a_tmp.append(strlist(i['first-name']))
                if 'middle-name' in i and i['middle-name'] is not None:
                    a_tmp.append(strlist(i['middle-name']))
                if 'nickname' in i and i['nickname'] is not None:
                    a_tmp.append('(' + strlist(i['nickname']) + ')')
                a_tmp2 = " ".join(a_tmp)
                a_tmp2 = a_tmp2.strip().strip("'").strip('"')
                if len(a_tmp2) > 0:
                    g.append(a_tmp2)
        if len(g) > 0:
            ret = "|".join(g)
    else:
        a_tmp = []
        if author is not None:
            if 'last-name' in author and author['last-name'] is not None:
                a_tmp.append(strlist(author['last-name']))
            if 'first-name' in author and author['first-name'] is not None:
                a_tmp.append(strlist(author['first-name']))
            if 'middle-name' in author and author['middle-name'] is not None:
                a_tmp.append(strlist(author['middle-name']))
            if 'nickname' in author and author['nickname'] is not None:
                a_tmp.append('(' + strlist(author['nickname']) + ')')
        r = " ".join(a_tmp)
        r = r.strip().strip("'").strip('"')
        if len(r) > 0:
            ret = r
    return ret


# return comma-separated string of authors from input struct
def get_author_ids(author):
    ret = "336d5ebc5436534e61d16e63ddfca327"  # default
    g = []
    if isinstance(author, list):
        for i in author:
            a_tmp = []
            if i is not None:
                if 'last-name' in i and i['last-name'] is not None:
                    a_tmp.append(strlist(i['last-name']))
                if 'first-name' in i and i['first-name'] is not None:
                    a_tmp.append(strlist(i['first-name']))
                if 'middle-name' in i and i['middle-name'] is not None:
                    a_tmp.append(strlist(i['middle-name']))
                if 'nickname' in i and i['nickname'] is not None:
                    a_tmp.append('(' + strlist(i['nickname']) + ')')
            a_tmp2 = " ".join(a_tmp)
            a_tmp2 = a_tmp2.strip().strip("'").strip('"')
            if len(a_tmp2) > 0:
                g.append(hashlib.md5(a_tmp2.encode('utf-8')).hexdigest())
        if len(g) > 0:
            ret = "|".join(g)
    else:
        a_tmp = []
        if author is not None:
            if 'last-name' in author and author['last-name'] is not None:
                a_tmp.append(strlist(author['last-name']))
            if 'first-name' in author and author['first-name'] is not None:
                a_tmp.append(strlist(author['first-name']))
            if 'middle-name' in author and author['middle-name'] is not None:
                a_tmp.append(strlist(author['middle-name']))
            if 'nickname' in author and author['nickname'] is not None:
                a_tmp.append('(' + strlist(author['nickname']) + ')')
        r = " ".join(a_tmp)
        r = r.strip().strip("'").strip('"')
        if len(r) > 0:
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
        return "|".join(ret)
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
        return "|".join(ret)
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
        return "|".join(ret)
    return str(seq)


def get_lang(lng):
    ret = ""
    rets = {}
    if isinstance(lng, list):
        for i in lng:
            rets[i] = 1
        ret = "|".join(rets)
    else:
        ret = str(lng)
    return ret


# ret substr by key
def get_struct_by_key(key, struct):
    if key in struct:
        return struct[key]
    if isinstance(struct, list):
        for k in struct:
            r = get_struct_by_key(key, k)
            if r is not None:
                return r
    if isinstance(struct, dict):
        for k, v in struct.items():
            r = get_struct_by_key(key, v)
            if r is not None:
                return r
    return None


# get filename in zip, print some data
def fb2parse(z, filename):
    file_info = z.getinfo(filename)
    fb2dt = datetime(*file_info.date_time)
    date_time = fb2dt.strftime("%F_%H:%M")
    size = file_info.file_size
    if size < 1000:
        return None
    fb2 = z.open(filename)
    bs = BeautifulSoup(bytes(fb2.read(READ_SIZE)), 'xml')
    doc = bs.prettify()
    # data = xmltodict.parse(doc, xml_attribs=False)
    data = xmltodict.parse(doc)
    if 'FictionBook' not in data:  # parse with namespace
        data = xmltodict.parse(
            doc,
            process_namespaces=True,
            namespaces={'http://www.gribuser.ru/xml/fictionbook/2.0': None}
        )
    fb2data = get_struct_by_key('FictionBook', data)  # data['FictionBook']
    descr = get_struct_by_key('description', fb2data)  # fb2data['description']
    # if filename == '509075.fb2':  # debug
    #     print(json.dumps(descr, ensure_ascii=False))
    info = get_struct_by_key('title-info', descr)  # descr['title-info']

    if 'genre' in info and info['genre'] is not None:
        genre = get_genre(info['genre'])
    else:
        genre = ""
    author = '-'
    if 'author' in info and info['author'] is not None:
        author = get_authors(info['author'])
    author_ids = '336d5ebc5436534e61d16e63ddfca327'  # author == '-'
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
    if 'annotation' in info and info['annotation'] is not None:
        annotext = recursive_text(info['annotation'])
    book_path = str(os.path.basename(z.filename)) + "/" + filename
    book_id = hashlib.md5(book_path.encode('utf-8')).hexdigest()
    out = {
        "zipfile": str(os.path.basename(z.filename)),
        "filename": filename,
        "genres": genre,
        "authors": author.strip(),
        "author_ids": author_ids,
        "sequences": sequence,
        "sequence_names": sequence_names,
        "sequence_ids": sequence_ids,
        "book_title": str(book_title),
        "book_id": book_id,
        "lang": str(lang),
        "date_time": date_time,
        "size": str(size),
        "annotation": str(annotext.replace('\n', " ").replace('|', " "))
    }
    # print(json.dumps(out, indent=2))  # debug
    # print('|'.join(out))
    return out


# zip/fb2 list proc
def ziplist(zip_file):
    print(zip_file)
    ret = []
    z = zipfile.ZipFile(zip_file)
    for filename in z.namelist():
        if not os.path.isdir(filename):
            print(zip_file + "/" + filename + "             ", end="\r")
            res = fb2parse(z, filename)
            if res is not None:
                ret.append(res)
    print("")
    return ret


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
            replacement = f[1].split(",")
            genres_replacements[f[0]] = '|'.join(replacement)
    data.close()


# print unknown genres
def check_genres(g):
    gg = g[2].split('|')
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
    gg = genrs.split("|")
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
    return "|".join(ret)


def author2db(cur, authors):
    for author in authors.split("|"):
        if author is not None and author != "":
            author = author.strip()
            author_id = hashlib.md5(author.encode('utf-8')).hexdigest()
            REQ = 'SELECT count(*) FROM authors WHERE id = "%s"' % author_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                author_data = [author_id, author, ""]
                cur.execute("INSERT INTO authors VALUES (?, ?, ?)", (author_data))


def seq2db(cur, seqs):
    for seq in seqs.split("|"):
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
    for genre_id in genrs.split("|"):
        if genre_id is not None and genre_id != "":
            genre = genres[genre_id]
            REQ = 'SELECT count(*) FROM genres WHERE id = "%s"' % genre_id
            cur.execute(REQ)
            rows = cur.fetchall()
            cnt = rows[0][0]
            if cnt == 0:
                genre_data = [genre_id, genre, ""]
                cur.execute("INSERT INTO genres VALUES (?, ?, ?)", (genre_data))


# main function
def iterate_list(blist, dbfile):
    data = open(blist, 'r')
    zip_file = os.path.basename(rchop(blist, '.list'))
    con = sqlite3.connect(dbfile)
    cur = con.cursor()
    cur.execute("DELETE FROM books WHERE zipfile = ?", [zip_file])
    authors_list = blist + ".authors"  # debug
    au = open(authors_list, 'w')  # debug
    books = json.load(data)
    for book in books:
        insdata = [
            book["zipfile"],
            book["filename"],
            book["genres"],
            book["authors"].replace("'","''"),
            book["author_ids"],
            book["sequences"].replace("'","''"),
            book["sequence_names"],
            book["sequence_ids"],
            book["book_title"],
            book["book_id"],
            book["lang"],
            book["date_time"],
            book["size"],
            book["annotation"]
        ]

        insdata[2] = genres_replace(insdata[2])
        check_genres(insdata[:3])
        genres2db(cur, insdata[2])
        author2db(cur, insdata[3])
        seq2db(cur, insdata[6])
        cur.execute("INSERT INTO books VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (insdata))
        for author in book["authors"].split("|"):  # debug
            au.write(author + "|" + book["zipfile"] + "/" + book["filename"] + "\n")  # debug
    con.commit()
    con.close()
    au.close()
    data.close()


def booklist2db(booklist, dbfile):
    get_genres()  # official genres from genres.list
    get_genres_replace()  # replacement for unofficial genres from genres_replace.list
    iterate_list(booklist, dbfile)
