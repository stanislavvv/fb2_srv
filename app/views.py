# -*- coding: utf-8 -*-

from flask import Blueprint, Response, request
from .opds_seq import main_opds, get_sequences, get_books_in_seq
from .opds_auth import get_authors_list, get_author_list, get_author_sequences, get_author_sequence
from .opds_auth import get_author_sequenceless, get_author_by_alphabet, get_author_by_time
from .opds_genres import get_genres_list, get_genre_books
from .opds_search import get_search_main, get_search_authors, get_search_books
import xmltodict

opds = Blueprint("opds", __name__)


@opds.route("/opds", methods=['GET'])
@opds.route("/opds/", methods=['GET'])
def opds_root():
    xml = xmltodict.unparse(main_opds(), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequencesindex/", methods=['GET'])
@opds.route("/opds/sequencesindex", methods=['GET'])
def opds_by_seq_root():
    xml = xmltodict.unparse(get_sequences(None), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequencesindex/<seq>", methods=['GET'])
@opds.route("/opds/sequences/<seq>", methods=['GET'])
def opds_by_seq(seq=None):
    xml = xmltodict.unparse(get_sequences(seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/sequencebooks/<seq>", methods=['GET'])
def opds_books_in_seq(seq=None):
    xml = xmltodict.unparse(get_books_in_seq(seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/authorsindex/", methods=['GET'])
@opds.route("/opds/authorsindex", methods=['GET'])
def opds_by_authors_root():
    xml = xmltodict.unparse(get_authors_list(None), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/authorsindex/<auth>", methods=['GET'])
@opds.route("/opds/authors/<auth>", methods=['GET'])
def opds_by_authors(auth=None):
    xml = xmltodict.unparse(get_authors_list(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<auth>", methods=['GET'])
def opds_by_author(auth=None):
    xml = xmltodict.unparse(get_author_list(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<auth>/sequences")
def opds_author_sequences(auth=None):
    xml = xmltodict.unparse(get_author_sequences(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/authorsequence/<auth>/<seq>")
def opds_author_sequence(auth=None, seq=None):
    xml = xmltodict.unparse(get_author_sequence(auth, seq), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<auth>/sequenceless")
def opds_author_sequenceless(auth=None):
    xml = xmltodict.unparse(get_author_sequenceless(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<auth>/alphabet")
def opds_author_alphabet(auth=None):
    xml = xmltodict.unparse(get_author_by_alphabet(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/author/<auth>/time")
def opds_author_time(auth=None):
    xml = xmltodict.unparse(get_author_by_time(auth), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genres/")
@opds.route("/opds/genres")
def opds_genres_root():
    xml = xmltodict.unparse(get_genres_list(), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genres/<gen_id>")
def opds_genres_book(gen_id=None):
    xml = xmltodict.unparse(get_genre_books(gen_id), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/genres/<gen_id>/<int:page>")
def opds_genres_book_page(gen_id=None, page=0):
    xml = xmltodict.unparse(get_genre_books(gen_id, page), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/search")
def opds_search():
    s_term = request.args.get('searchTerm')
    xml = xmltodict.unparse(get_search_main(s_term), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/search-authors")
def opds_search_authors():
    s_term = request.args.get('searchTerm')
    xml = xmltodict.unparse(get_search_authors(s_term), pretty=True)
    return Response(xml, mimetype='text/xml')


@opds.route("/opds/search-books")
def opds_search_books():
    s_term = request.args.get('searchTerm')
    xml = xmltodict.unparse(get_search_books(s_term), pretty=True)
    return Response(xml, mimetype='text/xml')
