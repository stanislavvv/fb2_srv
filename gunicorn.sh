#!/bin/bash

gunicorn3 --workers=4 'app:create_app()' --access-logfile -
