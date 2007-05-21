#!/bin/sh

remove_test=1
database="testing.db"
testing="tests/db/schema-testing.db"

cp $database $testing

echo "Copied $database to $testing."

if [ "$remove_test" -ne 0 ] 
then
    rm $database
    echo "Removed $database."
fi
