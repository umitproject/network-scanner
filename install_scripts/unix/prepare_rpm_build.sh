#!/bin/sh

python setup.py sdist
mv dist/umit-0.9.4.tar.gz /usr/src/redhat/SOURCES
rmdir dist
rpmbuild -vv -bb umit.fedora.spec --clean
