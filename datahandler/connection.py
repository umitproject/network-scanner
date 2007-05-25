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
This handles connections to the database.
Right now it supports only sqlite, but could support more dbs.
"""

from _sqlite import sqlite
from utils import debug

class ConnectDB:
    """
    This is a handler for database connection.
    """
    
    def __init__(self, database):
        """
        Open connection to database and acquire an cursor.
        """
        debug("Openning connection to database; %s" % database)
        
        self.conn = sqlite.connect(database)
        self.cursor = self.conn
        
        
    def __del__(self):
        """
        Closes connections to database.
        """
        debug("Closing connection to database..")
        
        self.cursor.close()
        self.conn.close()
    
    
    def get_id_for(self, table_name):
        """
        Return last insert rowid in a table. (sqlite only)
        """
        debug("Getting pk for last insert in table: %s.." % table_name)
        
        return self.cursor.execute("SELECT last_insert_rowid() \
                FROM %s" % table_name).fetchone()[0]

