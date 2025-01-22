#!/bin/bash
echo "BUILD START"

# Install required dependencies
python3.9 -m pip install requirements.txt
echo "Collectstatic.."
python3.9 manage.py collectstatic --noinput --clear
echo "BUILD END"
