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

"""
This scripts tests database integrity based on foreign keys in sqlite
for the umitdb schema. INCOMPLETE!
"""

from db.dbfile import db_test
from db.sqlite import sqlite
import unittest

def conn_cursor():
    c = sqlite.connect(db_test)
    return (c, c.cursor())

class IntegrityTest(unittest.TestCase):
    # values for testing
    address = 'sometext'

    bad_queries = { 
                    # host table
                    (0,): "INSERT INTO host (fk_host_state) VALUES (?)",
                    (4,): "INSERT INTO host (fk_host_state) VALUES (?)",

                    # address table
                    (address, 1): "INSERT INTO address (address, type) \
                                   VALUES (?, ?)",
                    (address, 1, 0):  "INSERT INTO address (address, \
                                       type, fk_vendor) VALUES (?, ?, ?)",
                  }

    def setUp(self):
        self.conn, self.cursor = conn_cursor()

    def testBadQueries(self):
        for values, query in self.bad_queries.items():
            self.assertRaises(sqlite.IntegrityError, self.cursor.execute, 
                              query, values)
    

if __name__ == "__main__":
    unittest.main()
