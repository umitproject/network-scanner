#!/bin/sh

# Run this from this dir, thanks.

database="testing.db"
dbschema="sql/sqlite-schema.sql"
dbtriggers_insert="sql/sqlite-insert-triggers.sql"
dbtriggers_update="sql/sqlite-update-triggers.sql"

echo "Creating $database.."
sqlite3 $database < $dbschema
sqlite3 $database < $dbtriggers_insert
sqlite3 $database < $dbtriggers_update

echo "Database $database created."
