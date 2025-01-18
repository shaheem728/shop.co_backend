#!/bin/bash
echo "BUILD START"
python3 -m ensurepip --upgrade
pip install --no-cache-dir -r requirements.txt
echo "Collectstatic.."
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"
