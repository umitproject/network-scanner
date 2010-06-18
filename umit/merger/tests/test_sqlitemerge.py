#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2009 Adriano Monteiro Marques
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import unittest
import tempfile
from test.test_support import run_unittest

from umit.merger.sqlitedb import sqlite, merge, column_definitions, _DictCursor

def conn_cursor(name):
    conn = sqlite.connect(name)
    return conn, conn.cursor()

def _table_name():
    """Generates an unique table name each time."""
    name = 'a'
    while True:
        yield name
        new_letter = ord(name[-1]) + 1
        if new_letter > ord('z'):
            name = 'a' * (len(name) + 1)
        else:
            name = name[:-1] + chr(new_letter)

class Base(unittest.TestCase):

    def setUp(self):
        self.new_db_file = tempfile.NamedTemporaryFile()
        self.old_db_file = tempfile.NamedTemporaryFile()
        self.new_db, self.new_cursor = conn_cursor(self.new_db_file.name)
        self.old_db, self.old_cursor = conn_cursor(self.old_db_file.name)

        self.table_name = _table_name()

    def tearDown(self):
        self.new_cursor.close()
        self.old_cursor.close()
        self.new_db.close()
        self.old_db.close()
        self.new_db_file.close()
        self.old_db_file.close()

    def merge_now(self):
        merge(self.new_db_file.name, self.old_db_file.name)


class ColumnDefinitionTest(unittest.TestCase):

    def test_invalid(self):
        self.failUnlessRaises(Exception, column_definitions, 'buh')
        self.failUnlessRaises(Exception, column_definitions, None)

    def test_simple_createtable(self):
        ctable_stmt = "CREATE TABLE x (a)"
        self.failUnlessEqual(column_definitions(ctable_stmt), {'a': None})

        ctable_stmt = "CREATE TABLE x (a,b)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': None, 'b': None})

        ctable_stmt = "CREATE TABLE x (a UNIQUE)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE'})

        ctable_stmt = (
                "CREATE TABLE x ("
                "   a UNIQUE CHECK (1, 2), "
                "   b CONSTRAINT buh)")
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE CHECK (1, 2)', 'b': 'CONSTRAINT buh'})

        ctable_stmt = "CREATE TABLE x (a UNIQUE, -- C,\n)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE'})
        ctable_stmt = "CREATE TABLE x (a UNIQUE, -- C,)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE'})
        ctable_stmt = "CREATE TABLE x (a UNIQUE, -- C,\nb)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE', 'b': None})
        ctable_stmt = "CREATE TABLE x (a UNIQUE, -- C,\n   b)"
        self.failUnlessEqual(column_definitions(ctable_stmt),
                {'a': 'UNIQUE', 'b': None})


class ColumnMergeTest(Base):

    def _prepare_mergetest(self, new, old):
        table = self.table_name.next()
        self.new_cursor.execute("CREATE TABLE %s (%s)" % (table, new))
        self.old_cursor.execute("CREATE TABLE %s (%s)" % (table, old))
        return table

    def _verify_merge(self, new, old):
        table = self._prepare_mergetest(new, old)
        new_table_info = self.new_cursor.execute(
                "pragma table_info(%s)" % table).fetchall()

        self.merge_now()

        # Need to reconnect to get the updated table information.
        conn, cursor = conn_cursor(self.old_db_file.name)
        # I don't care if the pragma table_info still exists or not, if it
        # doesn't then the two next tests will be comparing empty lists.
        old_table_info = cursor.execute(
                "pragma table_info(%s)" % table).fetchall()
        self.failUnlessEqual(len(old_table_info), len(new_table_info))
        self.failUnlessEqual(old_table_info, new_table_info)
        sql_query = (
                "SELECT sql FROM sqlite_master "
                "WHERE type='table' and NAME=?")
        self.failUnlessEqual(
                self.new_cursor.execute(sql_query, (table, )).fetchone()[0],
                cursor.execute(sql_query, (table, )).fetchone()[0])
        cursor.close()
        conn.close()

    def _verify_merge_fails(self, exc, new, old):
        self._prepare_mergetest(new, old)
        self.failUnlessRaises(exc, self.merge_now)


    def test_column_merge(self):
        self._verify_merge(
                "b, c",
                "b")

        self._verify_merge(
                "b INTEGER, c INTEGER",
                "b INTEGER")

        self._verify_merge(
                "b INTEGER, c INTEGER NOT NULL DEFAULT 3",
                "b INTEGER")

        self._verify_merge(
                "a INTEGER, b INTEGER CONSTRAINT fk REFERENCES d(id)",
                "a INTEGER")
        self._verify_merge(
                "a INTEGER, b INTEGER REFERENCES d(id) ON DELETE CASCADE",
                "a INTEGER")

        self._verify_merge_fails(sqlite.OperationalError,
                "b INTEGER, c INTEGER NOT NULL",
                "b INTEGER")

        self._verify_merge_fails(Exception,
                "b INTEGER, c INTEGERY PRIMARY KEY",
                "b INTEGER")


class TriggersTest(Base):

    def _verify_merge(self):
        triggers = "SELECT sql FROM sqlite_master WHERE type='trigger'"
        conn, cursor = conn_cursor(self.old_db_file.name)
        self.failUnlessEqual(
                self.new_cursor.execute(triggers).fetchall(),
                cursor.execute(triggers).fetchall())

    def test_trigger_merge(self):
        table = self.table_name.next()
        self.new_cursor.execute("CREATE TABLE %s (a INTEGER)" % table)
        self.old_cursor.execute("CREATE TABLE %s (a INTEGER)" % table)
        self.new_cursor.execute(
                "CREATE TRIGGER %s AFTER UPDATE OF a ON %s "
                "BEGIN"
                "  UPDATE %s SET a = old.a; "
                "END" % (self.table_name.next(), table, table))

        self.merge_now()
        self._verify_merge()


class TableCopyTest(Base):

    def _verify_copy(self, table):
        # Need to reconnect to get the updated table information.
        conn, cursor = conn_cursor(self.old_db_file.name)

        query = "SELECT sql FROM sqlite_master WHERE name=? OR tbl_name=?"
        args = (table, table)
        self.failUnlessEqual(
                cursor.execute(query, args).fetchall(),
                self.new_cursor.execute(query, args).fetchall())

    def test_table_copy(self):
        table = self.table_name.next()
        self.new_cursor.execute("CREATE TABLE %s (a INTEGER)" % table)
        self.new_cursor.execute(
                "CREATE TRIGGER %s AFTER UPDATE OF a ON %s "
                "BEGIN"
                "  UPDATE %s SET a = old.a; "
                "END" % (self.table_name.next(), table, table))

        self.merge_now()
        self._verify_copy(table)


if __name__ == "__main__":
    run_unittest(ColumnDefinitionTest, ColumnMergeTest, TriggersTest,
            TableCopyTest)
