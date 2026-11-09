#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Database migrations
python manage.py migrate

# Seed demonstration datasets
python seed_miriam_chiphaka.py
python seed_naffe.py
python seed_ten_farmers.py

# Collect static assets for WhiteNoise
python manage.py collectstatic --no-input

