# -*- coding: utf-8 -*-

# from flask import request, redirect, Blueprint, Response, url_for
from flask import redirect, Blueprint, Response, url_for
from .opds_seq import main_opds, get_sequences, get_books_in_seq
from .opds_auth import get_authors_list, get_author_list, get_author_sequences, get_author_sequence
from .opds_auth import get_author_sequenceless, get_author_by_alphabet, get_author_by_time
from .opds_genres import get_genres_list, get_genre_books

api = Blueprint("api", __name__)


@api.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"


@api.route("/st", methods=['GET'])
@api.route("/st/", methods=['GET'])
def static_root():
    location = url_for('static', filename='index.html')
    code = 301
    return redirect(location, code, Response=None)


@api.route("/opds", methods=['GET'])
@api.route("/opds/", methods=['GET'])
def opds_root():
    xml = main_opds()
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencesindex", methods=['GET'])
@api.route("/opds/sequencesindex/", methods=['GET'])
def opds_by_seq_root():
    xml = get_sequences(None)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencesindex/<seq>", methods=['GET'])
@api.route("/opds/sequences/<seq>", methods=['GET'])
def opds_by_seq(seq=None):
    xml = get_sequences(seq)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencebooks/<seq>", methods=['GET'])
def opds_books_in_seq(seq=None):
    xml = get_books_in_seq(seq)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsindex", methods=['GET'])
@api.route("/opds/authorsindex/", methods=['GET'])
def opds_by_authors_root():
    xml = get_authors_list(None)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsindex/<auth>", methods=['GET'])
@api.route("/opds/authors/<auth>", methods=['GET'])
def opds_by_authors(auth=None):
    xml = get_authors_list(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>", methods=['GET'])
def opds_by_author(auth=None):
    xml = get_author_list(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/sequences")
def opds_author_sequences(auth=None):
    xml = get_author_sequences(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsequence/<auth>/<seq>")
def opds_author_sequence(auth=None, seq=None):
    xml = get_author_sequence(auth, seq)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/sequenceless")
def opds_author_sequenceless(auth=None):
    xml = get_author_sequenceless(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/alphabet")
def opds_author_alphabet(auth=None):
    xml = get_author_by_alphabet(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/time")
def opds_author_time(auth=None):
    xml = get_author_by_time(auth)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/genres")
@api.route("/opds/genres/")
def opds_genres_root():
    xml = get_genres_list()
    return Response(xml, mimetype='text/xml')


@api.route("/opds/genres/<gen_id>")
def opds_genres_book(gen_id=None):
    xml = get_genre_books(gen_id)
    return Response(xml, mimetype='text/xml')

@api.route("/opds/genres/<gen_id>/<int:page>")
def opds_genres_book_page(gen_id=None, page=0):
    xml = get_genre_books(gen_id, page)
    return Response(xml, mimetype='text/xml')
