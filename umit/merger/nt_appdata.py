import os
import shutil

from umit.core import BasePaths

def merge():
    """Moves the old ~/.umit to the new configuration directory, this new
    one is the user's local appdata if using nt with umit 1.0beta2 or newer."""
    if os.name != 'nt':
        # There is nothing to do here.
        return

    if BasePaths.UMIT_CFG_DIR == 'umit':
        # This is indeed a version new enough of umit.
        old_path = os.path.join(os.path.expanduser("~"), ".umit")
        if os.path.exists(old_path):
            try:
                shutil.move(old_path,
                        os.path.join(BasePaths.HOME, BasePaths.UMIT_CFG_DIR))
            except OSError, err:
                if err.errno == 17:
                    # Destination already exists, need to merge the files
                    # from the old directory to this new one.
                    # XXX
                    return
                raise
