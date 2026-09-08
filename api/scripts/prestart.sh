#!/usr/bin/env bash

set -euo pipefail

alembic upgrade head
python app/pre_start.py
python app/initial_data.py
