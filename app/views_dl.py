# -*- coding: utf-8 -*-

from flask import Blueprint, Response, send_file
from .get_fb2 import fb2_out, html_out

# import json

dl = Blueprint("dl", __name__)


@dl.route("/fb2/<zip_file>/<filename>")
def fb2_download(zip_file=None, filename=None):
    data = fb2_out(zip_file, filename)
    if data is not None:
        return send_file(data, attachment_filename=filename, as_attachment=True)
    else:
        return Response("Book not found", status=404)


@dl.route("/read/<zip_file>/<filename>")
def fb2_read(zip_file=None, filename=None):
    data = html_out(zip_file, filename)
    if data is not None:
        return Response(data, mimetype='text/html')
    else:
        return Response("Book not found", status=404)
