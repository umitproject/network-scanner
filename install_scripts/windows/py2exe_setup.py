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

__all__ = ['py2exe_cmdclass', 'py2exe_options']

import os
import sys

from py2exe.build_exe import py2exe as build_exe

from install_scripts.common import BIN_DIRNAME, ICONS_DIR

# Add the bin dir to the sys.path so we can indicate that the umit_scheduler
# module is a service.
umit_top_dir = os.path.abspath(os.path.dirname(
    os.path.join(__file__, os.path.pardir, os.path.pardir)))
sys.path.append(os.path.join(umit_top_dir, BIN_DIRNAME))

# win32com changes its __path__ to be able to do imports from
# win32comext (which is not a python package), but the modulefinder
# does not handle such situtation and thus win32com.shell (which is
# really win32comext.shell) cannot be found. Let's fix this here so
# umit.core.BasePaths still works after we run py2exe over it.
try:
    import py2exe.mf as modulefinder
except ImportError:
    # This py2exe is too old, will use the standard modulefinder
    import modulefinder
import win32com
for path in win32com.__path__[1:]:
    modulefinder.AddPackagePath("win32com", path)

class umit_py2exe(build_exe):
    def run(self):
        build_exe.run(self)
        self.finish_banner()

    def finish_banner(self):
        print
        print "%s The compiled version of Umit %s is in ./dist %s" % \
              ("#"*10, VERSION, "#"*10)
        print


py2exe_cmdclass = {"py2exe": umit_py2exe}

py2exe_options = dict(
        zipfile = None,
        service = [{'modules': ['umit_scheduler'], 'cmdline_style': 'custom'}],
        windows = [{
            "script": os.path.join(BIN_DIRNAME, "umit"),
            "icon_resources": [(1, os.path.join(ICONS_DIR, "umit_48.ico"))]
            }],
        options = {"py2exe": {
            "compressed": 1,
            "optimize": 2,
            "packages": "encodings",
            "includes": [
                'pango', 'atk', 'gobject', 'pickle', 'bz2',
                'encodings', 'encodings.*', 'cairo', 'pangocairo'],
            # Ignore psyco if it is not installed
            "ignores": ['psyco'],
            "excludes": ['Tkinter', 'pdb']}
            }
        )
