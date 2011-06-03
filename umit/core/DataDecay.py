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
A module with a cool name that controls database data removal if it gets 
too old.
"""

from ConfigParser import ConfigParser, NoOptionError, NoSectionError
from umit.core.Paths import Path
from umit.db.Remove import ScanRemover

umitdb = Path.umitdb_ng
umit_conf = Path.get_umit_conf()

def get_decays():
    """
    Return decay for Inventory data and standard UMIT data.
    """
    section = "database"
    
    cfgparse = ConfigParser()
    cfgparse.read(umit_conf)
    
    decays = ()
    
    try:
        decays = (cfgparse.getint(section, "umit_decay"),
                  cfgparse.getint(section, "inventory_decay"))
    except (NoOptionError, NoSectionError):
        decays = (0, 0)
    
    return decays


def set_decay(option, value):
    """
    Set new decay value for some option.
    """
    section = "database"
    
    cfgparse = ConfigParser()
    cfgparse.read(umit_conf)
    
    try:
        cfgparse.getint(section, option)
    except (NoOptionError, NoSectionError):
        return
    
    cfgparse.set(section, option, value)
    cfgparse.write(open(umit_conf, 'w'))
    

def remove_old_data():
    """
    Remove old data if there is any "old" data at all.
    """
    try:
        umit_decay, inventory_decay = get_decays()
    except ValueError:
        # empty tuple returned probably
        return
    
    remover = ScanRemover(umitdb)
    remover.remove_old_umit_scans(umit_decay)
    remover.remove_old_inventory_scans(inventory_decay)
    
