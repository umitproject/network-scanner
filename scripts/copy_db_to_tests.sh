#!/bin/sh

remove_test=1
database="testing.db"
testing="tests/db/schema-testing.db"
testing2="datahandler/schema-testing.db"

cp $database $testing
cp $database $testing2

echo "Copied $database to $testing."
echo "Copied $database to $testing2."

if [ "$remove_test" -ne 0 ] 
then
    rm $database
    echo "Removed $database."
fi
