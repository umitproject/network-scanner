#!/bin/sh

old_pwd=`pwd`
script_dir=`pwd`/$0
script_dir=`dirname $script_dir`
cd $script_dir/../..

python setup.py sdist
mv dist/umit-0.9.4.tar.gz /usr/src/redhat/SOURCES
rmdir dist
rpmbuild -vv -bb umit.fedora.spec --clean

cd $old_pwd
