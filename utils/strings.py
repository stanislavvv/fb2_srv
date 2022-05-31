# -*- coding: utf-8 -*-

import codecs


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


# '"word word"' -> 'word word'
# '"word" word' -> '`word` word'
def strip_quotes(s: str):
    if s is None:
        return None
    s = s.replace('"', '`'),replace('«', '`'),replace('»', '`')
    tmp = s.strip('`')
    if tmp.find('`') == -1:  # not found
        s = tmp
    return s


# init genres dict
def get_genres():
    global genres
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
    global genres_replacements
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
    global genres
    gg = g[2].split('|')
    for i in gg:
        if i not in genres and i != "":
            print(g[0] + "|" + g[1] + "|" + i)


def genres_replace(genrs):
    global genres_replacements
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


def get_genre_name(gen_id):
    if gen_id in genres and genres[gen_id] is not None:
        return genres[gen_id]
    else:
        return gen_id
