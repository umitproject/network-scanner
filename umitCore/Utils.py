# Copyright (C) 2007 Insecure.Com LLC.
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
if WIN32:
    import win32api
    import win32con
    import win32process

# Check if we are on Maemo
MAEMO = False
try:
    import hildon
    MAEMO = True
except ImportError:
    pass

def check_process(pid):
    """
    Check if a process is still running.
    Returns True if it is, False otherwise. 
    It will return -1 in case you are not the owner of process or something
    else.
    """

    if WIN32:
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 
                                          False, pid)
        except: # bad PID probably
            return False

        ret = win32process.GetExitCodeProcess(handle)
        if ret == win32con.STILL_ACTIVE:
            return True
        else:
            return False
    else:
        try:
            os.kill(pid, 0)
            return True
        except OSError, e:
            if e.errno == errno.ESRCH: # OS Error 3: No such process
                return False
            
            # Could be OS Error 1: Operation not permitted
            return -1


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
    except: 
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
