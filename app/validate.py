# -*- coding: utf-8 -*-

import re
from flask import redirect, url_for
from .opds_internals import get_db_connection, unurl

id_check = re.compile('([0-9a-f]+)')
genre_check = re.compile('([0-9a-z_]+)')
zip_check = re.compile('([0-9a-zA-Z_.-]+.zip)')
fb2_check = re.compile('([0-9a-zA-Z_.-]+.fb2)')


def redir_invalid(redir_name):
    location = url_for(redir_name)
    code = 302  # for readers
    return redirect(location, code, Response=None)


def validate_id(s: str):
    ret = s
    if id_check.match(s):
        return ret
    return None


def validate_genre(s: str):
    ret = s
    if genre_check.match(s):
        REQ = "SELECT count(id) FROM genres WHERE id = '" + s + "';"
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        count = rows[0][0]
        if count == 0:
            return None
        return ret
    return None


def validate_genre_meta(s: str):
    ret = s
    if genre_check.match(s):
        REQ = "SELECT count(meta_id) FROM genres_meta WHERE meta_id = '" + s + "';"
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        count = rows[0][0]
        if count == 0:
            return None
        return ret
    return None


# simple prefix validation in .../sequenceindes and .../authorsindex
def validate_prefix(s: str):
    ret = s.replace('"', '`').replace("'", '`')  # no "' quotes in database
    if len(ret) > 10:
        return None
    return ret


# search pattern some normalization
def validate_search(s: str):
    ret = unurl(s).replace('"', '`').replace("'", '`').replace(';', '')
    if len(ret) > 128:
        ret = ret[:128]
    return ret


def validate_zip(s: str):
    ret = s
    if zip_check.match(s):
        return ret
    return None


def validate_fb2(s: str):
    ret = s
    if fb2_check.match(s):
        return ret
    return None
