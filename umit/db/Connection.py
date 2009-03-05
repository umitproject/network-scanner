# Copyright (C) 2007 Adriano Monteiro Marques
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
This handles connections to the database.
"""

from umit.db._database import sql
from umit.db._database import database
from umit.db.Utils import log_debug

debug = log_debug('umit.db.Connection')

def dict_factory(cursor, row):
    """
    Convert a standard row to a dict.
    """
    d = {}

    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]

    return d


class ConnectDB:
    """
    This is a handler for database connection.
    """

    def __init__(self, db):
        """
        Open connection to db and acquire a cursor.
        """
        debug("Openning connection to database: %r", db)

        if database == 'sqlite':
            self.conn = sql.connect(db,
                detect_types=sql.PARSE_COLNAMES | sql.PARSE_DECLTYPES)
        else: # others not supported for now
            self.conn = sql.connect(db)

        self.cursor = self.conn.cursor()


    def close(self):
        """
        Closes connections to database.
        """
        debug("Closing connection to database..")

        self.cursor.close()
        self.conn.close()


    def use_dict_cursor(self):
        """
        Change to dict_factory cursor.
        """
        self.cursor.close()
        self.conn.row_factory = dict_factory
        self.cursor = self.conn.cursor()


    def use_standard_cursor(self):
        """
        Change to standard cursor.
        """
        self.cursor.close()
        self.conn.row_factory = None
        self.cursor = self.conn.cursor()


    def get_id_for(self, table_name):
        """
        Return last insert rowid in a table. (sqlite only)
        """
        debug("Getting pk for last insert in table: %r..", table_name)

        if database == 'sqlite':
            return self.cursor.execute("SELECT last_insert_rowid() \
                    FROM %s" % table_name).fetchone()[0]
        else:
            debug("Using MAX to retrieve last insert in table")

            return self.cursor.execute("SELECT MAX(pk) \
                    FROM %s" % table_name).fetchone()[0]
