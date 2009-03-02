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

"""
Controls read and write for startup options in Network Inventory.
"""

from ConfigParser import ConfigParser

from umit.core.Paths import Path

TL_SETTINGS = Path.tl_conf
TL_SECTION = "Startup"
INV_SECTION = "inventory"

configparser = ConfigParser()
configparser.read((TL_SETTINGS, Path.get_umit_conf()))

def startup_options():
    """
    Returns startup options dict.
    """
    startup = { }

    section = TL_SECTION

    for opt, value in configparser.items(section):
        startup[opt] = value

    section = INV_SECTION

    inv_opts = configparser.options(section)
    for opt in inv_opts:
        startup[opt] = configparser.getboolean(section, opt)

    return startup


def write_startup_setting(section, setting, value):
    """
    Set a new value for a startup setting.
    """
    configparser.set(section, setting, value)

    if section == TL_SECTION:
        configparser.write(open(TL_SETTINGS, 'w'))
        # update representation
        configparser.read(TL_SETTINGS)
    elif section == INV_SECTION:
        configparser.write(open(Path.get_umit_conf(), 'w'))
        # update representation
        configparser.read(Path.get_umit_conf())
