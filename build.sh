#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install python dependencies
pip install -r requirements.txt

# Database migrations
python manage.py migrate

# Seed Miriam Chiphaka 10-year realistic demonstration dataset
python seed_miriam_chiphaka.py

# Collect static assets for WhiteNoise
python manage.py collectstatic --no-input

