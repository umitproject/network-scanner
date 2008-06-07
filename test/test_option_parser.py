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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import unittest
from umitCore.UmitOptionParser import UmitOptionParser

class TestUmitOptionParser(unittest.TestCase):
    def testInventory1(self):
        option_parser = UmitOptionParser(["-i"])
        self.assert_(option_parser.get_inventory(),
                     "Failed to get inventory option (-i)")

    def testInventory2(self):
        option_parser = UmitOptionParser(["--inventory"])
        self.assert_(option_parser.get_inventory(),
                     "Failed to get inventory option (--inventory)")

    def testInventory3(self):
        option_parser = UmitOptionParser(["-i", "inventory_name"])
        self.assert_(option_parser.get_inventory() == "inventory_name",
                     "Failed to get inventory option (-i inventory_name)")

    def testInventory4(self):
        option_parser = UmitOptionParser(["--inventory", "inventory_name"])
        self.assert_(option_parser.get_inventory() == "inventory_name",
                "Failed to get inventory option (--inventory inventory_name)")

    def testNmap1(self):
        option_parser = UmitOptionParser(["-n"])
        # Shoudl return False, because no nmap arg was defined
        self.assert_(not option_parser.get_nmap(),
                     "Failed to get nmap option (-n)")

    def testNmap2(self):
        option_parser = UmitOptionParser(["-n", "-T4", "-P0", "192.168.0.*"])
        # Shoudl return False, because no nmap arg was defined
        self.assert_(option_parser.get_nmap() == ["-T4", "-P0", "192.168.0.*"],
                     "Failed to get nmap option (-n -T4 -P0 192.168.0.*)")

    def testNmap3(self):
        option_parser = UmitOptionParser(["--nmap"])
        # Shoudl return False, because no nmap arg was defined
        self.assert_(not option_parser.get_nmap(),
                     "Failed to get nmap option (--nmap)")

    def testNmap4(self):
        option_parser = UmitOptionParser(["--nmap",
                                          "-T4",
                                          "-P0",
                                          "192.168.0.*"])
        # Shoudl return False, because no nmap arg was defined
        self.assert_(option_parser.get_nmap() == ["-T4", "-P0", "192.168.0.*"],
                     "Failed to get nmap option (--nmap -T4 -P0 192.168.0.*)")

    def testProfile1(self):
        option_parser = UmitOptionParser(["-p", "profile_name"])
        self.assert_(option_parser.get_profile() == "profile_name",
                     "Failed to get profile option (-p profile_name)")

    def testProfile2(self):
        option_parser = UmitOptionParser(["--profile=profile_name"])
        self.assert_(option_parser.get_profile() == "profile_name",
                     "Failed to get profile option (--profile=profile_name)")

    def testCompare1(self):
        option_parser = UmitOptionParser(["-c", "file1.usr", "file2.usr"])
        self.assert_(option_parser.get_compare() == ("file1.usr", "file2.usr"),
                     "Failed to get compare option (-c file1.usr file2.usr)")

    def testCompare2(self):
        option_parser = UmitOptionParser(["--compare",
                                          "file1.usr",
                                          "file2.usr"])
        self.assert_(option_parser.get_compare() == ("file1.usr",
                                                     "file2.usr"),
                     "Failed to get compare option \
(--compare file1.usr file2.usr)")

    def testCompareText1(self):
        option_parser = UmitOptionParser(["-e",
                                          "file1.usr",
                                          "file2.usr"])
        self.assert_(option_parser.get_compare_text() == ("file1.usr",
                                                          "file2.usr"),
                 "Failed to get text compare option (-e file1.usr file2.usr)")

    def testCompareText2(self):
        option_parser = UmitOptionParser(["--compare-text",
                                          "file1.usr",
                                          "file2.usr"])
        self.assert_(option_parser.get_compare_text() == ("file1.usr",
                                                          "file2.usr"),
                 "Failed to get text compare option \
(--compare-text file1.usr file2.usr)")

    def testDiff1(self):
        option_parser = UmitOptionParser(["-d",
                                          "file1.usr",
                                          "file2.usr"])
        self.assert_(option_parser.get_diff() == ("file1.usr",
                                                  "file2.usr"),
                 "Failed to get diff option (-d file1.usr file2.usr)")

    def testDiff2(self):
        option_parser = UmitOptionParser(["--diff",
                                          "file1.usr",
                                          "file2.usr"])
        self.assert_(option_parser.get_diff() == ("file1.usr",
                                                  "file2.usr"),
                 "Failed to get diff option \
(--diff file1.usr file2.usr)")

    def testNSEFacilitator1(self):
        option_parser = UmitOptionParser(["-s"])
        self.assert_(option_parser.get_nse_facilitator() == ["default"],
                 "Failed to get nse-facilitator option (-s)")

    def testNSEFacilitator2(self):
        option_parser = UmitOptionParser(["-s", "script1.nse"])
        self.assert_(option_parser.get_nse_facilitator() == ["script1.nse"],
                 "Failed to get nse-facilitator option (-s script1.nse)")

    def testNSEFacilitator3(self):
        option_parser = UmitOptionParser(["--nse-facilitator"])
        self.assert_(option_parser.get_nse_facilitator() == ["default"],
                 "Failed to get nse-facilitator option (--nse-facilitator)")

    def testNSEFacilitator4(self):
        option_parser = UmitOptionParser(["--nse-facilitator", "script1.nse"])
        self.assert_(option_parser.get_nse_facilitator() == ["script1.nse"],
                     "Failed to get nse-facilitator option \
(--nse-facilitator script1.nse)")

    def testTarget1(self):
        option_parser = UmitOptionParser(["-t", "www.microsoft.com"])
        self.assert_(option_parser.get_target() == "www.microsoft.com",
                 "Failed to get target option (-t www.microsoft.com)")

    def testTarget2(self):
        option_parser = UmitOptionParser(["--target=www.microsoft.com"])
        self.assert_(option_parser.get_target() == "www.microsoft.com",
                 "Failed to get target option (--target=www.microsoft.com)")

    def testUmitProtocol(self):
        option_parser = UmitOptionParser(["umit://profile_name/target"])
        self.assert_(option_parser.get_protocol() == \
                     "umit://profile_name/target",
                "Failed to get protocol argument (umit://profile_name/target)")

    def testScanProtocol(self):
        option_parser = UmitOptionParser(["scan://profile_name/target"])
        self.assert_(option_parser.get_protocol() == \
                     "scan://profile_name/target",
                "Failed to get protocol argument (scan://profile_name/target)")

    def testNmapProtocol(self):
        option_parser = UmitOptionParser(["nmap://profile_name/target"])
        self.assert_(option_parser.get_protocol() == \
                     "nmap://profile_name/target",
                "Failed to get protocol argument (nmap://profile_name/target)")

    def testOpenScanResult1(self):
        option_parser = UmitOptionParser(["file1.xml", "file2.usr"])
        self.assert_(option_parser.get_open_results() == \
                     ["file1.xml", "file2.usr"],
                     "Failed to get files (file1.xml file2.usr)")

    def testOpenScanResult2(self):
        option_parser = UmitOptionParser(["-f", "file1.xml", 
                                          "-f", "file2.usr"])
        self.assert_(option_parser.get_open_results() == \
                     ["file1.xml", "file2.usr"],
                     "Failed to get files (-f file1.xml -f file2.usr)")

    def testOpenScanResult3(self):
        option_parser = UmitOptionParser(["--file=file1.xml", 
                                          "--file=file2.usr"])
        self.assert_(option_parser.get_open_results() == \
                     ["file1.xml", "file2.usr"],
                    "Failed to get files (--file=file1.xml --file=file2.usr)")

    def testOpenScanResult4(self):
        option_parser = UmitOptionParser(["--file=file1.xml", 
                                          "--file=file2.usr",
                                          "file3.xml"])
        self.assert_(option_parser.get_open_results() == \
                     ["file1.xml", "file2.usr", "file3.xml"],
                    "Failed to get files (--file=file1.xml \
--file=file2.usr file3.xml)")

    def testOpenMapper1(self):
        option_parser = UmitOptionParser(["-m", "file1.usr"])
        self.assert_(option_parser.get_mapper() == "file1.usr",
                     "Failed to get mapper option (-m file1.usr)")

    def testOpenMapper2(self):
        option_parser = UmitOptionParser(["--mapper=file1.usr"])
        self.assert_(option_parser.get_mapper() == "file1.usr",
                     "Failed to get mapper option (--mapper=file1.usr)")

    def testVerbose1(self):
        option_parser = UmitOptionParser([""])
        self.assert_(option_parser.get_verbose() == 40,
                     "Failed to get verbose")

    def testVerbose2(self):
        option_parser = UmitOptionParser(["-v"])
        self.assert_(option_parser.get_verbose() == 30,
                     "Failed to get verbose (-v)")

    def testVerbose3(self):
        option_parser = UmitOptionParser(["-v", "-v"])
        self.assert_(option_parser.get_verbose() == 20,
                     "Failed to get verbose (-v -v)")

    def testVerbose4(self):
        option_parser = UmitOptionParser(["-v", "-v", "-v"])
        self.assert_(option_parser.get_verbose() == 10,
                     "Failed to get verbose (-v -v -v)")

    def testVerbose5(self):
        option_parser = UmitOptionParser(["-v", "-v", "-v", "-v"])
        self.assert_(option_parser.get_verbose() == 0,
                     "Failed to get verbose (-v -v -v -v)")

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestUmitOptionParser)
    unittest.TextTestRunner(verbosity=5).run(suite)