__all__ = ['dir_creator', 'file_merger']

import os
import shutil
import warnings

from umit.merger import sqlitedb, merge_ini
from umit.merger.errors import OriginError, DestinationError

def dir_creator(dest, *dirs):
    """Create any non existing directory in dest."""
    for dirname in dirs:
        dirpath = os.path.join(dest, dirname)
        if not os.path.exists(dirpath):
            os.mkdir(dirpath)
            # XXX handle exceptions

class DummyMerge(object):
    def merge(self, orig, dest):
        if not os.path.isfile(orig):
            raise OriginError(orig)
        if not os.path.isfile(dest):
            raise DestinationError(dest)

def file_merger(from_dir, to_dir, nowarn=False, *files):
    """Merge the files in to_dir according to the supposed newer files in
    from_dir."""
    for filename in files:
        from_file = os.path.join(from_dir, filename)
        to_file = os.path.join(to_dir, filename)

        merger = DummyMerge()
        name, ext = os.path.splitext(filename)
        if ext == '.conf':
            # .conf files are merged using merge_ini merger
            merger = merge_ini
        elif ext == '.db':
            # .db files are merged using sqlitedb merger
            merger = sqlitedb

        try:
            merger.merge(from_file.encode('utf-8'), to_file.encode('utf-8'))
        except OriginError:
            # Received a filename that is not even present in the from_dir,
            # warn the caller about it.
            if not nowarn:
                warnings.warn("The file %r is not present in %r." % (
                    from_file, from_dir))
        except DestinationError:
            # Simply copy the file.
            shutil.copy(from_file, to_file)
            # XXX handle exceptions
