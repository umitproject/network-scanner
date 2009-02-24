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

from umitDB.Utils import empty
from umitDB.Utils import log_debug
from umitDB.Utils import normalize
from umitDB.Connection import ConnectDB

"""
Missing methods for:
    Traceroute retrieval.
"""

debug = log_debug('umitDB.Retrieve')

class RawRetrieve:
    """
    Retrieve raw data from database.
    """

    def __init__(self, conn, cursor):
        """
        Expects a conn and cursor from database connection.
        """
        self.conn = conn
        self.cursor = cursor


    def get_service_info_id_from_db(self, info, service_name_id):
        """
        Get service_info id based on data from info and service_name_id.
        """
        debug("Getting pk for service_info..")

        normalize(info)

        info["ostype"] = empty() # ToFix: Parser isnt storing this

        data = (
            info["product"], info["version"],
            info["extrainfo"], info["method"],
            info["conf"], service_name_id)

        s_id = self.cursor.execute("SELECT pk FROM service_info "
            "WHERE product = ? AND version = ? AND extrainfo = ? AND "
            "method = ? AND conf = ? AND fk_service_name = ?", data).fetchone()

        if s_id:
            return s_id[0]


    def get_port_id_from_db(self, portid, fk_service_info, fk_protocol,
        fk_port_state):
        """
        Get port id from database.
        """
        debug("Getting pk for port..")

        p_id = self.cursor.execute("SELECT pk FROM port "
            "WHERE portid = ? AND fk_service_info = ? AND fk_protocol = ? AND "
            "fk_port_state = ?", (portid, fk_service_info, fk_protocol,
                fk_port_state)).fetchone()

        if p_id:
            return p_id[0]


    def get_service_name_id_from_db(self, service_name):
        """
        Get id from service_name for service_name.
        """
        debug("Getting pk for service_name..")

        s_id = self.cursor.execute("SELECT pk FROM service_name "
            "WHERE name = ?",  (service_name, )).fetchone()

        if s_id:
            return s_id[0]


    def get_hostname_id_from_db(self, hostname):
        """
        Return hostname id from database based on type and name.
        """
        debug("Getting pk for hostname..")

        h_id = self.cursor.execute("SELECT pk FROM hostname "
            "WHERE type = ? AND name = ?", (hostname["type"],
                hostname["name"])).fetchone()
                
        if h_id:
            return h_id[0]


    def get_address_id_from_db(self, address, a_type, vendor):
        """
        Return address id from database based on address, type and vendor.
        """
        debug("Getting pk for address..")

        a_id = self.cursor.execute("SELECT pk FROM address "
            "WHERE address = ? AND type = ? AND fk_vendor = ?", (address,
                a_type, vendor)).fetchone()

        if a_id:
            return a_id[0]


    def get_address_id_for_address_from_db(self, address):
        """
        Return address id from database based on address only.
        """
        a_id = self.cursor.execute("SELECT pk FROM address "
            "WHERE address=?", (address, )).fetchone()

        if a_id:
            return a_id[0]


    def get_address_for_address_id_from_db(self, fk_address):
        """
        Return address from database based on address id.
        """
        addr = self.cursor.execute("SELECT address FROM address WHERE pk=?",
            (fk_address, )).fetchone()

        if addr:
            return addr[0]


    def get_address_pk_for_host_from_db(self, fk_host):
        """
        Return address pk from database based on host id.
        """
        self.cursor.execute("SELECT address.pk FROM address "
            "JOIN _host_address ON (_host_address.fk_address=address.pk) "
            "WHERE _host_address.fk_host=?", (fk_host, ))
        addr = self.cursor.fetchone()

        if addr:
            return addr[0]


    def get_vendor_id_from_db(self, name):
        """
        Return vendor id from database based on name.
        """
        debug("Getting pk for vendor..")

        v_id = self.cursor.execute("SELECT pk FROM vendor WHERE name = ?",
            (name, )).fetchone()

        if v_id:
            return v_id[0]


    def get_host_state_id_from_db(self, state):
        """
        Return state id from database based on state description.
        """
        debug("Getting pk for host_state..")

        h_id = self.cursor.execute("SELECT pk FROM host_state "
            "WHERE state = ?", (state, )).fetchone()

        if h_id:
            return h_id[0]


    def get_tcp_sequence_id_from_db(self, tcpseq_dict):
        """
        Return tcp_sequence id from database based on tcpsequence values.
        """
        debug("Getting pk for tcp_sequence..")

        t_id = self.cursor.execute("SELECT pk FROM tcp_sequence "
            "WHERE tcp_values = ?", (tcpseq_dict["values"], )).fetchone()

        if t_id:
            return t_id[0]


    def get_tcp_ts_sequence_id_from_db(self, tcptsseq_dict):
        """
        Return tcp_sequence id from database based on tcptssequence values.
        """
        debug("Getting pk for tcp_ts_sequence..")
        
        t_id = self.cursor.execute("SELECT pk FROM tcp_ts_sequence "
            "WHERE tcp_ts_values = ?", (tcptsseq_dict["values"], )).fetchone()

        if t_id:
            return t_id[0]


    def get_ip_id_sequence_id_from_db(self, ipidseq_dict):
        """
        Return ip_id_sequence id from database based on ipidseq values.
        """
        debug("Getting pk for ip_id_sequence..")

        t_id = self.cursor.execute("SELECT pk FROM ip_id_sequence "
            "WHERE ip_id_values = ?", (ipidseq_dict["values"], )).fetchone()

        if t_id:
            return t_id[0]


    def get_scan_type_id_from_db(self, name):
        """
        Return scan_type id from database based on name.
        """
        debug("Getting pk for scan_type..")

        s_id = self.cursor.execute("SELECT pk FROM scan_type "
            "WHERE name = ?", (name, )).fetchone()

        if s_id:
            return s_id[0]


    def get_port_state_id_from_db(self, state):
        """
        Return port_state id from database based on state..
        """
        debug("Getting pk for port_state..")

        p_id = self.cursor.execute("SELECT pk FROM port_state "
            "WHERE state = ?", (state, )).fetchone()

        if p_id:
            return p_id[0]


    def get_protocol_id_from_db(self, name):
        """
        Return protocol id from database based on name.
        """
        debug("Getting pk for protocol..")

        p_id = self.cursor.execute("SELECT pk FROM protocol "
            "WHERE name = ?", (name, )).fetchone()

        if p_id:
            return p_id[0]


    def get_scanner_id_from_db(self, name, version):
        """
        Return scanner id from database based on scanner name and version
        """
        debug("Getting pk for scanner..")

        s_id = self.cursor.execute("SELECT pk FROM scanner "
            "WHERE name = ? AND  version = ?", (name, version)).fetchone()

        if s_id:
            return s_id[0]


    def get_osgen_id_from_db(self, osgen):
        """
        Get id from osgen table for osgen.
        """
        debug("Getting pk for osgen..")

        o_id = self.cursor.execute("SELECT pk FROM osgen WHERE gen = ?",
            (osgen, )).fetchone()

        if o_id:
            return o_id[0]


    def get_osfamily_id_from_db(self, osfamily):
        """
        Get id from osfamily table for osfamily.
        """
        debug("Getting pk for osfamily..")

        o_id = self.cursor.execute("SELECT pk FROM osfamily "
            "WHERE family = ?", (osfamily, )).fetchone()

        if o_id:
            return o_id[0]


    def get_osvendor_id_from_db(self, osvendor):
        """
        Get id from osvendor table for osvendor.
        """
        debug("Getting pk for osvendor..")

        o_id = self.cursor.execute("SELECT pk FROM osvendor "
            "WHERE vendor = ?",  (osvendor, )).fetchone()

        if o_id:
            return o_id[0]


    def get_ostype_id_from_db(self, ostype):
        """
        Get id from ostype table for ostype.
        """
        debug("Getting pk for ostype..")

        o_id = self.cursor.execute("SELECT pk FROM ostype WHERE type = ?",
            (ostype, )).fetchone()

        if o_id:
            return o_id[0]

    
    def get_inventory_id_from_db(self, inventory):
        """
        Get id from inventory for inventory.
        """
        debug("Getting pk for inventory..")

        i_id = self.cursor.execute("SELECT pk FROM inventory WHERE name = ?",
            (inventory, )).fetchone()

        if i_id:
            return i_id[0]


class CompositeRetrieve(RawRetrieve):
    """
    Retrieve composite data from database.
    """

    def __init__(self, conn, cursor):
        """
        Expects a conn and cursor from database connection.
        """
        RawRetrieve.__init__(self, conn, cursor)


    def get_hosts_id_for_scan_from_db(self, fk_scan):
        """
        Get all hosts from database that are in fk_scan.
        """
        debug("Getting hosts from scan id %d..", fk_scan)

        ids = self.cursor.execute("SELECT pk FROM host WHERE fk_scan = ?",
            (fk_scan, )).fetchall()

        return ids


    def get_addrtype_for_host_from_db(self, fk_host, addrtype):
        """
        Get IPV4, IPV6 or MAC for a host.
        """
        debug("Getting %s address for host id %d..", addrtype, fk_host)

        fk_address = self.cursor.execute("SELECT fk_address "
            "FROM _host_address WHERE fk_host = ?", (fk_host, )).fetchall()

        address = None
        for fk in fk_address:
            address = self.cursor.execute("SELECT address FROM address "
                "WHERE type = ? AND pk = ?", (addrtype, fk[0], )).fetchone()
            if address:
                break

        if address:
            return address[0]


    def get_ipv4_for_host_from_db(self, fk_host):
        """
        Get IPv4 address for a host.
        """
        return self.get_addrtype_for_host_from_db(fk_host, "ipv4")


    def get_ipv6_for_host_from_db(self, fk_host):
        """
        Get IPV6 address for a host.
        """
        return self.get_addrtype_for_host_from_db(fk_host, "ipv6")


    def get_mac_for_host_from_db(self, fk_host):
        """
        Get MAC address associated with a host.
        """
        return self.get_addrtype_for_host_from_db(fk_host, "mac")


    def get_hostnames_for_host_from_db(self, fk_host):
        """
        Get hostnames associated with a host.
        """
        debug("Getting hostnames for host id %d..", fk_host)

        fk_hostname = self.cursor.execute("SELECT fk_hostname "
            "FROM _host_hostname WHERE fk_host = ?", (fk_host, )).fetchall()

        hostnames = [ ]
        for fk in fk_hostname:
            hostname = self.cursor.execute("SELECT name FROM hostname "
                "WHERE pk = ?", (fk[0], )).fetchone()
            if hostname:
                hostnames.append(hostname[0])

        return tuple(hostnames)


    def get_os_for_host_from_db(self, fk_host):
        """
        Get OS for a host from database.
        """
        os_name = self.cursor.execute("SELECT name FROM osmatch WHERE "
            "fk_host=?", (fk_host, )).fetchone()

        if os_name:
            return os_name[0]


    def get_osshort_for_host_from_db(self, fk_host):
        """
        Gets result from get_os_for_host_from_db and make it shorter.
        """
        os_name = self.get_os_for_host_from_db(fk_host)

        if os_name:
            os_name = os_name.split()[0]

        return os_name


    def get_finish_timestamp_for_scan_from_db(self, scan):
        """
        Get finish timestamp for a scan.
        """
        debug("Getting finish timestamp for scan id %d..", scan)
        
        fts = self.cursor.execute("SELECT finish 'as finish [timestamp]' "
            "FROM scan WHERE pk = ?", (scan, )).fetchone()[0]

        return fts


    def get_scan_details_for_scan_from_db(self, scan):
        """
        Get scan details for a scan.
        """
        debug("Getting scan details for scan id %d..", scan)
        
        details = self.cursor.execute("SELECT args, xmloutputversion, "
            "verbose, debugging, scanner.name, scanner.version "
            "FROM scan JOIN scanner ON (scan.fk_scanner = scanner.pk) "
            "WHERE scan.pk = ?", (scan, )).fetchone()

        return details


    """
    (c1) Missing for port data retrieve: ostype in service_info.
    Reason: NmapParser doesn't handle this yet.
    """

    def get_portid_and_state_for_host_from_db(self, host):
        """
        Get only portid and port state from port table, for a host.
        """
        debug("Getting portid and state for host id %d from table "
            "port..", host)
    
        pst = self.cursor.execute("SELECT port.portid, port_state.state "
            "FROM port "
            "JOIN _host_port ON (_host_port.fk_port=port.pk) "
            "JOIN port_state ON (port.fk_port_state=port_state.pk) "
            " WHERE _host_port.fk_host=?", (host, )).fetchall()

        return pst


    def get_portid_and_fks_for_host_from_db(self, host):
        """
        Get portid and fks from port table, for a host.
        """
        debug("Getting portid and foreign keys for host id %d from "
            "table port..", host)
        
        pdata = self.cursor.execute("SELECT portid, fk_service_info, "
            "fk_protocol, fk_port_state FROM port JOIN _host_port ON "
            "(_host_port.fk_port=port.pk) WHERE _host_port.fk_host=?",
                (host, )).fetchall()

        return pdata


    def get_port_data_for_pdata_from_db(self, protocol_id, port_state_id,
        service_info_id):
        """
        Get port data based on data returned from
        get_portid_and_fks_for_host_from_db
        """
        debug("Getting port data for pdata..")
        
        fullpdata = self.cursor.execute("SELECT protocol.name as protocol, "
            "port_state.state, service_info.product, "
            "service_info.version, service_info.extrainfo, "
            "service_info.method, service_info.conf, service_name.name "
            "FROM protocol, port_state, service_info, service_name "
            "WHERE protocol.pk = ? AND port_state.pk = ? AND "
            "service_info.pk = ? AND "
            "service_name.pk = service_info.fk_service_name", (protocol_id,
                port_state_id, service_info_id)).fetchall()[0]

        return fullpdata


    """
    End (c1)
    """

    def get_extraports_count_for_host_from_db(self, host_id):
        """
        Get extraports Count for host id.
        """
        debug("Getting extraports count for host id %d", host_id)

        epcount = self.cursor.execute("SELECT extraports.count "
            "FROM extraports WHERE extraports.fk_host = ?",
                (host_id, )).fetchall()

        return epcount


    def get_extraports_data_for_host_from_db(self, host_id):
        """
        Get extraport data for host id (returns Count and State).
        """
        debug("Getting extraports data for host id %d", host_id)
        
        epdata = self.cursor.execute("SELECT extraports.count, "
            "port_state.state FROM extraports, port_state "
            "WHERE extraports.fk_host = ? AND "
            "port_state.pk = extraports.fk_port_state", (host_id, )).fetchall()

        return epdata


    def get_fingerprint_info_for_host_from_db(self, host_id):
        """
        Get fingerprinto info for a host id.
        """
        debug("Getting fingerprinto info for host id %d", host_id)

        # W: Not using signature field for now.

        fpinfo = self.cursor.execute("SELECT uptime, lastboot, "
            "tcp_sequence_class, tcp_sequence_index, tcp_sequence_value, "
            "tcp_sequence_difficulty, tcp_ts_sequence_class, "
            "tcp_ts_sequence_value, ip_id_sequence_class, "
            "ip_id_sequence_value FROM fingerprint_info "
            "WHERE fk_host = ?", (host_id, )).fetchone()

        return fpinfo


    def get_osmatch_for_host_from_db(self, host_id):
        """
        Get osmatch data for a host id.
        """
        debug("Getting osmatch for host id %d", host_id)

        match = self.cursor.execute("SELECT name, accuracy, line FROM osmatch "
            "WHERE fk_host = ?", (host_id, )).fetchone()

        return match

    def get_osclasses_for_host_from_db(self, host_id):
        """
        Get osclasses for a host id.
        """
        debug("Getting osclasses for host id %d", host_id)

        classes = self.cursor.execute("SELECT osclass.accuracy, osgen.gen, "
            "osfamily.family, osvendor.vendor, ostype.type FROM osclass "
            "JOIN osgen ON (osclass.fk_osgen = osgen.pk) "
            "JOIN osfamily ON (osclass.fk_osfamily = osfamily.pk) "
            "JOIN osvendor ON (osclass.fk_osvendor = osvendor.pk) "
            "JOIN ostype ON (osclass.fk_ostype = ostype.pk) "
            "WHERE osclass.fk_host = ?", (host_id, )).fetchall()

        return classes


class InventoryRetrieve(CompositeRetrieve):
    """
    Retrieves inventory data from database.
    """

    def __init__(self, conn, cursor):
        CompositeRetrieve.__init__(self, conn, cursor)


    def get_inventories_ids(self):
        """
        Returns all inventories ids from database.
        """
        debug("Getting all inventories ids..")

        ids = self.cursor.execute("SELECT pk FROM inventory").fetchall()

        return ids


    def get_inventories_names(self):
        """
        Returns all inventories names from database.
        """
        debug("Getting all inventories name..")

        names = self.cursor.execute("SELECT name FROM inventory").fetchall()

        return names


    def get_inventories_ids_names(self):
        """
        Returns all inventories ids and names from database.
        """
        debug("Getting all inventories ids and names..")

        id_names = self.cursor.execute("SELECT pk, name FROM \
                            inventory").fetchall()

        return id_names


    def get_inventory_name_for_id(self, inv_id):
        """
        Returns inventory name for id.
        """
        debug("Getting inventory name for id %d..", inv_id)
        
        name = self.cursor.execute("SELECT name FROM inventory WHERE pk = ?",
            (inv_id, )).fetchone()

        if name:
            return name[0]


    def get_inventory_id_for_name(self, name):
        """
        Returns inventory id for name.
        """
        debug("Getting inventory id for name %s..", name)

        i_id = self.cursor.execute("SELECT pk FROM inventory WHERE name = ?",
            (name, )).fetchone()

        if i_id:
            return i_id[0]


    def get_scan_args_for_inventory_id(self, fk_inventory):
        """
        Return scan arguments for an inventory id.
        """
        debug("Getting scan arguments for inventory id %d..", fk_inventory)

        args = self.cursor.execute("SELECT args FROM scan "
            "JOIN _inventory_scan ON (scan.pk = _inventory_scan.fk_scan) "
            "WHERE _inventory_scan.fk_inventory=? LIMIT 1",
                (fk_inventory, )).fetchone()

        if args:
            return args[0]


    def get_scans_id_for_inventory(self, fk_inventory):
        """
        Returns all pks from table scan, where scan is in an inventory.
        """
        debug("Getting scans for inventory id %d..", fk_inventory)
        
        ids = self.cursor.execute("SELECT fk_scan FROM _inventory_scan "
            "WHERE fk_inventory = ?", (fk_inventory, )).fetchall()

        return ids


    def get_hosts_id_for_scan_from_db(self, fk_scan):
        """
        Get all pks from table host, where host is in fk_scan and host in an
        inventory.
        """
        debug("Getting hosts from scan id %d..", fk_scan)

        ids = self.cursor.execute("SELECT pk FROM host WHERE fk_scan = ? "
            "AND fk_scan IN (SELECT fk_scan FROM _inventory_scan)",
                (fk_scan, )).fetchall()

        return ids


    def get_hosts_base_data_for_inventory_from_db(self, host_address,
        fk_inventory):
        """
        Get all pks and fk_scans from table host, where: host has an especified
        host_address and host is in an especified fk_inventory.
        """
        debug("Getting pks in host with host_address %s and "
            "fk_inventory %d", host_address, fk_inventory)
        
        ids = self.cursor.execute("SELECT host.fk_scan, host.pk "
            "FROM host "
            "JOIN _host_address ON (host.pk = _host_address.fk_host) "
            "WHERE _host_address.fk_address = (SELECT "
            "address.pk FROM address WHERE address = ?) "
            "AND host.fk_scan IN (SELECT fk_scan FROM "
            "_inventory_scan WHERE fk_inventory = ?) ORDER BY host.pk DESC",
                (host_address, fk_inventory)).fetchall()

        return ids


    def get_finish_data_for_inventory_from_db(self, fk_inventory):
        """
        Get all finish timestamps and scan id from scans that are in an
        inventory.
        """
        debug("Getting finish timestamps for fk_inventory %d", fk_inventory)
        
        data = self.cursor.execute("SELECT scan.pk, "
            "scan.finish as 'finish [timestamp]' FROM scan "
            "JOIN _inventory_scan ON (_inventory_scan.fk_scan = scan.pk) "
            "WHERE _inventory_scan.fk_inventory = ? ORDER BY scan.pk DESC",
                (fk_inventory, )).fetchall()

        return data


    def get_inventory_change_category_id(self, name):
        """
        Get inventory_change_category pk based on category name.
        """
        debug("Getting change_category id for name %r", name)

        pk = self.cursor.execute("SELECT pk FROM inventory_change_category "
            "WHERE name=?", (name, )).fetchone()

        if pk:
            return pk[0]


    def get_inventory_comparison(self, old_hid, new_hid, date, fk_inventory):
        """
        Returns entry in _inventory_changes if there is a comparison stored
        for old_hid against new_hid in a date for fk_inventory.
        """
        debug("Checking if there is a comparison for old hostid %d against "
                "new hostid %d @ %s for Inventory id %d",
                old_hid, new_hid, date, fk_inventory)
        
        pk = self.cursor.execute("SELECT pk FROM _inventory_changes "
            "WHERE old_hostid=? AND new_hostid=? AND entry_date=? AND "
            "fk_inventory=?", (old_hid, new_hid, date, fk_inventory)).fetchall()

        if pk:
            return True

    def get_inventory_changes(self, fk_inventory, fk_address):
        """
        Returns changes in _inventory_changes for fk_inventory and
        fk_address
        """
        debug("Getting changes for Inventory id %d and Address id %d",
                fk_inventory, fk_address)


        changes = self.cursor.execute("SELECT old_hostid, new_hostid, "
            "entry_date, short_description, inventory_change_category.name "
            "FROM _inventory_changes JOIN inventory_change_category ON "
            "(_inventory_changes.fk_category=inventory_change_category.pk) "
            "WHERE fk_inventory=? AND fk_address=? ORDER BY entry_date DESC",
                (fk_inventory, fk_address)).fetchall()

        return changes


    def get_inventory_changes_for_category(self, fk_inventory, fk_address,
        fk_category):
        """
        Returns changes in _inventory_changes for fk_inventory, fk_address and
        a especific fk_category.
        """
        debug("Getting changes for Inventory id %d, Address id %d and "
                "Category id %d", fk_inventory, fk_address, fk_category)

        changes = self.cursor.execute("SELECT old_hostid, new_hostid, "
            "entry_date, short_description FROM _inventory_changes "
            "WHERE fk_category=? and fk_inventory=? AND fk_address=? "
            "ORDER BY entry_date DESC", (fk_category, fk_inventory,
                fk_address)).fetchall()

        return changes


    def get_inventory_changes_for_category_in_range(self, fk_inventory,
        fk_address, fk_category, start, end):
        """
        Returns changes in _inventory_changes for fk_inventory, fk_address and
        a especific fk_category in a time range.
        """
        debug("Getting changes for Inventory id %d, Address id %d and "
                "Category id %d from %s to %s", fk_inventory, fk_address,
                fk_category, start, end)

        changes = self.cursor.execute("SELECT old_hostid, new_hostid, "
            "entry_date, short_description FROM _inventory_changes "
            "WHERE entry_date >= ? AND entry_date < ? AND fk_category=? AND "
            "fk_inventory=? AND fk_address=? ORDER BY entry_date DESC",
                (start, end, fk_category, fk_inventory, fk_address)).fetchall()

        return changes


class ConnectInventoryDB(ConnectDB, InventoryRetrieve):
    """
    This replaces the previous UpdateChanges class in InventoryChanges module.
    ToDo: Write a better doc =)
    """

    def __init__(self, db):
        ConnectDB.__init__(self, db)
        InventoryRetrieve.__init__(self, self.conn, self.cursor)

