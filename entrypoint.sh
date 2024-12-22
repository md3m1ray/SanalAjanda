#!/bin/sh

python manage.py makemigrations --noinput
python manage.py migrate -- run-syncdb --noinput

exec "$@"