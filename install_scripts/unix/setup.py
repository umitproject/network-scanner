#!/usr/bin/env python
# Copyright (C) 2005 Insecure.Com LLC.
#
# Authors: Adriano Monteiro Marques <py.adriano@gmail.com>
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

import sys
import os
import os.path
import re

from distutils.core import setup
from distutils.command.install import install
from distutils.command.sdist import sdist
from distutils import log, dir_util

from glob import glob
from stat import *


# The environ variables are catch only on package generating phase.
# After package generation, the version and revision turns into a hardcoded string
VERSION = os.environ.get("UMIT_VERSION", "0.4.5")
REVISION = os.environ.get("UMIT_REVISION", "1567")

VERSION_FILE = os.path.join("share", "umit", "config", "umit_version")
SOURCE_PKG = False

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


################################################################################
# Installation variables

svg = glob(os.path.join('share', 'pixmaps', '*.svg'))
data_files = [ (pixmaps_dir, svg + glob(os.path.join(pixmaps_dir, '*.png')) +
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



################################################################################
# Distutils subclasses

class umit_install(install):
    def run(self):
        install.run(self)

        self.set_perms()
        self.set_modules_path()
        self.fix_paths()
        self.create_uninstaller()
        self.finish_banner()

    def create_uninstaller(self):
        uninstaller_filename = os.path.join(self.install_scripts, "uninstall_umit")
        uninstaller = """#!/usr/bin/env python
import os, sys

print
print '%(line)s Uninstall Umit %(version)s-%(revision)s %(line)s'
print

answer = raw_input('Are you sure that you want to completly uninstall Umit %(version)s? \
(yes/no) ')

if answer != 'yes' and answer != 'y':
    sys.exit(0)

print
print '%(line)s Uninstalling Umit %(version)s... %(line)s'
print
""" % {'version':VERSION, 'revision':REVISION, 'line':'-'*10}

        for output in self.get_outputs():
            uninstaller += "print 'Removing %s...'\n" % output
            uninstaller += "os.remove('%s')\n" % output

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

        ucontent.insert(uline, "sys.path.append('%s')\n" % modules)

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
        su = os.path.join("share", "umit")
        interesting_paths = {"CONFIG_DIR":os.path.join(su, "config"),
                             "DOCS_DIR":os.path.join(su, "docs"),
                             "LOCALE_DIR":os.path.join(su, "locale"),
                             "MISC_DIR":os.path.join(su, "misc"),
                             "PIXMAPS_DIR":os.path.join("share", "pixmaps"),
                             "ICONS_DIR":os.path.join("share", "icons"),
                             "UMIT_ICON":"umit_48.ico"}

        pcontent = ""
        paths_file = os.path.join("umitCore", "Paths.py")
        installed_files = self.get_outputs()
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
        print "%s Thanks for using Umit %s-%s %s" % \
              ("#"*10, VERSION, REVISION, "#"*10)
        print


class umit_sdist(sdist):
    def run(self):
        self.keep_temp = 1
        sdist.run(self)
        self.finish_banner()

    def make_release_tree(self, base_dir, files):
        """Create the directory tree that will become the source
        distribution archive.  All directories implied by the filenames in
        'files' are created under 'base_dir', and then we hard link or copy
        (if hard linking is unavailable) those files into place.
        Essentially, this duplicates the developer's source tree, but in a
        directory named after the distribution, containing only the files
        to be distributed.
        
        --- This is a copy of the distutils.command.sdist make_release_tree with
        a slight modification, which forces the copy of the files instead of
        hard linking them to the temp directory.
        """
        # Create all the directories under 'base_dir' necessary to
        # put 'files' there; the 'mkpath()' is just so we don't die
        # if the manifest happens to be empty.
        self.mkpath(base_dir)
        dir_util.create_tree(base_dir, files, dry_run=self.dry_run)

        # And walk over the list of files, either making a hard link (if
        # os.link exists) to each one that doesn't already exist in its
        # corresponding location under 'base_dir', or copying each file
        # that's out-of-date in 'base_dir'.  (Usually, all files will be
        # out-of-date, because by default we blow away 'base_dir' when
        # we're done making the distribution archives.)

        # Removed the original if statement to force file copying
        link = None
        msg = "copying files to %s..." % base_dir

        if not files:
            log.warn("no files to distribute -- empty manifest?")
        else:
            log.info(msg)
        for file in files:
            if not os.path.isfile(file):
                log.warn("'%s' not a regular file -- skipping" % file)
            else:
                dest = os.path.join(base_dir, file)
                self.copy_file(file, dest, link=link)

        self.distribution.metadata.write_pkg_info(base_dir)
        # End of the modified version of make_release_tree

        # Updating version, revision, splash and paths informations...
        sys.path.append(os.path.join("install_scripts", "utils"))
        from version_update import update_setup, update_paths, update_umit_version

        update_setup(base_dir, VERSION, REVISION)
        update_paths(base_dir, VERSION, REVISION)
        update_umit_version(base_dir, VERSION, REVISION)

    def finish_banner(self):
        print 
        print "%s The packages for Umit %s-%s are in ./dist %s" % \
              ("#" * 10, VERSION, REVISION, "#" * 10)
        print

if SOURCE_PKG:
    umit_sdist = sdist

##################### Umit banner ########################
print
print "%s Umit for Linux %s-%s %s" % ("#" * 10, VERSION, REVISION, "#" * 10)
print
##########################################################

setup(name = 'umit',
      license = 'GNU GPL (version 2 or later)',
      url = 'http://umit.sourceforge.net',
      download_url = 'http://sourceforge.net/project/showfiles.php?group_id=142490',
      author = 'Adriano Monteiro & Cleber Rodrigues',
      author_email = 'py.adriano@gmail.com, cleber@globalred.com.br',
      maintainer = 'Adriano Monteiro',
      maintainer_email = 'py.adriano@gmail.com',
      description = """UMIT is a nmap frontend, developed in Python and GTK and was \
started with the sponsoring of Google's Summer of Code.""",
      long_description = """The project goal is to develop a nmap frontend that \
is really useful for advanced users and easy to be used by newbies. With UMIT, a network admin \
could create scan profiles for faster and easier network scanning or even compare \
scan results to easily see any changes. A regular user will also be able to construct \
powerful scans with UMIT command creator wizards.""",
      version = VERSION,
      scripts = ['umit'],
      packages = ['', 'umitCore', 'umitGUI', 'higwidgets'],
      data_files = data_files,
      cmdclass = {"install":umit_install,
                  "sdist":umit_sdist})