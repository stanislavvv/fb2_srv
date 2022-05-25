# -*- coding: utf-8 -*-

from flask import redirect, Blueprint, Response, url_for, render_template, request
from .opds_seq import main_opds, get_sequences, get_books_in_seq
from .opds_auth import get_authors_list, get_author_list, get_author_sequences, get_author_sequence
from .opds_auth import get_author_sequenceless, get_author_by_alphabet, get_author_by_time
from .opds_genres import get_genres_list, get_genre_books
from .opds_search import get_search_main, get_search_authors, get_search_books

html = Blueprint("html", __name__, template_folder='templates')


@html.route("/", methods=['GET'])
def hello_world():
    location = url_for("html.html_root")
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
    data = get_sequences(seq)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/sequencebooks/<seq>", methods=['GET'])
def html_books_in_seq(seq=None):
    data = get_books_in_seq(seq)
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
    data = get_authors_list(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>", methods=['GET'])
def html_by_author(auth=None):
    data = get_author_list(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_main.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/sequences")
def html_author_sequences(auth=None):
    data = get_author_sequences(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_author_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/authorsequence/<auth>/<seq>")
def html_author_sequence(auth=None, seq=None):
    data = get_author_sequence(auth, seq)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/sequenceless")
def html_author_sequenceless(auth=None):
    data = get_author_sequenceless(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/alphabet")
def html_author_alphabet(auth=None):
    data = get_author_by_alphabet(auth)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/author/<auth>/time")
def html_author_time(auth=None):
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


@html.route("/html/genres/<gen_id>")
def html_genres_book(gen_id=None):
    data = get_genre_books(gen_id)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/genres/<gen_id>/<int:page>")
def html_genres_book_page(gen_id=None, page=0):
    data = get_genre_books(gen_id, page)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search", methods=['GET'])
def html_search():
    s_term = request.args.get('searchTerm')
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
    data = get_search_authors(s_term)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_root.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')


@html.route("/html/search-books", methods=['GET'])
def html_search_books():
    s_term = request.args.get('searchTerm')
    data = get_search_books(s_term)
    title = data['feed']['title']
    updated = data['feed']['updated']
    entry = data['feed']['entry']
    link = data['feed']['link']
    page = render_template('opds_sequence.html', title=title, updated=updated, link=link, entry=entry)
    return Response(page, mimetype='text/html')
