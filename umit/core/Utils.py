# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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

import os
import sys
import errno
import platform

# Check if we are on win32
WIN32 = bool(platform.win32_ver()[0])

# Check if we are on Maemo
MAEMO = False
try:
    import hildon
    MAEMO = True
except ImportError:
    pass

def development_mode(default=True):
    """
    Returns True if the environment var UMIT_DEVELOPMENT is set to true,
    'true' (case insensitive) or some number different than 0 are considered
    as true, False otherwise.

    If the env var is not set, then the default value governs the return
    value. If you want UMIT_DEVELOPMENT to be True by default, call this
    function with default=True (default).
    """
    val = os.environ.get('UMIT_DEVELOPMENT', default)
    try:
        val = int(val)
    except ValueError:
        if val.lower() == 'true':
            return True
    else:
        if val:
            return True

    return False


def is_maemo():
    """
    Returns True in case we are on Maemo, otherwise, False.
    """
    return MAEMO


def amiroot():
    """
    Checks if root is around ;)
    """
    root = False
    try:
        if WIN32:
            root = True
        elif is_maemo():
            root = True
        elif os.getuid() == 0:
            root = True
    except: # XXX
        pass

    return root


def open_url_as():
    """
    If python ver >= 2.5, will open help pages in a new tab.
    """
    tab = 0
    if sys.hexversion >= 0x2050000:
        tab = 2

    return tab
