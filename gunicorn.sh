#!/bin/bash

gunicorn3 -e FLASK_ENV=prod --workers=4 'app:create_app()' --access-logfile - --error-logfile -
