# -*- coding: utf-8 -*-

from flask import request, redirect, json, jsonify, Blueprint, Response, url_for
api = Blueprint("api", __name__)


@api.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

@api.route("/st", methods=['GET'])
@api.route("/st/", methods=['GET'])
def static_root():
    location = url_for('static', filename='index.html')
    code = 301
    return redirect(location, code, Response = None)
