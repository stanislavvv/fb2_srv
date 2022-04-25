# -*- coding: utf-8 -*-

from flask import Blueprint, Response, send_file
from .get_fb2 import fb2_out

# import json

dl = Blueprint("dl", __name__)


@dl.route("/fb2/<zip_file>/<filename>")
def fb2_download(zip_file=None, filename=None):
    data = fb2_out(zip_file, filename)
    print(zip_file, filename)
    if data is not None:
        return send_file(data, attachment_filename=filename, as_attachment=True)
    else:
        return Response("Book not found", status=404)
