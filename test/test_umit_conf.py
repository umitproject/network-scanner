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

# Setting up Paths so UmitConf can be correctly loaded
from os.path import join
from umitCore.Paths import Path
Path.set_umit_conf([join("share", "umit", "config", "umit.conf")])

# Loading UmitConf files
from umitCore.UmitConf import *


class TestUmitConf(unittest.TestCase):
    def testUmitVersion(self):
        self.assert_(umit_version(),
                     "Failed to get UmitConf.umit_version()")

    def setUp(self):
        self.umit_conf = UmitConf()

    def tearDown(self):
        del self.umit_conf

    def testGetColoredDiff(self):
        self.umit_conf.colored_diff

    def testSetColoredDiff(self):
        self.umit_conf.colored_diff = True

    def testColoredDiffSaved(self):
        self.umit_conf.colored_diff = False
        self.umit_conf.save_changes()

        colored = self.umit_conf.colored_diff
        self.assert_(colored == False,
                "Failed to save colored diff - False. Returned %s" % colored)

        self.umit_conf.colored_diff = True
        self.umit_conf.save_changes()

        colored = self.umit_conf.colored_diff
        self.assert_(colored == True,
                "Failed to save colored diff - True. Returned %s" % colored)

    def testGetDiffMode(self):
        self.umit_conf.diff_mode

    def testSetDiffMode(self):
        self.umit_conf.diff_mode = "compare"

    def testDiffModeSaved(self):
        self.umit_conf.diff_mode = "text"
        self.umit_conf.save_changes()

        mode = self.umit_conf.diff_mode
        self.assert_(mode == "text",
                 "Failed to save diff_mode 'text'. Returned '%s'" % mode)

        self.umit_conf.diff_mode = "compare"
        self.umit_conf.save_changes()

        mode = self.umit_conf.diff_mode
        self.assert_(mode == "compare",
                 "Failed to save diff_mode 'compare'. Returned '%s'" % mode)

class TestSearchConfig(unittest.TestCase):
    def setUp(self):
        self.search_umit = SearchConfig()

    def tearDown(self):
        del self.search_umit

    def testGetDirectory(self):
        self.search_umit.directory

    def testSetDirectory(self):
        self.search_umit.directory = ""

    def testDirectorySaved(self):
        self.search_umit.directory = "directory"
        self.search_umit.save_changes()

        d = self.search_umit.directory
        self.assert_(d == "directory",
                "Failed to save directory 'directory'. Returned '%s'" % d)

        self.search_umit.direcorty = ""
        self.search_umit.save_changes()

    def testGetFileExtension(self):
        self.search_umit.file_extension

    def testSetFileExtension(self):
        self.search_umit.file_extension = "usr"

    def testFileExtensionSaved(self):
        self.search_umit.file_extension = ".usr"
        self.search_umit.save_changes()

        ext = self.search_umit.file_extension
        self.assert_(ext == [".usr"],
                 "Failed to save file_extension ['.usr']. Returned '%s'" % ext)

        self.search_umit.file_extension = "usr"
        self.search_umit.save_changes()

    def testGetSaveTime1(self):
        self.search_umit.save_time

    def testGetSaveTime2(self):
        self.assert_(type(self.search_umit.save_time) == type([]),
                     "Failed to get save_time as a list.")

    def testSetSaveTime1(self):
        self.search_umit.save_time = "60;days"

    def testSetSaveTime2(self):
        self.search_umit.save_time = ["60", "days"]

    def testSaveTimeSaved(self):
        self.search_umit.save_time = ["30","days"]
        self.search_umit.save_changes()

        save = self.search_umit.save_time
        self.assert_(save == ["30", "days"],
            "Failed to save save_time as ['30','days']. Returned '%s'" % save)

    def testGetStoreResults(self):
        self.search_umit.store_results

    def testSetStoreResults(self):
        self.search_umit.store_results = True

    def testStoreResultsSaved(self):
        self.search_umit.store_results = False
        self.search_umit.save_changes()

        store = self.search_umit.store_results
        self.assert_(store == False,
                 "Failed to save store_results as False. Returned %s" % store)

        self.search_umit.store_results = True
        self.search_umit.save_changes()

    def testGetSearchDB(self):
        self.search_umit.search_db

    def testSetSearchDB(self):
        self.search_umit.search_db = True

    def testSearchDBSaved(self):
        self.search_umit.search_db = False
        self.search_umit.save_changes()

        search = self.search_umit.search_db
        self.assert_(search == False,
                 "Failed to save search_db as False. Returned %s" % search)

        self.search_umit.search_db = True
        self.search_umit.save_changes()

    def testGetConvertedSaveTime(self):
        self.search_umit.converted_save_time

    def testGetTimeList(self):
        self.search_umit.time_list


class TestProfile(unittest.TestCase):
    def setUp(self):
        self.profile = Profile()

    def tearDown(self):
        del self.profile

    def testAddAndRemoveProfile(self):
        self.profile.add_profile("test_suite",\
                                 command="test_suite",\
                                 hint="test suite",\
                                 description="test suite",\
                                 annotation="test suite",\
                                 options={"test1":"test1",
                                          "test2":"test2"})
        self.profile.save_changes()
        self.profile._verify_profile("test_suite")
        self.profile.remove_profile("test_suite")
        self.profile.save_changes()

class TestCommandProfile(unittest.TestCase):
    def setUp(self):
        self.command_profile = CommandProfile()

    def tearDown(self):
        del self.command_profile

    def testProfile(self):
        self.command_profile.add_profile("test_suite",\
                                 command="test_suite_command",\
                                 hint="test_suite_hint",\
                                 description="test_suite_description",\
                                 annotation="test_suite_annotation",\
                                 options={"test1":"test1",
                                          "test2":"test2"})
        self.command_profile.save_changes()
        self.command_profile._verify_profile("test_suite")
        self.command_profile.get_profile("test_suite")

        self.assert_(self.command_profile.get_command("test_suite") == \
                     "test_suite_command",
                     "Failed to get_command().")
        self.assert_(self.command_profile.get_hint("test_suite") == \
                     "test_suite_hint",
                     "Failed to get_hint()")
        self.assert_(self.command_profile.get_description("test_suite") == \
                     "test_suite_description",
                     "Failed to get_description()")
        self.assert_(self.command_profile.get_annotation("test_suite") == \
                     "test_suite_annotation",
                     "Failed to get_annotation()")
        self.assert_(self.command_profile.get_options("test_suite") == \
                     {"test1":"test1",
                      "test2":"test2"},
                     "Failed to get_options(). Returned %s" % \
                     self.command_profile.get_options("test_suite"))

        self.command_profile.remove_profile("test_suite")
        self.command_profile.save_changes()

class TestNmapOutputHighlight(unittest.TestCase):
    def setUp(self):
        self.high = NmapOutputHighlight()

    def tearDown(self):
        del self.high

    def testDateSaved(self):
        self.high.date = self.default_highlights["date"]
        self.high.save_changes()

        date = self.high.date
        self.assert_(date == self.default_highlights["date"],
                     "Failed to save date. Returned %s" % date)

    def testHostnameSaved(self):
        self.high.hostname = self.default_highlights["hostname"]
        self.high.save_changes()

        hn = self.high.hostname
        self.assert_(hn == self.default_highlights["hostname"],
                     "Failed to save hostname. Returned %s" % hn)

    def testIPSaved(self):
        self.high.ip = self.default_highlights["ip"]
        self.high.save_changes()

        ip = self.high.ip
        self.assert_(ip == self.default_highlights["ip"],
                     "Failed to save ip. Returned %s" % ip)

    def testPortListSaved(self):
        self.high.port_list = self.default_highlights["port_list"]
        self.high.save_changes()

        port_list = self.high.port_list
        self.assert_(port_list == self.default_highlights["port_list"],
                     "Failed to save port_list. Returned %s" % port_list)

    def testOpenPortSaved(self):
        self.high.open_port = self.default_highlights["open_port"]
        self.high.save_changes()

        op = self.high.open_port
        self.assert_(op == self.default_highlights["open_port"],
                     "Failed to save open_port. Returned %s" % op)

    def testClosedPortSaved(self):
        self.high.closed_Port = self.default_highlights["closed_port"]
        self.high.save_changes()

        cp = self.high.closed_port
        self.assert_(cp == self.default_highlights["closed_port"],
                     "Failed to save closed_port. Returned %s" % cp)

    def testFilteredPortSaved(self):
        self.high.filtered_port = self.default_highlights["filtered_port"]
        self.high.save_changes()

        fp = self.high.filtered_port
        self.assert_(fp == self.default_highlights["filtered_port"],
                     "Failed to save filtered_port. Returned %s" % fp)

    def testDetailsSaved(self):
        self.high.details = self.default_highlights["details"]
        self.high.save_changes()

        details = self.high.details
        self.assert_(details == self.default_highlights["details"],
                     "Failed to save details. Returned %s" % details)

    default_highlights = {\
        "date":[1, 0, 0, [0, 0, 0], [65535, 65535, 65535],
                "\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}\s.{1,4}"],
        "hostname":[1, 1, 1, [0, 111, 65535], [65535, 65535, 65535],
                    "(\w{2,}://)*\w{2,}\.\w{2,}(\.\w{2,})*(/[\w{2,}]*)*"],
        "ip":[1, 0, 0, [0, 0, 0], [65535, 65535, 65535],
              "\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"],
        "port_list":[1, 0, 0, [0, 1272, 28362], [65535, 65535, 65535],
                     "PORT\s+STATE\s+SERVICE(\s+VERSION)?\s.*"],
        "open_port":[1, 0, 0, [0, 41036, 2396], [65535, 65535, 65535],
                     "\d{1,5}/.{1,5}\s+open\s+.*"],
        "closed_port":[0, 0, 0, [65535, 0, 0], [65535, 65535, 65535],
                       "\d{1,5}/.{1,5}\s+closed\s+.*"],
        "filtered_port":[0, 0, 0, [38502, 39119, 0], [65535, 65535, 65535],
                         "\d{1,5}/.{1,5}\s+filtered\s+.*"],
        "details":[1, 0, 1, [0, 0, 0],[65535, 65535, 65535],
                   "^(\w{2,}[\s]{,3}){,4}:"]}

class TestDiffColors(unittest.TestCase):
    def setUp(self):
        self.diff = DiffColors()

    def tearDown(self):
        del self.diff

    def testUnchanged(self):
        self.diff.unchanged = [65213, 65535, 38862]
        self.diff.save_changes()

        u = self.diff.unchanged
        self.assert_(u == [65213, 65535, 38862],
                 "Failed to save unchanged. Returned %s" % u)

    def testAdded(self):
        self.diff.added = [29490, 42662, 54079]
        self.diff.save_changes()

        a = self.diff.added
        self.assert_(a == [29490, 42662, 54079],
                 "Failed to save added. Returned %s" % a)

    def testNotPresent(self):
        self.diff.not_present = [58079, 19076, 12703]
        self.diff.save_changes()

        n = self.diff.not_present
        self.assert_(n == [58079, 19076, 12703],
                 "Failed to save not_present. Returned %s" % n)

    def testModified(self):
        self.diff.modified = [63881, 42182, 13193]
        self.diff.save_changes()

        m = self.diff.modified
        self.assert_(m == [63881, 42182, 13193],
                 "Failed to save modified. Returned %s" % m)

if __name__ == "__main__":
    print ">>> Testing UmitConf"
    umit_conf_suite = unittest.TestLoader().loadTestsFromTestCase(TestUmitConf)
    unittest.TextTestRunner(verbosity=5).run(umit_conf_suite)
    print

    print ">>> Testing SearchConfig"
    search_config_suite = unittest.TestLoader().loadTestsFromTestCase(TestSearchConfig)
    unittest.TextTestRunner(verbosity=5).run(search_config_suite)
    print

    print ">>> Testing Profile"
    profile_suite = unittest.TestLoader().loadTestsFromTestCase(TestProfile)
    unittest.TextTestRunner(verbosity=5).run(profile_suite)
    print

    print ">>> Testing CommandProfile"
    command_profile_suite = unittest.TestLoader().loadTestsFromTestCase(TestCommandProfile)
    unittest.TextTestRunner(verbosity=5).run(command_profile_suite)
    print

    print ">>> Testing NmapOutputHighlight"
    highlight_suite = unittest.TestLoader().loadTestsFromTestCase(TestNmapOutputHighlight)
    unittest.TextTestRunner(verbosity=5).run(highlight_suite)
    print

    print ">>> Testing DiffColors"
    diff_suite = unittest.TestLoader().loadTestsFromTestCase(TestDiffColors)
    unittest.TextTestRunner(verbosity=5).run(diff_suite)
    print
