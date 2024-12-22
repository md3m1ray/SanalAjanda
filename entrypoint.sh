#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate --run-syncdb --noinput
python manage.py loaddata data.json

exec "$@"