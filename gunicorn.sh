#!/bin/bash

export FLASK_ENV=prod
gunicorn3 --workers=4 'app:create_app()' --access-logfile -
