#!/bin/bash -x

manage.py migrate -v3 --no-input
python manage.py runserver 0.0.0.0:8001
