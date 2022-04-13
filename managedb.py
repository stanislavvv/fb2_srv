#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys

from app import create_app

def usage():
    print("Usage: managedb.py <command>")
    print("Commands:")
    print(" dropdb  -- remove database from disk", " NOT IMPLEMENTED")
    print(" cleandb -- clean database tables content", " NOT IMPLEMENTED")
    print(" newdb   -- [re]create database from scratch", " NOT IMPLEMENTED")
    print(" fillnew -- add new data to database", " NOT IMPLEMENTED")
    print(" fillall -- clean and refill data to database", " NOT IMPLEMENTED")


if __name__ == "__main__":
    app = create_app()
    #print(app.url_map)
    #app.run(host='0.0.0.0')
    if len(sys.argv) > 1:
        if sys.argv[1] == "dropdb":
            print("drop:", app.config['DBSQLITE'])
        elif sys.argv[1] == "cleandb":
            print("clean:", app.config['DBSQLITE'])
        elif sys.argv[1] == "newdb":
            print("newdb:", app.config['DBSQLITE'])
        elif sys.argv[1] == "fillnew":
            print("fillnew:", app.config['DBSQLITE'], app.config["ZIPS"])
        elif sys.argv[1] == "refillall":
            print("fillall:", app.config['DBSQLITE'], app.config["ZIPS"])
        else:
            usage()
    else:
        usage()
