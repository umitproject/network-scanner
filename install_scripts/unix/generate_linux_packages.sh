#!/bin/bash

echo
echo "########################"
echo "# Umit Source Packages #"
echo "########################"
echo

echo "Updating version and revision numbers..."
python install_scripts/utils/version_update.py

echo "Generating the splash image with new version and revision..."
python install_scripts/utils/add_splash_version.py

echo "Updating/Creating dumped operating system list..."
python install_scripts/utils/create_os_list.py

echo "Updating/Creating dumped services list..."
python install_scripts/utils/create_services_dump.py

echo "Updating/Creating operating system classification list..."
python install_scripts/utils/generate_classification.py

echo "Removing some unused files..."
bash install_scripts/utils/remove_unused_files.sh

echo "Starting setup.py..."
cp install_scripts/unix/setup.py .
cp install_scripts/unix/MANIFEST.in .
python setup.py sdist --formats=gztar,zip,bztar
rm setup.py MANIFEST.in MANIFEST