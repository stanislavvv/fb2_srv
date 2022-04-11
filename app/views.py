# -*- coding: utf-8 -*-

# from flask import request, redirect, Blueprint, Response, url_for
from flask import redirect, Blueprint, Response, url_for
from .opds_seq import main_opds, get_sequences, get_books_in_seq
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
