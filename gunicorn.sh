#!/bin/bash

export FLASK_ENV=production
gunicorn3 --workers=4 'app:create_app()' --access-logfile -
