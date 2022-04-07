# -*- coding: utf-8 -*-

from flask import Flask
from flask import g

from .config import config, SELECTED_CONFIG
from .views import api

def create_app():
    app = Flask(__name__, static_url_path='/st')
    app.config.from_object(config[SELECTED_CONFIG])
    app.register_blueprint(api)
    return app
