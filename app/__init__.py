# -*- coding: utf-8 -*-

from flask import Flask
from .config import config, SELECTED_CONFIG
from .views import api
from .views_html import html
from .views_dl import dl


def create_app():
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(api)
    app.register_blueprint(html)
    app.register_blueprint(dl)
    return app
