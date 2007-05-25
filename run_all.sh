# This will remove current database files or not, create valid databases,
# populate them and copy to the right place.

sdir="scripts"

sh $sdir/remove_dbs.sh
sh $sdir/create_valid_db.sh
sh $sdir/copy_db_to_tests.sh
