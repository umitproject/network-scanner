__all__ = ['merge']

import os
import re
import shutil
import warnings
try:
    from sqlite3 import dbapi2 as sqlite
except ImportError:
    from pysqlite2 import dbapi2 as sqlite

def _dict_factory(cursor, row):
    res = {}
    for indx, col in enumerate(cursor.description):
        res[col[0]] = row[indx]

    return res

class _DictCursor(sqlite.Cursor):
    def __init__(self, *args, **kwargs):
        sqlite.Cursor.__init__(self, *args, **kwargs)
        self.row_factory = _dict_factory

# XXX Missing:
#   Index merging (read copying)
#   Handling of multiline comment in column_definitions

VALID_NAME_PATTERN = (
        """
        (
            # If name starts with [ or ` or " then I assume anything
            # can form the name. Note that is not really important to
            # know if pairs of [ ] (or " ", ` `) matches, it is assumed
            # that sqltable was validated by sqlite already.
            ((\[ | ` | ") .+ (\] | ` | ")) |
            # Otherwise just [a-zA-Z0-9_] (maybe more depending on the flags).
            (\w+)
        )
        """)
VALID_NAME = re.compile(VALID_NAME_PATTERN, re.VERBOSE)

def column_definitions(sqltable):
    """Given a complete create-table-stmt defined in sqltable, return the
    columns on it and their respectives column-defs."""
    sqltable = sqltable.strip() or ''

    # Discarding all "CREATE [TEMP|TEMPORARY] TABLE [IF NOT EXISTS]"
    discard = re.match(
            """
            ^\s*CREATE\s*
            (TEMP|TEMPORARY)?\s*
            TABLE\s*
            (IF\s*NOT\s*EXISTS\s*)?\s+
            """, sqltable, re.IGNORECASE | re.VERBOSE)
    if discard is None:
        raise Exception("Malformed create-table-stmt")

    sqltable = sqltable[discard.end():]

    # Discarding [dbname].tablename
    discard = re.match(
            """
            # optional dbname
            ^(.+\.)?
            # Looking for tablename now.
            %s
            # Spaces
            \s*
            """ % VALID_NAME_PATTERN, sqltable, re.VERBOSE)
    if discard is None:
        raise Exception("Table name not present")

    if sqltable[:2].lower() == 'as':
        raise Exception("Table will be formed by the result set of "
                "a query, not supported.")

    if sqltable[discard.end()] != '(' or sqltable[-1] != ')':
        raise Exception("Malformed create-table-stmt, "
                "missing parentheses between columns definition")

    interesting = sqltable[discard.end()+1:-1].lstrip()

    # Now we have column-def, column-def, .. [, table-constraint ..] and
    # we want to split each column-def into
    # (column-name, type-name [column-constraint])
    column_defs = {}

    table_constraints = set([
        'constraint', 'primary', 'unique', 'check', 'foreign'])

    while interesting:
        if interesting.startswith('--'):
            # Discard the comment till a newline is found
            nl = interesting.find('\n')
            if nl == -1:
                # No new line, so all the rest is a comment, nothing else
                # to do
                break
            elif nl == len(interesting) - 1:
                # This newline was the last character in the input.
                break
            else:
                interesting = interesting[nl + 1:].lstrip()
        column_name = VALID_NAME.match(interesting)
        if column_name is None:
            raise Exception("Missing column-name")
        interesting = interesting[column_name.end():].lstrip()
        column_name = column_name.group().lower()
        if column_name in table_constraints:
            # We are not interested in table-contrainst.
            # XXX This can be used to indicate that this table can't be fully
            # merged.
            continue

        # Now there is either a type-name, column-constraint, or nothing.

        # We want to either find the next comma that separates this
        # column-def to the next one, or the end of input meaning this
        # was the last column-def.
        in_parens = False
        for indx, char in enumerate(interesting):
            if char == ',' and not in_parens:
                # Found the comma we were after.
                column_defs[column_name] = interesting[:indx] or None
                break
            elif char == '(':
                in_parens = True
            elif char == ')':
                in_parens = False
        else:
            # Comma not found, column-def finished.
            column_defs[column_name] = interesting or None
            break

        interesting = interesting[indx + 1:].lstrip()

    return column_defs


class SqliteDBMerge(object):
    """Merge a newer database structure with an older (but very similar)
    database."""

    def __init__(self, fromdb_path, todb_path, dry_run=False):
        self._fromdb = fromdb_path
        self._todb = todb_path
        self._dryrun = False

        self._fromcursor = None
        self._tocursor = None

        self._merge()


    def _merge(self):
        new = sqlite.connect(self._fromdb)
        self._fromcursor = new_cursor = new.cursor(_DictCursor)

        if not os.path.isfile(self._todb):
            raise Exception("The older db %r is not a file." % self._todb)

        old = sqlite.connect(self._todb)
        self._tocursor = old_cursor = old.cursor(_DictCursor)

        new_tables = new_cursor.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table'").fetchall()
        for table in new_tables:
            name = table['name']
            # Verify that this table is in the older db, or not
            old_table = old_cursor.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name=?", (name, )).fetchone()

            if old_table is None:
                # The older db does not have this table, create it there as
                # well the related triggers.
                print "Adding the table '%s' and related triggers." % name
                if self._dryrun:
                    continue
                self._create_table(name)
                self._create_triggers(name)

            else:
                self._merge_table(name)
                self._merge_triggers(name)


    def _merge_triggers(self, tablename):
        trigger_query = (
                "SELECT name, sql FROM sqlite_master "
                "WHERE type='trigger' AND tbl_name=?")

        res = self._fromcursor.execute(trigger_query, (tablename, )).fetchall()
        new_triggers = {}
        for row in res:
            new_triggers[row['name']] = row['sql']

        res = self._tocursor.execute(trigger_query, (tablename, )).fetchall()
        old_triggers = {}
        for row in res:
            old_triggers[row['name']] = row['sql']

        for name, sql in new_triggers.iteritems():
            if name in old_triggers:
                # XXX could define some action to take if the previous sql
                # differs from the new one here.
                continue

            print "Copying trigger '%s'" % name
            if self._dryrun:
                continue
            self._tocursor.execute(sql)


    def _merge_table(self, tablename):
        new_cursor, old_cursor = self._fromcursor, self._tocursor
        # The old db already have this table but maybe columns or
        # triggers for it changed.
        res = new_cursor.execute("pragma table_info(%s)" % tablename)
        new_table_info = res.fetchall()
        new_by_col = {}
        for col in new_table_info:
            colname = col.pop('name')
            new_by_col[colname] = col

        # sqlite says pragmas may disappear at any time, so, supposing
        # the table name does exist in the database and table_info is
        # an empty result then "pragma table_info" disappeared!
        if not new_table_info:
            warnings.warn("No table information returned, merge will "
                    "not happen.")
            return

        res = old_cursor.execute("pragma table_info(%s)" % tablename)
        old_table_info = res.fetchall()
        old_by_col = {}
        for col in old_table_info:
            colname = col.pop('name')
            old_by_col[colname] = col

        for cname, cinfo in old_by_col.iteritems():
            if cname not in new_by_col:
                # sqlite can't handle deletion of columns, this merge
                # can't be done.
                raise Exception("The table '%s' in the old database "
                        "contains a column named '%s' which no longer "
                        "exists in the new table, sqlite can't handle "
                        "this." % (tablename, cname))
            elif cinfo != new_by_col[cname]:
                # sqlite also can't handle changes in column type and
                # others
                raise Exception("The table '%s' in the old database "
                        "differs in the column named '%s'. (%r != %r)" % (
                            tablename, cname, cinfo, new_by_col[cname]))

            del new_by_col[cname]

        # Attempt to create new columns
        if new_by_col:
            print "Adding new columns in table '%s'" % tablename
        # Get the full column definitions for this table
        res = self._fromcursor.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='table' and name=?", (tablename, )).fetchone()
        coldef = column_definitions(res['sql'])
        for cname, cinfo in new_by_col.iteritems():
            if cinfo['pk']:
                # sqlite doesn't allow creating new columns as
                # primary key
                raise Exception("The table '%s' in the new database "
                        "has a new column named '%s' which is a "
                        "primary key, sqlite can't handle this." % (
                            name, cname))

            print "  Adding the column '%s'" % cname
            if self._dryrun:
                continue

            self._merge_column(tablename, cname, coldef[cname])


    def _merge_column(self, tablename, cname, cinfo):
        if cinfo is not None:
            query = "ALTER TABLE %s ADD COLUMN %s %s"
            args = (tablename, cname, cinfo)
        else:
            query = "ALTER TABLE %s ADD COLUMN %s"
            args = (tablename, cname)
        self._tocursor.execute(query % args)


    def _create_table(self, tablename):
        res = self._fromcursor.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='table' and name=?", (tablename, )).fetchone()
        self._tocursor.execute(res['sql'])


    def _create_triggers(self, tablename):
        res = self._fromcursor.execute(
                "SELECT sql FROM sqlite_master "
                "WHERE type='trigger' and tbl_name=?", (tablename, ))
        for result in res.fetchall():
            self._tocursor.execute(result['sql'])


merge = SqliteDBMerge


if __name__ == "__main__":
    import sys
    merge(*sys.argv[1:3])
