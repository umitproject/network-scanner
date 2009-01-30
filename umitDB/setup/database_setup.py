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
Setup database for umit.
"""

import os
import sys

_UMIT_ROOT = os.path.join(os.pardir, os.pardir)
_SQL_PATH = os.path.join(os.pardir, 'sql')
sys.path.insert(0, _UMIT_ROOT)
from umitDB._database import sql, database

def sqlfile_path(sqlname):
    return os.path.join(_SQL_PATH, '%s-%s.sql' % (database, sqlname))

def acquire_conn_cursor(db):
    """
    Get connection and cursor from database.
    """
    conn = sql.connect(db)
    cursor = conn.cursor()

    return conn, cursor

def setup_tables(conn, cursor):
    """
    Create all tables for database.
    """
    tables = open(sqlfile_path('schema'), 'r').readlines()
    tables = ''.join(line for line in tables)

    cursor.executescript(tables)
    conn.commit()

def setup_triggers(conn, cursor):
    """
    Setup triggers for database.
    """
    insert_triggers = open(sqlfile_path('insert-triggers'), 'r').readlines()
    insert_triggers = ''.join(line for line in insert_triggers)

    update_triggers = open(sqlfile_path('update-triggers'), 'r').readlines()
    update_triggers = ''.join(line for line in update_triggers)

    delete_triggers = open(sqlfile_path('delete-triggers'), 'r').readlines()
    delete_triggers = ''.join(line for line in delete_triggers)

    cursor.executescript(insert_triggers)
    cursor.executescript(update_triggers)
    cursor.executescript(delete_triggers)
    conn.commit()

def setup_database(conn, cursor):
    """
    Setup database.
    """
    setup_tables(conn, cursor)
    setup_triggers(conn, cursor)

def drop_tables(conn, cursor):
    """
    Drops all tables in database.
    """
    drop_tables = open(sqlfile_path('drop-tables'), 'r').readlines()
    drop_tables = ''.join(line for line in drop_tables)

    cursor.executescript(drop_tables)
    conn.commit()

def drop_triggers(conn, cursor):
    """
    Drops all triggers in database.
    """
    drop_triggers = open(sqlfile_path('drop-triggers'), 'r').readlines()
    drop_triggers = ''.join(line for line in drop_triggers)

    cursor.executescript(drop_triggers)
    conn.commit()


def clear_database(conn, cursor):
    """
    Clear database.
    """

    drop_triggers(conn, cursor)
    drop_tables(conn, cursor)
    cursor.execute("VACUUM")

    conn.commit()

# When invoked set up umit new generation database.
if __name__ == "__main__":
    db = os.path.join(_UMIT_ROOT, 'share', 'umit', 'config', 'umitng.db')
    conn, cursor = acquire_conn_cursor(db)
    try:
        setup_database(conn, cursor)
    except sql.OperationalError, err:
        sys.stderr.write("Creating a clean database failed!\n"
            "\tReason: %s\n\n" % err)
        raw_input(
            "Press ENTER to clear the current database and create a new one")
        clear_database(conn, cursor)
        setup_database(conn, cursor)

