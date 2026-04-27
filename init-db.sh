#!/bin/bash
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTRGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE DATABASE auth_db;
EOSQL

