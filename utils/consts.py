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
    CREATE TABLE `books_descr` (
        'book_id'    TEXT NOT NULL,
        'book_title' TEXT,
        'annotation' TEXT,
        FOREIGN KEY(book_id) REFERENCES books(book_id)
    )
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
    CREATE TABLE `books_authors` (
        'book_id'               TEXT NOT NULL,
        'author_id'             TEXT,
        FOREIGN KEY(book_id)    REFERENCES books(book_id)
        FOREIGN KEY(author_id)  REFERENCES authors(id)
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
    CREATE TABLE 'genres_meta' (
        'meta_id'    INTEGER,
        'description'	TEXT,
        PRIMARY KEY('meta_id')
    );
    """,
    """
    CREATE TABLE 'genres' (
        'id'	TEXT UNIQUE,
        'meta_id'    INTEGER,
        'description'	TEXT,
        PRIMARY KEY('id')
        FOREIGN KEY(meta_id) REFERENCES genres_meta(meta_id)
    );
    """,
    """
    CREATE TABLE 'seq_books' (
        'seq_id'	TEXT NOT NULL,
        'book_id'	TEXT NOT NULL,
        'seq_num'	INTEGER,
        PRIMARY KEY('seq_id', 'book_id')
        FOREIGN KEY(seq_id) REFERENCES sequences(id)
        FOREIGN KEY(book_id) REFERENCES books(book_id)
    );
    """
]
