#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import re
import cPickle
import os.path

def create_os_dump(os_db, os_fingerprints, os_dump):
    os_dump = os.path.join("misc", os_dump)
    
    osd = {}
    os_db_file = open(os_db, "r")
    os_fingerprints_file = open(os_fingerprints, "r")

    osd.update(parse(os_db_file))
    osd.update(parse(os_fingerprints_file))

    print ">>> Creating %s file" % os_dump
    of = open(os_dump, "w")
    cPickle.dump(osd, of)
    of.close()


def parse(os_file):
    os_dict = {}
    os_db_splited = os_file.read().split("\n\n")

    r_fingerprint = re.compile("Fingerprint\s+(.*)")
    r_class = re.compile("Class\s+(.*)")

    for osd in os_db_splited:
        os_splited = osd.split("\n")

        osd = None
        osclass = None
            
        for o in os_splited[:5]:
            f = r_fingerprint.match(o)
            c = r_class.match(o)
            if f:
                osd = f.groups()[0]
            elif c:
                osclass = c.groups()[0]
                    
        if osd and osclass:
            try:
                os_dict[osclass]
            except:
                os_dict[osclass] = [osd]
            else:
                os_dict[osclass].append(osd)

    os_file.close()
    return os_dict


def load_dumped_os():
    of = open(os_dump)
    osd = cPickle.load(of)
    of.close()

    return osd

if __name__ == "__main__":
    os_db = os.path.join("utils", "nmap-os-db")
    os_fingerprints = os.path.join("utils", "nmap-os-fingerprints")
    os_dump = os.path.join("utils", "os_db.dmp")

    create_os_dump(os_db, os_fingerprints, os_dump)
