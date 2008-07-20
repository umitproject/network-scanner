# Copyright (C) 2007 Adriano Monteiro Marques.
#
# Authors: Adriano Monteiro Marques <adriano@umitproject.org>
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

import unittest

# Setting up Paths so UmitConf can be correctly loaded
from os.path import join
from umitCore.Paths import Path
Path.set_umit_conf([join("share", "umit", "config", "umit.conf")])

# Loading UmitConf files
from umitCore.TargetList import target_list


class TestTargetList(unittest.TestCase):
    def setUp(self):
        self.umit_conf = UmitConf()

    def tearDown(self):
        del self.umit_conf

    def testAddTarget(self):
        target_list.add_target("127.0.0.1")

    def testCleanList(self):
        target_list.clean_list()

    def testSave(self):
        target_list.save()

    def testGetTargetList(self):
        target_list.get_traget_list()


if __name__ == "__main__":
    print ">>> Testing TargetList"
    target_list_suite = unittest.TestLoader().loadTestsFromTestCase(TestTargetList)
    unittest.TextTestRunner(verbosity=5).run(target_list_suite)
    print
