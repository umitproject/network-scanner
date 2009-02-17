# Copyright (C) 2007 Adriano Monteiro Marques
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
Some functions used along databaseng package.
Note: debug() is deprecrated, should use UmitLogging instead.
"""

DEBUG = False

def empty():
    """
    Returns something that indicates column is empty.
    """
    return ''


def debug(msg):
    """
    Prints a debug message.
    """
    if DEBUG:
        print ">> %s" % msg


def normalize(dictun):
    """
    Call this to normalize a dict. What it does: any empty value
    will be changed to return value of empty().
    """
    for key, value in dictun.items():
        if not value:
            dictun[key] = empty()

