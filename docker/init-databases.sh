#!/bin/sh
set -eu

for db in "$MAIN_DB_USERS_NAME" "$MAIN_DB_INFORMATICS_NAME" "$MAIN_DB_ARCHIVE_NAME"; do
  psql -v ON_ERROR_STOP=1 \
    --username "$POSTGRES_USER" \
    --dbname postgres \
    --set=db="$db" <<'EOSQL'
SELECT format('CREATE DATABASE %I', :'db')
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = :'db'
)\gexec
EOSQL
done
