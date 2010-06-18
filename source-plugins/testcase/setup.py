#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Adriano Monteiro Marques
#
# Author: Francesco Piccinno <stack.box@gmail.com>
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

import os
import sys
import math
import random

try:
    import hashlib as md5
except ImportError:
    import md5

from base64 import b64encode
from glob import glob
from umit.plugin.Containers import setup

if os.name == 'nt':
    print "Unable to create testcase plugin under windows."
    sys.exit(0)

randStr = lambda n: b64encode(os.urandom(int(math.ceil(0.75*n))),'-_')[:n]

os.system('rm -rf testfiles/*')

# Let's create our directories
top_ndir = random.randint(1, 10)
dep_ndir = random.randint(1, 10)

paths = []

for i in xrange(top_ndir):
    path = ""
    for x in xrange(dep_ndir):
        path = os.path.join(path, randStr(10))
    paths.append(path)

digest_list = []

for path in paths:
    dir = os.path.dirname(path)
    os.system('mkdir -p testfiles/%s' % dir)
    
    # Fill the file
    content_len = random.randint(1, 2000)
    content = randStr(content_len)
    f = open('testfiles/%s' % path, 'wb')
    f.write(content)
    f.close()

    hexdigest = md5.md5()
    hexdigest.update(content)
    hexdigest = hexdigest.hexdigest()

    digest_list.append((path, hexdigest))

# Now lets' generate our code
autogencode = """
try:
    import hashlib as md5
except ImportError:
    import md5

class TestAutoGen:
    DIGEST_LIST = $fuffa$
    def hexdigest(self, path):
        m = md5.md5()
        f = open(path)
        m.update(f.read())
        f.close()
        return m.hexdigest()

    def get_digest(self, ofile):
        for idx in xrange(len(self.DIGEST_LIST)):
            if ofile.endswith(self.DIGEST_LIST[idx][0]):
                dig = self.DIGEST_LIST[idx][1]
                del self.DIGEST_LIST[idx]
                return dig
            
    def run(self, reader):
        lst = reader.extract_dir('data/test/')

        if len(lst) != len(self.DIGEST_LIST):
            return False, "There are some file missing."
        
        for ofile in lst:
            digest = self.get_digest(ofile)
            if not digest:
                return False, "Digest not present for %s %s" % (ofile, self.DIGEST_LIST)
            cdigest = self.hexdigest(ofile)
            if cdigest != digest:
                return False, "MD5 verification failed on %s - (digest is %s while it should be %s)" % (ofile, cdigest, digest)

        return (True, "Wooo! Awesome! test passed :)")
"""

f = open('sources/test/autogen.py', 'w')
f.write(autogencode.replace('$fuffa$', str(digest_list)))
f.close()

data_files = []

for file in glob('testfiles%s' % ('/*' * dep_ndir)):
    data_files.append(('data/test%s' % os.path.dirname(file)[9:], [file]))

setup(
    name='TestCase',
    version='1.0',
    author=['Francesco Piccinno'],
    license=['GPL'],
    copyright=['(C) 2009 Adriano Monteiro Marques'],
    url='http://blog.archpwn.org',
    scripts=['sources/main.py'],
    start_file="main",
    data_files=[('data', ['dist/logo.png']), ] + data_files,
    description='Testcase plugin',
    package_dir={'test' : 'sources/test'},
    packages=['test'],
    output='TestCase.ump'
)
