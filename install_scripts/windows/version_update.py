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

import os.path
import re
import os

def umit_version():
    return open(os.path.join("share", "umit", "config", "umit_version")).read()

def umit_revision():
    svn = os.system("svn info --xml")
    # I know that using regex to catch the revision in an XML may seem dull,
    # but it's the easier way to do that here
    return re.findall("revision=\"(\d+)\"", svn)[0]

VERSION = umit_version()
REVISION = umit_revision()

print "Updating some files with the current Umit version and revision..."
print "VERSION:", VERSION
print "REVISION:", REVISION