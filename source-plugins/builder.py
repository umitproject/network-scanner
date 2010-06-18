#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques
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

"""
Simple python script to replace update.sh
"""

import os
import sys
import glob
import os.path

cwd = os.getcwd()
root = os.path.dirname(cwd)
sys.path.insert(0, root)

from umit.core.Paths import Path
Path.set_umit_conf(os.path.split(sys.argv[0])[0])

plug_dir = os.path.join(Path.config_dir, "plugins")

sys.path.pop(0)
os.environ["PYTHONPATH"] = root

def build_in(dir_entry):
    os.chdir(os.path.join(cwd, dir_entry))

    if os.name =="nt":
        os.system("C:\\python25\\python.exe setup.py build_ext -c mingw32 install")
    else:
        os.system("python setup.py install")

    for plugin in glob.glob("*.ump"):
        dest = os.path.join(plug_dir, os.path.basename(plugin))
        if os.path.exists(dest):
            os.remove(dest)
        os.rename(plugin, dest)

    os.chdir(cwd)

if __name__ == "__main__":

    if len(sys.argv) == 2 and os.path.isdir(sys.argv[1]):
        print "[*] Building %s plugin ..." % sys.argv[1]

        build_in(sys.argv[1])
    elif len(sys.argv) == 2 and sys.argv[1].lower() == "--help":
        print "Usage: %s [plugin-dir]" % sys.argv[0]
    else:
        print "[*] Building and moving all plugins into %s ..." % plug_dir

        for dir_entry in os.listdir(cwd):
            if not os.path.isdir(dir_entry) or \
               not os.path.exists(os.path.join(dir_entry, "setup.py")):
                continue
            
            print "[*] Building plugin %s" % dir_entry
            build_in(dir_entry)
