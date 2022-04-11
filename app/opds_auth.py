# -*- coding: utf-8 -*-

import xmltodict
import datetime
import sqlite3
import urllib.parse
import hashlib
from flask import current_app
from .opds_seq import get_db_connection, get_dtiso, any2alphabet


def get_authors_list(auth_root):
    dtiso = get_dtiso()
    ret = {
        "feed": {
            "@xmlns": "http://www.w3.org/2005/Atom",
            "@xmlns:dc": "http://purl.org/dc/terms/",
            "@xmlns:os": "http://a9.com/-/spec/opensearch/1.1/",
            "@xmlns:opds": "http://opds-spec.org/2010/catalog",
            "id": "tag:root:authors",
            "title": "Books by authors",
            "updated": dtiso,
            "icon": "/favicon.ico",
            "link": [
                # {
                    # "@href": "/opds-opensearch.xml",
                    # "@rel": "search",
                    # "@type": "application/opensearchdescription+xml"
                # },
                # {
                    # "@href": "/opds/search?searchTerm={searchTerms}",
                    # "@rel": "search",
                    # "@type": "application/atom+xml"
                # },
                {
                    "@href": "/opds",
                    "@rel": "start",
                    "@type": "application/atom+xml;profile=opds-catalog"
                }
            ],
            "entry": []
        }
    }
    if auth_root is None or auth_root == "" or auth_root == "/" or not isinstance(auth_root, str):
        ALL_AUTHORS = 'SELECT name FROM authors ORDER BY name;'
        conn = get_db_connection()
        rows = conn.execute(ALL_AUTHORS).fetchall()
        for ch in any2alphabet("name", rows, 1):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + urllib.parse.quote(ch),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Авторы на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/authorsindex/" + urllib.parse.quote(ch),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    elif len(auth_root) < 2:
        REQ = 'SELECT name FROM authors WHERE name like "' + auth_root + '%";'
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        ret["feed"]["id"] = "tag:root:authors:" + urllib.parse.quote_plus(auth_root, encoding='utf-8')
        for ch in any2alphabet("name", rows, 3):
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                    "title": ch,
                    "content": {
                        "@type": "text",
                        "#text": "Авторы на '" + ch + "'"
                    },
                    "link": {
                        "@href": "/opds/authors/" + urllib.parse.quote_plus(ch, encoding='utf-8'),
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    else:
        REQ = 'SELECT id, name FROM authors WHERE name LIKE "' + auth_root + '%";'
        ret["feed"]["id"] = "tag:root:authors:" + urllib.parse.quote_plus(auth_root, encoding='utf-8')
        conn = get_db_connection()
        rows = conn.execute(REQ).fetchall()
        for row in rows:
            auth_name = row["name"]
            auth_id = row["id"]
            ret["feed"]["entry"].append(
                {
                    "updated": dtiso,
                    "id": "tag:authors:" + urllib.parse.quote_plus(auth_name, encoding='utf-8'),
                    "title": auth_name,
                    "content": {
                        "@type": "text",
                        "#text": "книги на '" + auth_name + "'"
                    },
                    "link": {
                        "@href": "/opds/author/" + auth_id,
                        "@type": "application/atom+xml;profile=opds-catalog"
                    }
                }
            )
        conn.close()
    return xmltodict.unparse(ret, pretty=True)


