#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
#         David Fifield <david@bamsoftware.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

# This program reads Nmap OS fingerprint database files and writes their
# contents in preprocessed pickled form to other files. One of the output files,
# os_db.dmp, contains a dict mapping OS classes to lists of OS names. The other
# file, os_classification.dmp, contains a list of tuples whose first element is
# a condensed OS class and whose second element is the OS class separated with
# spaces instead of "|"s.

import cPickle
import os.path
import re
import sys

NMAP_OS_FINGERPRINTS = os.path.join("install_scripts", "utils", "nmap-os-fingerprints")
NMAP_OS_DB = os.path.join("install_scripts", "utils", "nmap-os-db")

OS_DB_DUMP = os.path.join("share", "umit", "misc", "os_db.dmp")
OS_CLASSIFICATION_DUMP = os.path.join("share", "umit", "misc", "os_classification.dmp")

r_fingerprint = re.compile("^Fingerprint\s+(.*)")
r_class = re.compile("^Class\s+(.*)")

def parse(os_file):
    """Return a dict that maps OS classes to lists of OS names that use that
    class."""
    os_dict = {}
    for fp in os_file.read().split("\n\n"):
        os_name = None
        for line in fp.split("\n"):
            m = r_fingerprint.match(line)
            if m:
                os_name = m.groups()[0]
                continue
            m = r_class.match(line)
            if m and os_name:
                os_class = m.groups()[0]
                l = os_dict.setdefault(os_class, [])
                if os_name not in l:
                    l.append(os_name)
    return os_dict

def write_os_db_dump(osd, file_name):
    f = open(file_name, "wb")
    try:
        cPickle.dump(osd, f)
    finally:
        f.close()

def write_os_classification_dump(osd, file_name):
    f = open(file_name, "wb")
    try:
        os_classes = osd.keys()
        os_classes.sort(lambda a, b: cmp(a.lower(), b.lower()))
        pairs = []
        for os_class in os_classes:
            # Split up the class.
            parts = [x.strip() for x in os_class.split("|")]
            # The first part is joined with "|".
            os_class = "|".join(parts)
            # The second part is joined with " " with empty parts removed.
            stripped = " ".join([x for x in parts if x != ""])
            pairs.append((os_class, stripped))
        cPickle.dump(pairs, f)
    finally:
        f.close()

def load_dumped_os():
    f = open(os_dump, "rb")
    osd = cPickle.load(f)
    f.close()

    return osd

if __name__ == "__main__":
    osd = {}
    for file_name in (NMAP_OS_FINGERPRINTS, NMAP_OS_DB):
        try:
            f = open(file_name, "r")
        except IOError:
            print >> sys.stderr, """\
Can't open %s for reading.
This script (%s) must be run from the root of a
Umit distribution.""" % (file_name, sys.argv[0])
            sys.exit(1)
        osd.update(parse(f))
        f.close()

    if len(osd) == 0:
        print >> sys.stderr, """\
Something's wrong. No fingerprints were found by %s.""" % sys.argv[0]
        sys.exit(1)

    print ">>> Writing OS DB dump to %s." % OS_DB_DUMP
    write_os_db_dump(osd, OS_DB_DUMP)
    print ">>> Writing OS classification dump to %s." % OS_CLASSIFICATION_DUMP
    write_os_classification_dump(osd, OS_CLASSIFICATION_DUMP)
