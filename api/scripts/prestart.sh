#! /usr/bin/env bash

set -e
set -x

# Run migrations
alembic upgrade head

# Let the DB start
python app/pre_start.py

# Create initial data in DB
python app/initial_data.py
