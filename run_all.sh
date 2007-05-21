# This will remove current database files or not, create valid databases,
# populate them and copy to the right place.

sh remove_dbs.sh
sh create_valid_db.sh
sh populate_db.sh
sh copy_db_to_tests.sh
