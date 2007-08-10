# Copyright (C) 2005-2007 Insecure.Com LLC.
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

import unittest
import sys

# Setting up Paths so UmitConf can be correctly loaded
from os.path import join, split, abspath, exists
from umitCore.Paths import Paths


class TestPaths(unittest.TestCase):
    cur_dir = abspath(split(sys.argv[0])[0])
    paths_list = [cur_dir,
                  split(cur_dir)[0],
                  split(split(cur_dir)[0])[0]]

    def setUp(self):
        self.path = Paths()
        cur_dir = self.paths_list.pop(0)
        print "Testing Paths from inside %s" % cur_dir
        self.path.set_umit_conf(cur_dir)

    def tearDown(self):
        del self.path

    def get_paths(self):
        self.assert_(exists(self.path.locale_dir),
                     "Failed to get 'locale_dir'")
        self.assert_(exists(self.path.pixmaps_dir),
                     "Failed to get 'pixmaps_dir'")
        self.assert_(exists(self.path.config_dir),
                     "Failed to get 'config_dir'")

        self.assert_(exists(self.path.config_file),
                     "Failed to get 'config_file'")
        self.assert_(exists(self.path.target_list),
                     "Failed to get 'target_list'")
        self.assert_(exists(self.path.profile_editor),
                     "Failed to get 'profile_editor'")
        self.assert_(exists(self.path.wizard),
                     "Failed to get 'wizard'")
        self.assert_(exists(self.path.scan_profile),
                     "Failed to get 'scan_profile'")
        self.assert_(exists(self.path.recent_scans),
                     "Failed to get 'recent_scans'")
        self.assert_(exists(self.path.options),
                     "Failed to get 'options'")

        self.assert_(exists(self.path.umit_op),
                     "Failed to get 'umit_op'")
        self.assert_(exists(self.path.umit_opi),
                     "Failed to get 'umit_opi'")
        self.assert_(exists(self.path.umit_opt),
                     "Failed to get 'umit_opt'")
        self.assert_(exists(self.path.umit_opf),
                     "Failed to get 'umit_opf'")
        self.assert_(exists(self.path.umitdb),
                     "Failed to get 'umitdb'")
        self.assert_(exists(self.path.services_dump),
                     "Failed to get 'services_dump'")
        self.assert_(exists(self.path.os_dump),
                     "Failed tp get 'os_dump'")
        self.assert_(exists(self.path.umit_version),
                     "Failed tp get 'umit_version'")
        self.assert_(exists(self.path.os_classification),
                     "Failed to get 'os_classification'")

        self.path.nmap_command_path

    def testConfigPaths1(self):
        self.get_paths()

    def testConfigPaths2(self):
        self.get_paths()

    def testConfigPaths3(self):
        self.get_paths()


if __name__ == "__main__":
    print ">>> Testing Paths"
    paths_suite = unittest.TestLoader().loadTestsFromTestCase(TestPaths)
    unittest.TextTestRunner(verbosity=5).run(paths_suite)