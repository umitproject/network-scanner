"""
Common values that may be needed by the generic setup, windows setup and the
macosx setup.
"""
import os

BIN_DIRNAME = 'bin'
UMIT_MAIN = os.path.join(BIN_DIRNAME, 'umit')
QUICKSCAN_LAUNCHER = os.path.join(BIN_DIRNAME, 'quickscan_launcher.py')
UMIT_SCHEDULER = os.path.join(BIN_DIRNAME, 'umit_scheduler.py')
# These directories are relative to the installation or dist directory
# Ex: python setup.py install --prefix=/tmp/umit
# Will create the directory /tmp/umit with the following directories
PIXMAPS_DIR = os.path.join('share', 'pixmaps', 'umit')
ICONS_DIR = os.path.join('share', 'icons', 'umit')
LOCALE_DIR = os.path.join('share', 'locale')
CONFIG_DIR = os.path.join('share', 'umit', 'config')
BASE_DOCS_DIR = os.path.join('share', 'doc', 'umit')
DOCS_DIR = os.path.join(BASE_DOCS_DIR, 'html')
MISC_DIR = os.path.join('share', 'umit', 'misc')
SQL_DIR = os.path.join('share', 'umit', 'sql')
SQL_DIR = os.path.join('share', 'umit', 'db')
PLUGINS_DIR = os.path.join('share', 'umit', 'plugins')
PLUGINS_TEMP_DIR = os.path.join('share', 'umit', 'config','plugins-temp')
PLUGINS_DOWNLOAD_DIR = os.path.join('share', 'umit', 'config', 'plugins-download')


