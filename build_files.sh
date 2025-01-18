#!/bin/bash
echo "BUILD START"
python3.9 -m pip install -r requirements.txt
echo "Collectstatic.."
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"
