#!/usr/bin/env python
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Cleber Rodrigues <cleber.gnu@gmail.com>
#                           <cleber@globalred.com.br>
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

import os
import os.path

from setuptools import setup
from glob import glob

from umitCore.Version import VERSION

# Directories for POSIX operating systems
# These are created after a "install" or "py2exe" command
# These directories are relative to the installation or dist directory
# Ex: python setup.py install --prefix=/tmp/umit
# Will create the directory /tmp/umit with the following directories
pixmaps_dir = os.path.join('share', 'pixmaps')
icons_dir = os.path.join('share', 'icons')
locale_dir = os.path.join('share', 'umit', 'locale')
config_dir = os.path.join('share', 'umit', 'config')
docs_dir = os.path.join('share', 'umit', 'docs')
misc_dir = os.path.join('share', 'umit', 'misc')


def mo_find(result, dirname, fnames):
    files = []
    for f in fnames:
        p = os.path.join(dirname, f)
        if os.path.isfile(p) and f.endswith(".mo"):
            files.append(p)
        
    if files:
        result.append((dirname, files))

data_files = [ (pixmaps_dir, glob(os.path.join(pixmaps_dir, '*.svg')) +
                             glob(os.path.join(pixmaps_dir, '*.png')) +
                             glob(os.path.join(pixmaps_dir, 'umit.o*'))),

               (config_dir, [os.path.join(config_dir, 'umit.conf')] +
                            [os.path.join(config_dir, 'scan_profile.usp')] +
                            [os.path.join(config_dir, 'umit_version')] +
                            glob(os.path.join(config_dir, '*.xml'))+
                            glob(os.path.join(config_dir, '*.txt'))),

               (misc_dir, glob(os.path.join(misc_dir, '*.dmp'))), 

               (icons_dir, glob(os.path.join('share', 'icons', '*.ico'))+
                           glob(os.path.join('share', 'icons', '*.png'))),

               (docs_dir, glob(os.path.join(docs_dir, '*.html'))+
                          glob(os.path.join(docs_dir,
                                            'comparing_results', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'profile_editor', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'scanning', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'searching', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'wizard', '*.xml'))+
                          glob(os.path.join(docs_dir,
                                            'screenshots', '*.png')))]

# Add i18n files to data_files list
os.path.walk(locale_dir, mo_find, data_files)

##################### Umit banner ########################
print
print "%s Umit %s %s" % ("#"*10, VERSION, "#"*10)
print
##########################################################

setup(name = 'umit',
      license = 'GNU GPL (version 2 or later)',
      url = 'http://www.umitproject.org',
      download_url = 'http://www.umitproject.org',
      author = 'Adriano Monteiro & Cleber Rodrigues',
      author_email = 'adriano@umitproject.org, cleber@globalred.com.br',
      maintainer = 'Adriano Monteiro',
      maintainer_email = 'adriano@umitproject.org',
      description = """Umit is a network scanning frontend, developed in \
Python and GTK and was started with the sponsoring of Google's Summer of \
Code.""",
      long_description = """The project goal is to develop a network scanning \
frontend that is really useful for advanced users and easy to be used by \
newbies. With Umit, a network admin could create scan profiles for faster and \
easier network scanning or even compare scan results to easily see any \
changes. A regular user will also be able to construct powerful scans with \
Umit command creator wizards.""",
      version = VERSION,
      scripts = ['umit.py'],
      app = ["umit.py"],
      packages = ['', 'umitCore', 'umitGUI', 'higwidgets'],
      data_files = data_files,
      options=dict(py2app=dict(argv_emulation=True,
                               compressed=True)),
      setup_requires=["py2app"])