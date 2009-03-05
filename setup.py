#!/usr/bin/env python
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
#          Guilherme Polo <ggpolo@gmail.com>
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
import re
import sys
from stat import *
from glob import glob

from distutils.core import setup
from distutils.command.install import install
from distutils.command.sdist import sdist
from distutils.command.build import build
from distutils import log, dir_util

from umit.core.Version import VERSION
from utils.i18n import msgfmt

from install_scripts.common import BIN_DIRNAME, PIXMAPS_DIR, ICONS_DIR, \
        DOCS_DIR, LOCALE_DIR, CONFIG_DIR, MISC_DIR, SQL_DIR

py2exe_cmdclass = py2exe_options = py2app_options = None
if 'py2exe' in sys.argv:
    from install_scripts.windows.py2exe_setup import py2exe_cmdclass, \
            py2exe_options
if 'py2app' in sys.argv:
    from install_scripts.macosx.py2app_setup import py2app_options


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

# What to copy to the destiny
# Here, we define what should be put inside the directories set in the
# beginning of this file. This list contain tuples where the first element
# contains a path to where the other elements of the tuple should be installed.
# The first element is a path in the INSTALLATION PREFIX, and the other
# elements are the path in the source base.
# Ex: [("share/pixmaps", "/umit/trunk/share/pixmaps/test.png")]
# This will install the test.png file in the installation dir share/pixmaps.
svg = glob(os.path.join('share', 'pixmaps', '*.svg'))
data_files = [
        (PIXMAPS_DIR,
            glob(os.path.join(PIXMAPS_DIR, '*.svg')) +
            glob(os.path.join(PIXMAPS_DIR, '*.png')) +
            glob(os.path.join(PIXMAPS_DIR, '*.xpm')) +
            glob(os.path.join(PIXMAPS_DIR, 'umit.o*'))),

        (CONFIG_DIR,
            [os.path.join(CONFIG_DIR, 'umit.conf')] +
            [os.path.join(CONFIG_DIR, 'scan_profile.usp')] +
            [os.path.join(CONFIG_DIR, 'umit_version')] +
            [os.path.join(CONFIG_DIR, 'umitng.db')] +
            [os.path.join(CONFIG_DIR, 'timeline-settings.conf')] +
            [os.path.join(CONFIG_DIR, 'tl_colors_evt_std.conf')] +
            [os.path.join(CONFIG_DIR, 'scheduler-schemas.conf')] +
            [os.path.join(CONFIG_DIR, 'scheduler-profiles.conf')] +
            [os.path.join(CONFIG_DIR, 'scheduler.log')] +
            [os.path.join(CONFIG_DIR, 'smtp-schemas.conf')] +
            glob(os.path.join(CONFIG_DIR, '*.xml'))+
            glob(os.path.join(CONFIG_DIR, '*.txt'))),

        # umit.db SQL
        (SQL_DIR, glob(os.path.join(SQL_DIR, '*.sql'))),

        (MISC_DIR, glob(os.path.join(MISC_DIR, '*.dmp'))),

        # Radialnet
        (os.path.join(PIXMAPS_DIR, 'radialnet', 'application'),
            glob(os.path.join(PIXMAPS_DIR, 'radialnet', 'application',
                '*.png'))),
        (os.path.join(PIXMAPS_DIR, 'radialnet', 'icons'),
            glob(os.path.join(PIXMAPS_DIR, 'radialnet', 'icons','*.png'))),

        # Network Inventory
        (os.path.join(PIXMAPS_DIR, 'networkinventory'),
            glob(os.path.join(PIXMAPS_DIR, 'networkinventory', '*.png'))),

        # InterfaceEditor
        (os.path.join(PIXMAPS_DIR, 'uie'),
            glob(os.path.join(PIXMAPS_DIR, 'uie', '*.png'))),

        (ICONS_DIR,
            glob(os.path.join(ICONS_DIR, '*.ico')) +
            glob(os.path.join(ICONS_DIR, '*.png'))),

        (DOCS_DIR,
            glob(os.path.join(DOCS_DIR, '*.html')) +
            glob(os.path.join(DOCS_DIR, 'comparing_results', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'profile_editor', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'scanning', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'searching', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'wizard', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'scheduler', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'smtpsetup', '*.xml')) +
            glob(os.path.join(DOCS_DIR, 'screenshots', '*.png')))]

# Add i18n files to data_files list
os.path.walk(LOCALE_DIR, mo_find, data_files)


##############################################################################
# Distutils subclasses

class umit_build(build):

    def delete_mo_files(self):
        """ Remove *.mo files """
        tmp = []
        os.path.walk(LOCALE_DIR, mo_find, tmp)
        for (path, t) in tmp:
            os.remove(t[0])

    def build_mo_files(self):
        """Build mo files from po and put it into LC_MESSAGES """
        tmp = []
        os.path.walk(LOCALE_DIR, po_find, tmp)
        for (path, t) in tmp:
            full_path = os.path.join(path , "LC_MESSAGES", "umit.mo")
            self.mkpath(os.path.dirname(full_path))
            self.announce("Compiling %s -> %s" % (t[0], full_path))
            msgfmt.make(t[0], full_path, False)
        # like guess
        os.path.walk(LOCALE_DIR, mo_find, data_files)

    def run(self):
        self.delete_mo_files()
        self.build_mo_files()
        build.run(self)


class umit_install(install):

    def run(self):
        # Add i18n files to data_files list
        os.path.walk(LOCALE_DIR, mo_find, data_files)
        install.run(self)

        self.set_perms()
        self.set_modules_path()
        self.fix_paths()
        self.create_uninstaller()
        self.finish_banner()

    def create_uninstaller(self):
        uninstaller_filename = os.path.join(
                self.install_scripts, "uninstall_umit")
        uninstaller = []
        uninstaller.append(
                "#!/usr/bin/env python\n"
                "import os, sys\n"
                "\n"
                "print\n"
                "print '%(line)s Uninstall Umit %(version)s %(line)s'\n"
                "print\n"
                "\n"
                "answer = raw_input('Are you sure that you want to '\n"
                "        'completly uninstall Umit %(version)s? (yes/no) ')\n"
                "\n"
                "if answer.lower() not in ['yes', 'y']:\n"
                "    sys.exit(0)\n"
                "\n"
                "print\n"
                "print '%(line)s Uninstalling Umit %(version)s... %(line)s'\n"
                "print\n" % {'version': VERSION, 'line': '-' * 10})

        for output in self.get_outputs():
            uninstaller.append(
                    "print 'Removing %(output)s...'\n"
                    "if os.path.exists('%(output)s'):\n"
                    "    os.remove('%(output)s')\n" % {'output': output})

        uninstaller.append(
                "print 'Removing uninstaller itself...'\n"
                "os.remove('%s')\n" % uninstaller_filename)

        uninstaller_file = open(uninstaller_filename, 'w')
        uninstaller_file.writelines(uninstaller)
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
        interesting_paths = {"CONFIG_DIR": CONFIG_DIR,
                             "DOCS_DIR": DOCS_DIR,
                             "LOCALE_DIR": LOCALE_DIR,
                             "MISC_DIR": MISC_DIR,
                             "PIXMAPS_DIR": PIXMAPS_DIR,
                             "ICONS_DIR": ICONS_DIR}

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


cmdclasses = {
        "install": umit_install,
        "build": umit_build,
        "sdist": umit_sdist}

if py2exe_cmdclass:
    cmdclasses.update(py2exe_cmdclass)

options = dict(
        name = 'umit',
        license = 'GNU GPL (version 2 or later)',
        url = 'http://www.umitproject.org',
        download_url = 'http://www.umitproject.org',
        author = 'Adriano Monteiro & Cleber Rodrigues',
        author_email = 'adriano@umitproject.org, cleber@globalred.com.br',
        maintainer = 'Adriano Monteiro',
        maintainer_email = 'adriano@umitproject.org',
        description = ("Umit is a network scanning frontend, developed in "
            "Python and GTK and was started with the sponsoring of "
            "Google's Summer of Code."),
        long_description = ("The project goal is to develop a network "
            "scanning frontend that is really useful for advanced users and "
            "easy to be used by newbies. With Umit, a network admin can "
            "create scan profiles for faster and easier network scanning "
            "or even compare scan results to easily see any changes. "
            "A regular user will also be able to construct powerful scans "
            "with Umit command creator wizards."),
        version = VERSION,
        scripts = [
            os.path.join(BIN_DIRNAME, 'umit'),
            os.path.join(BIN_DIRNAME, 'umit_scheduler.py')],
        packages = [
            'umit', 'umit.core', 'umit.core.radialnet', 'umit.db',
            'umit.gui', 'umit.gui.radialnet', 'umit.interfaceeditor',
            'umit.interfaceeditor.selectborder', 'umit.inventory',
            'umit.plugin', 'higwidgets'],
        data_files = data_files,
        cmdclass = cmdclasses
        )

if py2exe_options:
    options.update(py2exe_options)

if py2app_options:
    options.update(py2app_options)

setup(**options)
