# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DBSQLITE = "data/fb_data.sqlite"
    GENRES_LIST = "genres.list"
    ZIPS = "data"
    TITLE = "Home opds directory"
    FB2_XSLT = 'fb2_to_html.xsl'
    APPLICATION_ROOT = ''
    PAGE_SIZE = 10


class TestConfig(Config):
    TESTING = True
    DEBUG = False
    DBSQLITE = "data/fb_data.sqlite"
    GENRES_LIST = "genres.list"
    ZIPS = "data"
    TITLE = "Home opds directory"
    FB2_XSLT = 'fb2_to_html.xsl'
    APPLICATION_ROOT = '/books'
    PAGE_SIZE = 10


class ProductionConfig(Config):
    DEBUG = False
    DBSQLITE = "data/fb_data.sqlite"
    GENRES_LIST = "genres.list"
    ZIPS = "data"
    TITLE = "Home opds directory"
    FB2_XSLT = 'fb2_to_html.xsl'
    APPLICATION_ROOT = '/books'
    PAGE_SIZE = 100


config = {"development": DevelopmentConfig, "test": TestConfig, "prod": ProductionConfig}

SELECTED_CONFIG = os.getenv("FLASK_ENV", "development")
