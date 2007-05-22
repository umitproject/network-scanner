import sys

try:
    import sqlite3 as sqlite
except:
    try:
        from pysqlite2 import dbapi2 as sqlite
    except ImportError, e:
        print "ImportError:", e
        sys.exit(0)

