#!/bin/bash
echo "BUILD START"

echo "Installing dependencies..."
pip install -r requirements.txt || { echo "Dependency installation failed"; exit 1; }

echo "Running migrations..."
python3.12 manage.py makemigrations --noinput || { echo "Migrations failed"; exit 1; }
python3.12 manage.py migrate --noinput || { echo "Migration application failed"; exit 1; }

echo "Collecting static files..."
python3.12 manage.py collectstatic --noinput --clear || { echo "Static file collection failed"; exit 1; }

echo "BUILD END"
