#!/bin/sh -e

echo
echo "########################"
echo "# Umit Source Packages #"
echo "########################"
echo

old_pwd=`pwd`
script_dir=`pwd`/$0
script_dir=`dirname $script_dir`
cd $script_dir/..

echo "Updating/Creating dumped operating system list..."
python install_scripts/utils/create_os_list.py

echo "Updating/Creating dumped services list..."
python install_scripts/utils/create_services_dump.py

echo "Removing some unused files..."
bash install_scripts/utils/remove_unused_files.sh

echo "Starting setup.py..."
python setup.py sdist --formats=gztar,zip,bztar
rm MANIFEST

cd $old_pwd
