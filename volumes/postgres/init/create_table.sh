#!/bin/sh
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_USER" <<-EOSQL
    CREATE DATABASE ${POSTGRES_USER}_development;
    CREATE DATABASE ${POSTGRES_USER}_test;
    CREATE DATABASE ${POSTGRES_USER}_production;
EOSQL
