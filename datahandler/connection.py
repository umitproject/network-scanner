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
Right now it supports only sqlite, but could be more generic.
"""

from _sqlite import sqlite

class ConnectDB:
    """
    This is a handler for database connection.
    """
    
    def __init__(self, database):
        """
        Open connection to database and acquire an cursor.
        """
        self.conn = sqlite.connect(database)
        self.cursor = self.conn
        
    def __del__(self):
        """
        Closes connections to database.
        """
        self.cursor.close()
        self.conn.close()
    