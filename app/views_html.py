# -*- coding: utf-8 -*-

from flask import redirect, Blueprint, Response, url_for, render_template, request
from .opds_seq import main_opds, get_sequences, get_books_in_seq
from .opds_auth import get_authors_list, get_author_list, get_author_sequences, get_author_sequence
from .opds_auth import get_author_sequenceless, get_author_by_alphabet, get_author_by_time
from .opds_genres import get_genres_list, get_genre_books
from .opds_search import get_search_main, get_search_authors, get_search_books, get_random_books
from .opds_search import get_search_seqs, get_random_seqs
from .opds_zips import get_zips_list, get_zip_list, get_zip_sequences, get_zip_sequence
from .opds_zips import get_zip_sequenceless, get_zip_by_alphabet
from .validate import redir_invalid, validate_id, validate_genre, validate_prefix
from .validate import validate_search, validate_genre_meta, validate_zip

html = Blueprint("html", __name__, template_folder='templates')

redir_all = "html.html_root"


@html.route("/", methods=['GET'])
def hello_world():
    location = url_for(redir_all)
    code = 301
    return redirect(location, code, Response=None)


@html.route("/st", methods=['GET'])
@html.route("/st/", methods=['GET'])
def static_root():
    location = url_for('static', filename='index.html')
    code = 301
    return redirect(location, code, Response=None)


@html.route("/html", methods=['GET'])
@html.route("/html/", methods=['GET'])
def html_root():
    data = main_opds()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequencesindex/", methods=['GET'])
@html.route("/html/sequencesindex", methods=['GET'])
def html_by_seq_root():
    data = get_sequences(None)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequencesindex/<seq>", methods=['GET'])
@html.route("/html/sequences/<seq>", methods=['GET'])
def html_by_seq(seq=None):
    seq = validate_prefix(seq)
    if seq is None:
        return redir_invalid(redir_all)
    data = get_sequences(seq)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequencebooks/<seq>", methods=['GET'])
def html_books_in_seq(seq=None):
    seq = validate_id(seq)
    if seq is None:
        return redir_invalid(redir_all)
    data = get_books_in_seq(seq)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsindex/", methods=['GET'])
@html.route("/html/authorsindex", methods=['GET'])
def html_by_authors_root():
    data = get_authors_list(None)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsindex/<auth>", methods=['GET'])
@html.route("/html/authors/<auth>", methods=['GET'])
def html_by_authors(auth=None):
    auth = validate_prefix(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_authors_list(auth)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>", methods=['GET'])
def html_by_author(auth=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_author_list(auth)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/sequences")
def html_author_sequences(auth=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_author_sequences(auth)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsequence/<auth>/<seq>")
def html_author_sequence(auth=None, seq=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    seq = validate_id(seq)
    if seq is None:
        return redir_invalid(redir_all)
    data = get_author_sequence(auth, seq)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/sequenceless")
def html_author_sequenceless(auth=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_author_sequenceless(auth)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/alphabet")
def html_author_alphabet(auth=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_author_by_alphabet(auth)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/time")
def html_author_time(auth=None):
    auth = validate_id(auth)
    if auth is None:
        return redir_invalid(redir_all)
    data = get_author_by_time(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_time.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genres/")
@html.route("/html/genres")
def html_genres_root():
    data = get_genres_list()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genres/<int:meta_id>")
def html_genres_meta(meta_id=None):
    meta_id = validate_genre_meta(str(meta_id))
    data = get_genres_list(meta_id)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genre/<gen_id>")
def html_genres_book(gen_id=None):
    gen_id = validate_genre(gen_id)
    if gen_id is None:
        return redir_invalid(redir_all)
    data = get_genre_books(gen_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genres/<gen_id>/<int:page>")
def html_genres_book_page(gen_id=None, page=0):
    gen_id = validate_genre(gen_id)
    if gen_id is None:
        return redir_invalid(redir_all)
    data = get_genre_books(gen_id, page)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zips", methods=['GET'])
def html_by_zips_root():
    data = get_zips_list()
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zip/<zip_name>", methods=['GET'])
def html_by_zip(zip_name=None):
    zip_name = validate_zip(zip_name)
    if zip_name is None:
        return redir_invalid(redir_all)
    data = get_zip_list(zip_name)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zip/<zip_name>/sequences")
def html_zip_sequences(zip_name=None):
    zip_name = validate_zip(zip_name)
    if zip_name is None:
        return redir_invalid(redir_all)
    data = get_zip_sequences(zip_name)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zipsequence/<zip_name>/<seq>")
def html_zip_sequence(zip_name=None, seq=None):
    zip_name = validate_zip(zip_name)
    if zip_name is None:
        return redir_invalid(redir_all)
    seq = validate_id(seq)
    if seq is None:
        return redir_invalid(redir_all)
    data = get_zip_sequence(zip_name, seq)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zip/<zip_name>/sequenceless")
@html.route("/html/zip/<zip_name>/sequenceless/<int:page>")
def html_zip_sequenceless(zip_name=None, page=0):
    zip_name = validate_zip(zip_name)
    if zip_name is None:
        return redir_invalid(redir_all)
    data = get_zip_sequenceless(zip_name, page)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/zip/<zip_name>/alphabet")
@html.route("/html/zip/<zip_name>/alphabet/<int:page>")
def html_zip_alphabet(zip_name=None, page=0):
    zip_name = validate_zip(zip_name)
    if zip_name is None:
        return redir_invalid(redir_all)
    data = get_zip_by_alphabet(zip_name, page)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/random-books")
@html.route("/html/random-books/<int:page>")
def html_random_books(zip_name=None, page=0):
    data = get_random_books()
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/random-sequences")
@html.route("/html/random-sequences/<int:page>")
def html_random_seqs(zip_name=None, page=0):
    data = get_random_seqs()
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search", methods=['GET'])
def html_search():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    data = get_search_main(s_term)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-authors", methods=['GET'])
def html_search_authors():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    data = get_search_authors(s_term)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-books", methods=['GET'])
def html_search_books():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    data = get_search_books(s_term)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-sequences", methods=['GET'])
def html_search_seqs():
    s_term = request.args.get('searchTerm')
    s_term = validate_search(s_term)
    data = get_search_seqs(s_term)
    if data is None or len(data) < 1:
        return redir_invalid(redir_all)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
