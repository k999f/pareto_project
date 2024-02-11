#!/bin/bash

set -e
export PGPASSWORD=$POSTGRES_PASSWORD;
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  CREATE USER $AUTH_USER WITH PASSWORD '$AUTH_PASS';
  CREATE USER $ADMIN_USER WITH PASSWORD '$ADMIN_PASS';
  CREATE USER $CLIENT_USER WITH PASSWORD '$CLIENT_PASS';
  CREATE DATABASE $DB_NAME;
  GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $ADMIN_USER;
EOSQL
psql -U $ADMIN_USER $DB_NAME < /docker-entrypoint-initdb.d/db.sql
psql -v ON_ERROR_STOP=1 --username "$ADMIN_USER" --dbname "$DB_NAME" <<-EOSQL
  GRANT SELECT, INSERT                 ON users                          TO $AUTH_USER;
  GRANT USAGE                          ON ALL SEQUENCES IN SCHEMA public TO $AUTH_USER;
  GRANT SELECT, INSERT, UPDATE, DELETE ON analysis                       TO $CLIENT_USER;
  GRANT SELECT, INSERT, UPDATE, DELETE ON calculation                    TO $CLIENT_USER;
  GRANT SELECT, INSERT, UPDATE, DELETE ON estimation                     TO $CLIENT_USER;
  GRANT SELECT, INSERT, UPDATE, DELETE ON project                        TO $CLIENT_USER;
  GRANT SELECT                         ON algorythm                      TO $CLIENT_USER;
  GRANT SELECT                         ON indicator                      TO $CLIENT_USER;
  GRANT SELECT, INSERT, UPDATE, DELETE ON task                           TO $CLIENT_USER;
  GRANT SELECT, INSERT, DELETE         ON tasks_in_analysis              TO $CLIENT_USER;
  GRANT USAGE, SELECT                  ON ALL SEQUENCES IN SCHEMA public TO $CLIENT_USER;
EOSQL
