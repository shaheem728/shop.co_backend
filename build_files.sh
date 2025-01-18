#!/bin/bash
echo "BUILD START"
# Install pip if not already installed
python3.12 -m ensurepip --upgrade
python3.12 -m pip install --upgrade pip
# Install required dependencies
python3.12 -m pip install --no-cache-dir -r requirements.txt
echo "Collectstatic.."
python3.12 manage.py collectstatic --noinput --clear
echo "BUILD END"
