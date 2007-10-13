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
import os

from glob import glob

VERSION_FILE = os.path.join("share", "umit", "config", "umit_version")

def get_winpcap():
    windeps = os.path.join("install_scripts", "windows",
                           "win_dependencies", "winpcap*")
    return os.path.split(glob(windeps)[0])[1]

WINPCAP = get_winpcap()

# List of files to update:
# `base_dir`\umitCore\Paths.py

def update_setup(base_dir, version, revision):
    setup = os.path.join(base_dir, "setup.py")
    print ">>> Updating setup.py at %s" % setup
    sf = open(setup)
    setup_content = sf.read()
    sf.close()

    setup_content = re.sub("VERSION\s*=\s*os.environ.get\(\"UMIT_VERSION\", \"([\d\.]+)\"\)",
                           "VERSION = \"%s\"" % version,
                           setup_content)
    setup_content = re.sub("REVISION\s*=\s*os.environ.get\(\"UMIT_REVISION\", \"([\d\.]+)\"\)",
                           "REVISION = \"%s\"" % revision,
                           setup_content)
    setup_content = re.sub("SOURCE_PKG\s*=\s*(False)",
                           "SOURCE_PKG = True",
                           setup_content)

    sf = open(setup, "w")
    sf.write(setup_content)
    sf.close()

def update_umit_compiled(base_dir, version, revision):
    umit_compiled = os.path.join(base_dir, "umit_compiled.nsi")
    print ">>> Updating:", umit_compiled
    ucf = open(umit_compiled)
    ucompiled_content = ucf.read()
    ucf.close()

    ucompiled_content = re.sub("!define APPLICATION_VERSION \".+\"",
                               "!define APPLICATION_VERSION \"%s\"" % version,
                               ucompiled_content)
    ucompiled_content = re.sub("!define WINPCAP \".+\"",
                               "!define WINPCAP \"%s\"" % WINPCAP,
                               ucompiled_content)

    ucf = open(umit_compiled, "w")
    ucf.write(ucompiled_content)
    ucf.close()

def update_paths(base_dir, version, revision):
    paths = os.path.join(base_dir, "umitCore", "Paths.py")
    print ">>> Updating umitCore.Paths at %s" % paths
    pf = open(paths)
    paths_content = pf.read()
    pf.close()

    paths_content = re.sub("VERSION\s*=\s*environ.get\(\"UMIT_VERSION\", \"([\d\.]+)\"\)",
                           "VERSION = \"%s\"" % version,
                           paths_content)
    paths_content = re.sub("REVISION\s*=\s*environ.get\(\"UMIT_REVISION\", \"([\d\.]+)\"\)",
                           "REVISION = \"%s\"" % revision,
                           paths_content)

    pf = open(paths, "w")
    pf.write(paths_content)
    pf.close()

def update_umit_version(base_dir, version, revision):
    print ">>> Updating umit_version at", VERSION_FILE
    vf = open(VERSION_FILE, "wb")
    vf.write("\n".join([version, revision]))
    vf.close()
