database="testing.db"
testing="tests/db/schema-testing.db"
testing2="datahandler/schema-testing.db"

if [ -f $database ] 
then
    echo "Removing $database.."
    rm $database
fi

if [ -f $testing ] 
then
    echo "Removing $testing.."
    rm $testing
fi

if [ -f $testing2 ]
then
    echo "Removing $testing2.."
fi
