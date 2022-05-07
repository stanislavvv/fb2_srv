#!/bin/bash

gunicorn --workers=4 'app:create_app()' --access-logfile -
