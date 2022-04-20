# -*- coding: utf-8 -*-

from flask import Blueprint, Response
from .opds_seq import main_opds, get_sequences, get_books_in_seq
from .opds_auth import get_authors_list, get_author_list, get_author_sequences, get_author_sequence
from .opds_auth import get_author_sequenceless, get_author_by_alphabet, get_author_by_time
from .opds_genres import get_genres_list, get_genre_books
import xmltodict

api = Blueprint("api", __name__)


@api.route("/opds", methods=['GET'])
@api.route("/opds/", methods=['GET'])
def opds_root():
    xml = xmltodict.unparse(main_opds(), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencesindex/", methods=['GET'])
@api.route("/opds/sequencesindex", methods=['GET'])
def opds_by_seq_root():
    xml = xmltodict.unparse(get_sequences(None), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencesindex/<seq>", methods=['GET'])
@api.route("/opds/sequences/<seq>", methods=['GET'])
def opds_by_seq(seq=None):
    xml = xmltodict.unparse(get_sequences(seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/sequencebooks/<seq>", methods=['GET'])
def opds_books_in_seq(seq=None):
    xml = xmltodict.unparse(get_books_in_seq(seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsindex/", methods=['GET'])
@api.route("/opds/authorsindex", methods=['GET'])
def opds_by_authors_root():
    xml = xmltodict.unparse(get_authors_list(None), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsindex/<auth>", methods=['GET'])
@api.route("/opds/authors/<auth>", methods=['GET'])
def opds_by_authors(auth=None):
    xml = xmltodict.unparse(get_authors_list(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>", methods=['GET'])
def opds_by_author(auth=None):
    xml = xmltodict.unparse(get_author_list(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/sequences")
def opds_author_sequences(auth=None):
    xml = xmltodict.unparse(get_author_sequences(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/authorsequence/<auth>/<seq>")
def opds_author_sequence(auth=None, seq=None):
    xml = xmltodict.unparse(get_author_sequence(auth, seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/sequenceless")
def opds_author_sequenceless(auth=None):
    xml = xmltodict.unparse(get_author_sequenceless(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/alphabet")
def opds_author_alphabet(auth=None):
    xml = xmltodict.unparse(get_author_by_alphabet(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/author/<auth>/time")
def opds_author_time(auth=None):
    xml = xmltodict.unparse(get_author_by_time(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/genres/")
@api.route("/opds/genres")
def opds_genres_root():
    xml = xmltodict.unparse(get_genres_list(), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/genres/<gen_id>")
def opds_genres_book(gen_id=None):
    xml = xmltodict.unparse(get_genre_books(gen_id), pretty=True)
    return Response(xml, mimetype='text/xml')


@api.route("/opds/genres/<gen_id>/<int:page>")
def opds_genres_book_page(gen_id=None, page=0):
    xml = xmltodict.unparse(get_genre_books(gen_id, page), pretty=True)
    return Response(xml, mimetype='text/xml')
