#!/usr/bin/env python
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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

import sys
import os
import os.path
import re

from distutils.core import setup
from distutils.command.install import install
from distutils.command.sdist import sdist
from distutils.command.build import build
from distutils import log, dir_util

from glob import glob
from stat import *

from umit.core.Version import VERSION
from utils import msgfmt

BIN_DIRNAME = 'bin'

# Directories for POSIX operating systems
# These are created after a "install" or "py2exe" command
# These directories are relative to the installation or dist directory
# Ex: python setup.py install --prefix=/tmp/umit
# Will create the directory /tmp/umit with the following directories
pixmaps_dir = os.path.join('share', 'pixmaps', 'umit')
icons_dir = os.path.join('share', 'icons', 'umit')
locale_dir = os.path.join('share', 'locale')
config_dir = os.path.join('share', 'umit', 'config')
docs_dir = os.path.join('share', 'doc', 'umit')
misc_dir = os.path.join('share', 'umit', 'misc')
sql_dir = os.path.join('share', 'umit', 'sql')

def extension_find(result, dirname, fnames, suffix):
    files = []
    for f in fnames:
        p = os.path.join(dirname, f)
        if os.path.isfile(p) and f.endswith(suffix):
            files.append(p)

    if files:
        result.append((dirname, files))

def mo_find(result, dirname, fnames):
    return extension_find(result, dirname, fnames, ".mo")

def po_find(result, dirname, fnames):
    return extension_find(result, dirname, fnames, ".po")


###############################################################################
# Installation variables

svg = glob(os.path.join('share', 'pixmaps', '*.svg'))
data_files = [
        (pixmaps_dir,
            glob(os.path.join(pixmaps_dir, '*.svg')) +
            glob(os.path.join(pixmaps_dir, '*.png')) +
            glob(os.path.join(pixmaps_dir, '*.xpm')) +
            glob(os.path.join(pixmaps_dir, 'umit.o*'))),

        (config_dir,
            [os.path.join(config_dir, 'umit.conf')] +
            [os.path.join(config_dir, 'scan_profile.usp')] +
            [os.path.join(config_dir, 'umit_version')] +
            [os.path.join(config_dir, 'umitng.db')] +
            [os.path.join(config_dir, 'timeline-settings.conf')] +
            [os.path.join(config_dir, 'tl_colors_evt_std.conf')] +
            [os.path.join(config_dir, 'scheduler-schemas.conf')] +
            [os.path.join(config_dir, 'scheduler-profiles.conf')] +
            [os.path.join(config_dir, 'scheduler.log')] +
            [os.path.join(config_dir, 'smtp-schemas.conf')] +
            glob(os.path.join(config_dir, '*.xml'))+
            glob(os.path.join(config_dir, '*.txt'))),

        # umitDB SQL
        (sql_dir, glob(os.path.join(sql_dir, '*.sql'))),

        (misc_dir, glob(os.path.join(misc_dir, '*.dmp'))),

        # Radialnet
        (os.path.join(pixmaps_dir, 'radialnet', 'application'),
            glob(os.path.join(pixmaps_dir, 'radialnet', 'application',
                '*.png'))),
        (os.path.join(pixmaps_dir, 'radialnet', 'icons'),
            glob(os.path.join(pixmaps_dir, 'radialnet', 'icons','*.png'))),

        # Network Inventory
        (os.path.join(pixmaps_dir, 'networkinventory'),
            glob(os.path.join(pixmaps_dir, 'networkinventory', '*.png'))),

        # InterfaceEditor
        (os.path.join(pixmaps_dir, 'uie'),
            glob(os.path.join(pixmaps_dir, 'uie', '*.png'))),

        (icons_dir,
            glob(os.path.join('share', 'icons', 'umit', '*.ico')) +
            glob(os.path.join('share', 'icons', 'umit', '*.png'))),

        (docs_dir,
            glob(os.path.join(docs_dir, '*.html')) +
            glob(os.path.join(docs_dir, 'comparing_results', '*.xml')) +
            glob(os.path.join(docs_dir, 'profile_editor', '*.xml')) +
            glob(os.path.join(docs_dir, 'scanning', '*.xml')) +
            glob(os.path.join(docs_dir, 'searching', '*.xml')) +
            glob(os.path.join(docs_dir, 'wizard', '*.xml')) +
            glob(os.path.join(docs_dir, 'scheduler', '*.xml')) +
            glob(os.path.join(docs_dir, 'smtpsetup', '*.xml')) +
            glob(os.path.join(docs_dir, 'screenshots', '*.png')))]

# Add i18n files to data_files list
os.path.walk(locale_dir, mo_find, data_files)


##############################################################################
# Distutils subclasses

class umit_build(build):

    def delete_mo_files(self):
        """ Remove *.mo files """
        tmp = []
        os.path.walk(locale_dir, mo_find, tmp)
        for (path, t) in tmp:
            os.remove(t[0])

    def build_mo_files(self):
        """Build mo files from po and put it into LC_MESSAGES """
        tmp = []
        os.path.walk(locale_dir, po_find, tmp)
        for (path, t) in tmp:
            full_path = os.path.join(path , "LC_MESSAGES", "umit.mo")
            self.mkpath(os.path.dirname(full_path))
            self.announce("Compiling %s -> %s" % (t[0],full_path))
            msgfmt.make(t[0], full_path, False)
        # like guess
        os.path.walk(locale_dir, mo_find, data_files)

    def run(self):
        self.delete_mo_files()
        self.build_mo_files()
        build.run(self)


class umit_install(install):

    def run(self):
        # Add i18n files to data_files list
        os.path.walk(locale_dir, mo_find, data_files)
        install.run(self)

        self.set_perms()
        self.set_modules_path()
        self.fix_paths()
        self.create_uninstaller()
        self.finish_banner()

    def create_uninstaller(self):
        uninstaller_filename = os.path.join(
                self.install_scripts, "uninstall_umit")
        uninstaller = """#!/usr/bin/env python
import os, os.path, sys

print
print '%(line)s Uninstall Umit %(version)s %(line)s'
print

answer = raw_input('Are you sure that you want to completly uninstall \
Umit %(version)s? (yes/no) ')

if answer != 'yes' and answer != 'y':
    sys.exit(0)

print
print '%(line)s Uninstalling Umit %(version)s... %(line)s'
print
""" % {'version':VERSION, 'line':'-'*10}

        for output in self.get_outputs():
            uninstaller += "print 'Removing %s...'\n" % output
            uninstaller += "if os.path.exists('%s'): os.remove('%s')\n" % \
                        (output, output)

        uninstaller += "print 'Removing uninstaller itself...'\n"
        uninstaller += "os.remove('%s')\n" % uninstaller_filename

        uninstaller_file = open(uninstaller_filename, 'w')
        uninstaller_file.write(uninstaller)
        uninstaller_file.close()

        # Set exec bit for uninstaller
        mode = ((os.stat(uninstaller_filename)[ST_MODE]) | 0555) & 07777
        os.chmod(uninstaller_filename, mode)

    def set_modules_path(self):
        umit = os.path.join(self.install_scripts, "umit")
        modules = self.install_lib

        re_sys = re.compile("^import sys$")

        ufile = open(umit, "r")
        ucontent = ufile.readlines()
        ufile.close()

        uline = None
        for line in xrange(len(ucontent)):
            if re_sys.match(ucontent[line]):
                uline = line + 1
                break

        ucontent.insert(uline, "sys.path.insert(0,'%s')\n" % modules )

        ufile = open(umit, "w")
        ufile.writelines(ucontent)
        ufile.close()

    def set_perms(self):
        re_bin = re.compile("(bin)")
        for output in self.get_outputs():
            if re_bin.findall(output):
                continue

            if os.path.isdir(output):
                os.chmod(output, S_IRWXU | \
                                 S_IRGRP | \
                                 S_IXGRP | \
                                 S_IROTH | \
                                 S_IXOTH)
            else:
                os.chmod(output, S_IRWXU | \
                                 S_IRGRP | \
                                 S_IROTH)

    def fix_paths(self):
        interesting_paths = {"CONFIG_DIR":config_dir,
                             "DOCS_DIR":docs_dir,
                             "LOCALE_DIR":locale_dir,
                             "MISC_DIR":misc_dir,
                             "PIXMAPS_DIR":pixmaps_dir,
                             "ICONS_DIR":icons_dir}

        pcontent = ""
        paths_file = os.path.join("umit", "core", "BasePaths.py")
        installed_files = self.get_outputs()

        # Finding where the Paths.py file was installed.
        for f in installed_files:
            if re.findall("(%s)" % re.escape(paths_file), f):
                paths_file = f
                pf = open(paths_file)
                pcontent = pf.read()
                pf.close()
                break

        for path in interesting_paths:
            for f in installed_files:
                result = re.findall("(.*%s)" %\
                                    re.escape(interesting_paths[path]),
                                    f)
                if len(result) == 1:
                    result = result[0]
                    pcontent = re.sub("%s\s+=\s+.+" % path,
                                      "%s = \"%s\"" % (path, result),
                                      pcontent)
                    break

        pf = open(paths_file, "w")
        pf.write(pcontent)
        pf.close()

    def finish_banner(self):
        print
        print "%s Thanks for using Umit %s %s" % \
              ("#"*10, VERSION, "#"*10)
        print


class umit_sdist(sdist):

    def read_manifest_no_mo(self):
        """Read Manifest without mo file."""
        for line in open(self.manifest):
            if not line:
                break

            if line[-1] == '\n':
                line = line[:-1]
            if line.find('umit.mo') != -1:
                self.filelist.files.remove(line)

    def run(self):
        from distutils.filelist import FileList
        self.keep_temp = 1
        #Rewrite: sdist.run(self)
        self.manifest = "MANIFEST"
        self.filelist = FileList()
        self.check_metadata()
        self.get_file_list()
        ## Exclude mo files:
        self.read_manifest_no_mo()
        if self.manifest_only:
            return
        self.make_distribution()

        self.finish_banner()

    def finish_banner(self):
        print
        print "%s The packages for Umit %s are in ./dist %s" % \
              ("#" * 10, VERSION, "#" * 10)
        print


##################### Umit banner ########################
print
print "%s Umit for Linux %s %s" % ("#" * 10, VERSION, "#" * 10)
print
##########################################################

setup(name = 'umit',
      license = 'GNU GPL (version 2 or later)',
      url = 'http://www.umitproject.org',
      download_url = 'http://www.umitproject.org',
      author = 'Adriano Monteiro & Cleber Rodrigues',
      author_email = 'adriano@umitproject.org, cleber@globalred.com.br',
      maintainer = 'Adriano Monteiro',
      maintainer_email = 'adriano@gmail.com',
      description = """Umit is a network scanning frontend, developed in \
Python and GTK and was started with the sponsoring of Google's Summer \
of Code.""",
      long_description = """The project goal is to develop a network scanning \
frontend that is really useful for advanced users and easy to be used by \
newbies. With Umit, a network admin could create scan profiles for faster and \
easier network scanning or even compare scan results to easily see any \
changes. A regular user will also be able to construct powerful scans with \
Umit command creator wizards.""",
      version = VERSION,
      scripts = [
          os.path.join(BIN_DIRNAME, 'umit'),
          os.path.join(BIN_DIRNAME, 'umit_scheduler.py')],
      packages = [
          'umit', 'umit.core', 'umit.core.radialnet', 'umit.db',
          'umit.gui', 'umit.gui.radialnet', 'umit.interfaceeditor',
          'umit.interfaceeditor.selectborder', 'umit.inventory',
          'umit.plugin', 'higwidgets', 'utils'],
      data_files = data_files,
      cmdclass = {
          "install": umit_install,
          "build": umit_build,
          "sdist": umit_sdist})
