# -*- coding: utf-8 -*-

from flask import Flask
from .config import config, SELECTED_CONFIG
from .views import api
from .views_html import html
from .views_dl import dl
from .get_fb2 import init_xslt


def create_app():
    global xslt
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(api)
    app.register_blueprint(html)
    app.register_blueprint(dl)
    xslt = init_xslt(app.config['FB2_XSLT'])
    return app
