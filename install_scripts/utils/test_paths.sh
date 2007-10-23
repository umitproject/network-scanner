#!/bin/sh

uninstall_umit
rm -rf ~/.umit
python setup.py install

echo ""
echo "####################################################################################"
echo ""

python /usr/lib/python2.4/site-packages/umitCore/Paths.py