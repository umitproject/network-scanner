import sys
import os

__all__ = ['db_test']

# Database file
db_test = os.path.abspath(os.path.dirname(sys.argv[0]))+"/db/schema-testing.db"
try:
    os.stat(db_test)
except OSError, e:
    print e
    sys.exit(0)
