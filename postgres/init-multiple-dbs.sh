#!/bin/bash
set -e

echo "Creating databases if they don't exist..."

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres <<-EOSQL
    CREATE DATABASE metabaseappdb;
EOSQL
