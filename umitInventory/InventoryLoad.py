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
from ConfigParser import ConfigParser

from umitCore.Paths import Path
from umitDB.Connection import ConnectDB
from umitDB.Retrieve import InventoryRetrieve

UMITDB = Path.umitdb_ng

class InventoryLoad(ConnectDB, InventoryRetrieve):
    """
    Load Inventories data to be used in Network Inventory.
    """
    
    def __init__(self):
        ConnectDB.__init__(self, UMITDB)
        InventoryRetrieve.__init__(self, self.conn, self.cursor)

        self.invdata = None
        self.database_stat = None

        
    def load_from_db(self):
        """
        Load all inventories from database and return a dict in this format:
        
        inv_data = {'inventory A': set([(ipv4addr A, ipv6addr A, macaddr A,
                                         (hostnameA, hostnameB, ..),
                                         osmatch A),
                                        (ipv4addr B, ipv6addr B, macaddr B,
                                         (hostnameC, ..), osmatch B), ...
                                        ]),
                    'inventory B': ...
                   }
        
        Each item inside set represent a host inside the 'inventory name'.
        """

        inv_data = { }

        # Grab Inventories names
        # from schemas file
        schemas = ConfigParser()
        schemas.read(Path.sched_schemas)

        for section in schemas.sections():
            if schemas.get(section, 'addtoinv') in ('1', '2'):
                inv_data[section] = set()
        # from database
        invs = self.get_inventories_names()
        for i in invs:
            if not i[0] in inv_data:
                # inventory created from umit interface
                inv_data[i[0]] = set()

        # check if database haven't changed since last time
        if self.database_stat == os.stat(UMITDB).st_mtime:
            # data has been loaded already, maybe a new Inventory was
            # added in schemas file only, let me check here:
            n_invs = set(inv_data.keys()).difference(set(self.invdata.keys()))
            for new_i in n_invs:
                self.invdata[new_i] = set()

            # return cached data with new inventories if any
            return self.invdata

        self.database_stat = os.stat(UMITDB).st_mtime

        # XXX ToDo: it would be good to do some kind of caching here or in
        # database, so we can stop doing so many queries.

        # Retrieve hosts for each Inventory
        for inv in inv_data.keys():
            invid = self.get_inventory_id_for_name(inv)

            if not invid:
                # this Inventory has been created but it is not on database
                # yet because no scan has been finished yet.
                continue

            scans_ids = self.get_scans_id_for_inventory(invid)

            if not scans_ids:
                # this Inventory has no associated scans with it, one possible
                # reason: all scans for the Inventory were deleted
                continue

            for scan in scans_ids:
                scan_hosts = set() # will store hosts in current scan

                # retrieve hosts id for each scan
                hosts = self.get_hosts_id_for_scan_from_db(scan[0])
                hosts = [h[0] for h in hosts]

                if len(hosts) <= len(inv_data[inv]):
                    # no new hosts found
                    continue

                #for host in self.get_hosts_id_for_scan_from_db(scan[0]):
                for host in hosts:

                    os_host = self.get_osshort_for_host_from_db(host)
                    ipv4addr = self.get_ipv4_for_host_from_db(host)
                    ipv6addr = self.get_ipv6_for_host_from_db(host)
                    macaddr = self.get_mac_for_host_from_db(host)
                    hostnames = self.get_hostnames_for_host_from_db(host)

                    scan_hosts.add((ipv4addr, ipv6addr, macaddr, hostnames,
                         os_host))

                if scan_hosts != inv_data[inv] and \
                   len(scan_hosts) > len(inv_data[inv]): # new hosts found
                    inv_data[inv] = scan_hosts

        self.invdata = inv_data
        return inv_data
