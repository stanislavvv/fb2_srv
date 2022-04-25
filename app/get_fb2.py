# -*- coding: utf-8 -*-

import os
import zipfile
import xmltodict
from flask import current_app


def fb2_out(zip_file, filename):
    zipdir = current_app.config['ZIPS']
    zippath = zipdir + "/" + zip_file
    try:
        data = ""
        with ZipFile(zippath) as myzip:
            with myzip.open(filename) as myfile:
                data = myfile.read()
        return data
    except:
        return None
