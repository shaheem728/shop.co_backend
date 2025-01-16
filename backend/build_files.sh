#!/bin/bash
echo "BUILD START"

echo "Installing dependencies..."
python3.12 pip install -r requirements.txt || { echo "Dependency installation failed"; exit 1; }

echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput --clear || { echo "Static files collection failed"; exit 1; }

echo "BUILD END"
