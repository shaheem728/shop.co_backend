#!/bin/bash
echo "BUILD START"
python3.9 pip install -r requirements.txt
echo "make migrations"
python3.9 manage.py makemikrations
echo "migrate"
python3.9 manage.py migrate
echo "collectstatic"
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"
