# -*- coding: utf-8 -*-

INPX = "flibusta_fb2_local.inpx"  # filename of metadata indexes zip

CREATE_REQ = [
    """
    pragma synchronous = normal;
    """,
    """
    pragma page_size = 32768;
    """,
    """
    CREATE TABLE 'books' (
        'zipfile'	TEXT NOT NULL,
        'filename'	TEXT NOT NULL,
        'genres'	TEXT,
        'book_id'	TEXT,
        'lang'	TEXT,
        'date_time'	TEXT,
        'size'	INTEGER,
        PRIMARY KEY('book_id')
    );
    """,
    """
    CREATE INDEX books_zipfile ON books(zipfile)
    """,
    """
    CREATE TABLE `books_descr` (
        'book_id'    TEXT REFERENCES books(book_id) ON DELETE CASCADE,
        'book_title' TEXT,
        'annotation' TEXT
    )
    """,
    """
    CREATE INDEX books_descr_title ON books_descr(book_title);
    """,
    """
    CREATE TABLE 'authors' (
        'id'    TEXT UNIQUE,
        'name'  TEXT,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE INDEX authors_name ON authors(name);
    """,
    """
    CREATE TABLE `books_authors` (
        'book_id'               TEXT REFERENCES books(book_id) ON DELETE CASCADE,
        'author_id'             TEXT REFERENCES authors(id) ON DELETE CASCADE
    );
    """,
    """
    CREATE TABLE 'sequences' (
        'id'    TEXT UNIQUE,
        'name'  TEXT,
        'info'  TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE INDEX sequences_name ON sequences(name);
    """,
    """
    CREATE TABLE 'genres_meta' (
        'meta_id'    INTEGER,
        'description'	TEXT,
        PRIMARY KEY('meta_id')
    );
    """,
    """
    CREATE TABLE 'genres' (
        'id'	TEXT UNIQUE,
        'meta_id'    INTEGER REFERENCES genres_meta(meta_id) ON DELETE SET NULL,
        'description'	TEXT,
        PRIMARY KEY('id')
    );
    """,
    """
    CREATE TABLE 'seq_books' (
        'seq_id'	TEXT REFERENCES sequences(id) ON DELETE CASCADE,
        'book_id'	TEXT REFERENCES books(book_id) ON DELETE CASCADE,
        'seq_num'	INTEGER
    );
    """
]

INSERT_REQ = {
    "books": """
        INSERT OR REPLACE INTO
            books(zipfile, filename, genres, book_id, lang, date_time, size)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """,
    "authors": """
        INSERT OR REPLACE INTO authors(id, name, info) VALUES (?, ?, ?)
    """,
    "sequences": """
        INSERT OR REPLACE INTO sequences(id, name, info) VALUES (?, ?, ?)
    """,
    "bookinfo": """
        INSERT OR REPLACE INTO books_descr(book_id, book_title, annotation) VALUES (?, ?, ?)
    """,
    "auth_ref": """
        INSERT OR REPLACE INTO books_authors(book_id, author_id) VALUES (?, ?)
    """,
    "seq_books": """
        INSERT OR REPLACE INTO seq_books(seq_id, book_id, seq_num) VALUES (?, ?, ?)
    """
}
