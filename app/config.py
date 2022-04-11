# -*- coding: utf-8 -*-

import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DBSQLITE = "fb_data.sqlite"
    ZIPS = "data"
    TITLE = "Home opds directory"


class TestConfig(Config):
    TESTING = True
    DEBUG = False
    DBSQLITE = "fb_data.sqlite"
    ZIPS = "data"
    TITLE = "Home opds directory"


class ProductionConfig(Config):
    DEBUG = False
    DBSQLITE = "fb_data.sqlite"
    ZIPS = "data"
    TITLE = "Home opds directory"


config = {"development": DevelopmentConfig, "test": TestConfig, "prod": ProductionConfig}

SELECTED_CONFIG = os.getenv("FLASK_ENV", "development")
