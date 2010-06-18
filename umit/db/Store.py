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

from umit.db.Utils import empty
from umit.db.Utils import log_debug

debug = log_debug('umit.db.Store')

"""
Missing methods for:
    Traceroute insertion.
"""

class RawStore:
    """
    Store data into database.
    """

    def __init__(self, conn, cursor):
        """
        Expects a conn and cursor from database connection.
        """
        self.conn = conn
        self.cursor = cursor


    def insert_scan_db(self, scan_d):
        """
        Creates new record in scan with data from scan dict.
        """
        debug("Inserting new scan into database")

        self.cursor.execute("INSERT INTO scan (args, start, startstr, finish, "
            "finishstr, xmloutputversion, xmloutput, verbose, debugging, "
            "hosts_up, hosts_down, fk_scanner) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (scan_d["args"],
                scan_d["start"], scan_d["startstr"], scan_d["finish"],
                scan_d["finishstr"], scan_d["xmloutputversion"],
                scan_d["xmloutput"], scan_d["verbose"],
                scan_d["debugging"], scan_d["hosts_up"],
                scan_d["hosts_down"], scan_d["scanner"]))


    def insert_scaninfo_db(self, scaninfo):
        """
        Creates new record in scaninfo with data from scaninfo dict.
        """
        debug("Inserting new scaninfo into database")

        self.cursor.execute("INSERT INTO scaninfo (numservices, services, "
            "fk_scan, fk_scan_type, fk_protocol) VALUES (?, ?, ?, ?, ?)",
                (scaninfo["numservices"], scaninfo["services"],
                 scaninfo["fk_scan"], scaninfo["type"], scaninfo["protocol"]))


    def insert_scan_type_db(self, scan_name):
        """
        Insert new record in scan_type.
        """
        debug("Inserting new scan_type into database")

        self.cursor.execute("INSERT INTO scan_type (name) VALUES (?)",
            (scan_name, ))


    def insert_scanner_db(self, scanner_name, scanner_version):
        """
        Creates new record in scanner.
        """
        debug("Inserting new scanner into database")

        self.cursor.execute("INSERT INTO scanner (name, version) "
            "VALUES (?, ?)", (scanner_name, scanner_version))


    def insert_port_db(self, portid, service_info_id, protocol_id,
        port_state_id):
        """
        Creates new record in port.
        """
        debug("Inserting new port into database")

        self.cursor.execute("INSERT INTO port (portid, fk_service_info, "
            "fk_protocol, fk_port_state) VALUES (?, ?, ?, ?)", (portid,
                service_info_id, protocol_id, port_state_id))


    def insert_port_state_db(self, port_state):
        """
        Creates new record in port_state.
        """
        debug("Inserting new port_state into database")

        self.cursor.execute("INSERT INTO port_state (state) VALUES (?)",
            (port_state, ))


    def insert_protocol_db(self, protocol):
        """
        Creates new record in protocol.
        """
        debug("Inserting new protocol into database")

        self.cursor.execute("INSERT INTO protocol (name) VALUES (?)",
            (protocol, ))


    def insert_host_port_db(self, fk_host, fk_port):
        """
        Creates new record in _host_port based on fk_host and fk_port.
        """
        debug("Inserting new _host_port into database")

        self.cursor.execute("INSERT INTO _host_port (fk_host, fk_port) "
            "VALUES (?, ?)", (fk_host, fk_port))


    def insert_extraports_db(self, count, fk_host, fk_port_state):
        """
        Creates new record in extraports.
        """
        debug("Inserting new extraports into database")

        self.cursor.execute("INSERT INTO extraports (count, fk_host, "
            "fk_port_state) VALUES (?, ?, ?)", (count, fk_host, fk_port_state))


    def insert_portused_db(self, portid, fk_port_state, fk_protocol, fk_host):
        """
        Create new record in portused.
        """
        debug("Inserting new portused into database")

        self.cursor.execute("INSERT INTO portused (portid, fk_port_state, "
            "fk_protocol, fk_host) VALUES (?, ?, ?, ?)", (portid,
                fk_port_state, fk_protocol, fk_host))


    def insert_osclass_db(self, osclass_accuracy, fk_osgen, fk_osfamily,
        fk_osvendor, fk_ostype, fk_host):
        """
        Create new record in osclass.
        """
        debug("Inserting new osclass into database")

        self.cursor.execute("INSERT INTO osclass (accuracy, fk_osgen, "
            "fk_osfamily, fk_osvendor, fk_ostype, fk_host) "
            "VALUES (?, ?, ?, ?, ?, ?)", (osclass_accuracy, fk_osgen,
                fk_osfamily, fk_osvendor, fk_ostype, fk_host))


    def insert_osmatch_db(self, host, osmatch):
        """
        Create new record in osmatch with data from osmatch dict.
        """
        debug("Inserting new osmatch into database")

        osmatch["line"] = empty() # ToFix: Parser isnt storing this
        self.cursor.execute("INSERT INTO osmatch (name, accuracy, line, "
            "fk_host) VALUES (?, ?, ?, ?)", (osmatch["name"],
                osmatch["accuracy"], osmatch["line"], host))


    def insert_osgen_db(self, osgen):
        """
        Creates new record in osgen.
        """
        debug("Inserting new osgen into database")

        self.cursor.execute("INSERT INTO osgen (gen) VALUES (?)", (osgen, ))


    def insert_osfamily_db(self, osfamily):
        """
        Creates new record in osfamily.
        """
        debug("Inserting new osfamily into database")

        self.cursor.execute("INSERT INTO osfamily (family) VALUES (?)",
            (osfamily, ))


    def insert_osvendor_db(self, osvendor):
        """
        Creates new record in osvendor.
        """
        debug("Inserting new osvendor into database")

        self.cursor.execute("INSERT INTO osvendor (vendor) VALUES (?)",
            (osvendor, ))


    def insert_ostype_db(self, ostype):
        """
        Creates new record in ostype.
        """
        debug("Inserting new ostype into database")

        self.cursor.execute("INSERT INTO ostype (type) VALUES (?)", (ostype, ))


    def insert_host_db(self, host_d):
        """
        Create new record in host with data from host dict.
        """
        debug("Inserting new host into database")

        self.cursor.execute("INSERT INTO host (distance, fk_scan, "
            "fk_host_state) VALUES (?, ?, ?)", (host_d["distance"],
                host_d["fk_scan"], host_d["fk_host_state"]))


    def insert_host_address_db(self, fk_host, fk_address):
        """
        Creates new record in _host_address.
        """
        debug("Inserting new _host_address into database")

        self.cursor.execute("INSERT INTO _host_address (fk_host, fk_address) "
            "VALUES (?, ?)", (fk_host, fk_address))


    def insert_host_hostname_db(self, fk_host, fk_hostname):
        """
        Creates new record in _host_hostname.
        """
        debug("Inserting new _host_hostname into database")

        self.cursor.execute("INSERT INTO _host_hostname (fk_host, "
            "fk_hostname) VALUES (?, ?)", (fk_host, fk_hostname))


    def insert_hostname_db(self, hostname):
        """
        Insert new record in hostnamed based on data from hostname.
        """
        debug("Inserting new hostname into database")

        self.cursor.execute("INSERT INTO hostname (type, name) "
            "VALUES (?, ?)", (hostname["type"], hostname["name"]))


    def insert_fingerprint_info_db(self, fp_d):
        """
        Creates new record in fingerprint_info with data from fp_d.
        """
        debug("Inserting new fingerprint information for host into database")

        columns = (
            "uptime", "lastboot", "tcp_sequence_class",
            "tcp_sequence_index", "tcp_sequence_value",
            "tcp_sequence_difficulty", "tcp_ts_sequence_class",
            "tcp_ts_sequence_value", "ip_id_sequence_class",
            "ip_id_sequence_value", "fk_host" )

        data = [fp_d.get(column) for column in columns]

        self.cursor.execute("INSERT INTO fingerprint_info (uptime, lastboot, "
            "tcp_sequence_class, tcp_sequence_index, tcp_sequence_value, "
            "tcp_sequence_difficulty, tcp_ts_sequence_class, "
            "tcp_ts_sequence_value, ip_id_sequence_class, "
            "ip_id_sequence_value, fk_host) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (data))


    def insert_service_name_db(self, service_name):
        """
        Creates new record in service_name.
        """
        debug("Inserting new service_name into database")

        self.cursor.execute("INSERT INTO service_name (name) VALUES (?)",
            (service_name, ))


    def insert_service_info_db(self, service_data):
        """
        Creates new record in service_info based on service_data
        """
        debug("Inserting new service_info into database")

        self.cursor.execute("INSERT INTO service_info (product, version, "
            "extrainfo, method, conf, fk_service_name) "
            "VALUES (?, ?, ?, ?, ?, ?)", service_data)


    def insert_address_db(self, address_addr, address_type, vendor):
        """
        Creates new record on address.
        """
        debug("Inserting new address into database")

        self.cursor.execute("INSERT INTO address (address, type, fk_vendor) "
            "VALUES (?, ?, ?)", (address_addr, address_type, vendor))


    def insert_vendor_db(self, vendor_name):
        """
        Creates new record in  vendor.
        """
        debug("Inserting new vendor into database")

        self.cursor.execute("INSERT INTO vendor (name) VALUES (?)",
            (vendor_name, ))


    def insert_host_state_db(self, host_state):
        """
        Creates new record in host_state.
        """
        debug("Inserting new host_state into database")

        self.cursor.execute("INSERT INTO host_state (state) VALUES (?)",
            (host_state, ))


    def insert_tcp_sequence_db(self, tcpseq_dict):
        """
        Creates new record in tcp_sequence based on data from tcpseq_dict.
        """
        debug("Inserting new tcp_sequence into database")

        self.cursor.execute("INSERT INTO tcp_sequence (tcp_index, "
            "class, difficulty, tcp_values) VALUES (?, ?, ?, ?)",
                (tcpseq_dict["index"], tcpseq_dict["class"],
                 tcpseq_dict["difficulty"], tcpseq_dict["values"]))


    def insert_tcp_ts_sequence_db(self, tcptsseq_dict):
        """
        Creates new record in tcp_ts_sequence based on data from tcptsseq
        dict.
        """
        debug("Inserting new tcp_ts_sequence into database")

        self.cursor.execute("INSERT INTO tcp_ts_sequence (class, "
            "tcp_ts_values)  VALUES (?, ?)", (tcptsseq_dict["class"],
                tcptsseq_dict["values"]))


    def insert_ip_id_sequence_db(self, ipidseq_dict):
        """
        Creates new record in ip_id_sequence based on data from ipidseq dict.
        """
        debug("Inserting new ip_id_sequence into database")

        self.cursor.execute("INSERT INTO ip_id_sequence (class, "
            "ip_id_values)  VALUES (?, ?)", (ipidseq_dict["class"],
                ipidseq_dict["values"]))


    def insert_inventory_db(self, inventory):
        """
        Creates new record in inventory.
        """
        debug("Inserting new inventory into database")

        self.cursor.execute("INSERT INTO inventory (name) VALUES (?)",
            (inventory, ))


    def insert_inventory_scan_db(self, scan, inventory):
        """
        Creates new record in _inventory_scan.
        """
        debug("Inserting new _inventory_scan into database")

        self.cursor.execute("INSERT INTO _inventory_scan (fk_scan, "
            "fk_inventory) VALUES (?, ?)", (scan, inventory))


    def insert_inventory_change_category_db(self, category):
        """
        Creates new record in inventory_change_category.
        """
        debug("Inserting new category %r into inventory_change_category",
                category)

        self.cursor.execute("INSERT INTO inventory_change_category (name) "
            "VALUES (?)", (category, ))


    def insert_inventory_comparison_db(self, old_hid, new_hid, date,
        short_descr, fk_inventory, fk_category, fk_address):
        """
        Creates new record in _inventory_changes.
        """
        debug("Inserting new change into _inventory_changes")

        self.cursor.execute("INSERT INTO _inventory_changes (old_hostid, "
            "new_hostid, entry_date, short_description, fk_inventory, "
            "fk_category, fk_address) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (old_hid, new_hid, date, short_descr, fk_inventory,
                 fk_category, fk_address))
