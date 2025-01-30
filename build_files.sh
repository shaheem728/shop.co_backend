#!/bin/bash
echo "BUILD START"
# Install pip if not already installed
python3 -m ensurepip --upgrade
python3 -m pip install --upgrade pip
# Install required dependencies
python3 -m pip install -r requirements.txt
echo "Collectstatic.."
python3 manage.py collectstatic --noinput 
echo "BUILD END"