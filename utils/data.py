# -*- coding: utf-8 -*-

import hashlib

from .strings import strnull, strlist, quote_identifier, rchop


# get name, strip quotes from begin/end, return md5
def make_id(name):
    if name is not None and name != "":
        n = str(name).strip("'").strip('"')
    else:
        n = "--- unknown ---"
    return hashlib.md5(n.encode('utf-8')).hexdigest()


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
                g.append(v.ljust(4))
            elif isinstance(v, dict):
                for k, v2 in v.items():
                    if not v2.isdigit() and v2 != "":
                        g.append(v2.ljust(4))
            elif isinstance(v, list):
                for v2 in v:
                    if not v2.isdigit() and v2 != "":
                        g.append(v2.ljust(4))
        genre = "|".join(g)
    elif isinstance(genr, list):
        for i in genr:
            if type(i) is str and not i.isdigit() and i != "":
                g.append(i.ljust(4))
            elif isinstance(i, dict):
                for k, v in i.items():
                    if not v.isdigit() and v != "":
                        g.append(v.ljust(4))
            elif isinstance(i, list):
                for v in i:
                    if not v.isdigit() and v != "":
                        g.append(v.ljust(4))
        genre = "|".join(g)
    else:
        genre = str(genr.ljust(4))
    return genre


# return pipe-separated string of authors from input struct
def get_authors(author):
    ret = "--- unknown ---"  # default
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
                    g.append(a_tmp2.ljust(4))
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
            ret = r.ljust(4)
    return ret


# return pipe-separated string of authors from input struct
def get_author_ids(author):
    ret = make_id("--- unknown ---".encode('utf-8'))  # default
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
                g.append(make_id(a_tmp2.ljust(4)))
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
            ret = make_id(r.ljust(4))
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
        return seq
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
    ret = ""
    if isinstance(seq, str) and seq != "":
        ret = make_id(seq)
    if isinstance(seq, dict):
        name = None
        if '@name' in seq:
            name = seq['@name']
            r = "%s" % name
            return make_id(r)
        ret = ""
    elif isinstance(seq, list):
        ret = []
        for s in seq:
            name = None
            if '@name' in s:
                name = s['@name']
                r = "%s" % name
                ret.append(make_id(r))
        return "|".join(ret)
    return ret


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