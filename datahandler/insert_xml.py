# Copyright (C) 2007 Insecure.Com LLC.
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
# USA

import sys
import time
import timing
from dbdatahandler import DBDataHandler


if __name__ == "__main__":
    args_len = len(sys.argv) - 1
    if not args_len:
        print "Especify at least one xml file."
        sys.exit(0)

    files = sys.argv[1:]

    timing.start()

    print "Start time:", time.ctime(), '\n'

    """
    test_data = "../tests/data"
    files = ["%s/xml_test.xml" % test_data, "%s/xml_test1.xml" % test_data, 
             "%s/xml_test2.xml" % test_data, "%s/xml_test3.xml" % test_data, 
             "%s/xml_test4.xml" % test_data, "%s/xml_test5.xml" % test_data, 
             "%s/xml_test6.xml" % test_data, "%s/xml_test7.xml" % test_data, 
             "%s/xml_test8.xml" % test_data, "%s/xml_test9.xml" % test_data, 
             "%s/xml_test10.xml" % test_data, "%s/xml_test11.xml" % test_data, 
             "%s/xml_test12.xml" % test_data, "%s/xml_a.xml" % test_data
            ]
    """
    #files = [ "%s/scan_siostype.xml" % test_data ]

    a = DBDataHandler("schema-testing.db", debug=False)
    
    errors = len(files)
    for test in files:
        err = a.insert_xml(test, store_original=False)
        if not err:
           errors -= 1

    timing.finish()

    if len(files) - errors:
        print "\n%d files inserted into database" % (len(files) - errors)
        print "Each file took around %.4f seconds to be inserted" % (float(timing.milli()) / (len(files) * 1000))
    print "Finish time:", time.ctime()
    print "Duration (miliseconds):", timing.milli()
