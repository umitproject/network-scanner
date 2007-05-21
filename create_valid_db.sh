#!/bin/sh

# Run this from this dir, thanks.

database="testing.db"
dbschema="sqlite-schema.sql"
dbtriggers_insert="sqlite-insert-triggers.sql"
dbtriggers_update="sqlite-update-triggers.sql"

echo "Creating $database.."
sqlite3 $database < $dbschema
sqlite3 $database < $dbtriggers_insert
sqlite3 $database < $dbtriggers_update

echo "Database $database created."
