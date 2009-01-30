# Copyright (C) 2007 Insecure.Com LLC.
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

from datetime import datetime

from umitCore.UmitLogging import log
from umitCore.NmapParser import NmapParser

from umitDB.Connection import ConnectDB
from umitDB.Store import RawStore
from umitDB.Retrieve import InventoryRetrieve
from umitDB.InventoryChanges import UpdateChanges
from umitDB.Utils import empty, debug, normalize

class XMLStore(ConnectDB, InventoryRetrieve, RawStore):
    """
    Stores xml into database.
    """

    def __init__(self, database, store_original=False):
        """
        store_original  -   stores xml files in the database or not
        """

        ConnectDB.__init__(self, database)
        InventoryRetrieve.__init__(self, self.conn, self.cursor)
        RawStore.__init__(self, self.conn, self.cursor)

        self.database = database
        self.store_original = store_original


    def store(self, xml_files, parsed=None, inventory=None):
        """
        Inserts xml file(s) into database.

        xml_files       -   a list or a single nmap xml output
        parsed          -   a NmapParserSAX object or None
        inventory       -   inventory that scans will be added to, or None
                            to create a new one
        """
        log.debug(">>> Inserting file(s) into databaseng: ", xml_files)

        if inventory:
            self.invchanges = UpdateChanges(self)

        if isinstance(xml_files, str):
            # using singe file
            xml_files = [xml_files, ]

        for xml_file in xml_files:
            self.xml_file = xml_file
            if parsed: # used only for single file
                self.parsed = parsed
            else:
                self.parsed = self.parse(xml_file)

            self.scan = self.scan_from_xml()
            self.scaninfo = self.scaninfo_from_xml()
            self.hosts = self.hosts_from_xml()

            if inventory:
                log.debug(">>> Inserting scan into Inventory '%s'" % inventory)
                inv_id = self.get_inventory_id_from_db(inventory)
                if not inv_id: # create new inventory
                    self.insert_inventory_db(inventory)
                    inv_id = self.get_id_for("inventory")
                self.insert_inventory_scan_db(self.scan["pk"], inv_id)

        if inventory:
            # update list of changes for inventory
            log.debug(">>> Updating changes for Inventory '%s'" % inventory)
            self.invchanges.do_update(inv_id)

        self.conn.commit()

        log.debug(xml_files, "inserted into database (hopefully).")


    def hosts_from_xml(self):
        """
        Returns a list of dicts compatible with database schema for host,
        and insert hosts data.
        """
        debug("Building host table...")

        hosts_l = [ ]
        for host in self.parsed.nmap["hosts"]:
            host_d = { }

            host_d["distance"] = empty() # ToFix: Parser not storing this.
            # get host_state fk
            host_state_id = self.get_host_state_id_from_db(host.state)
            if not host_state_id:
                self.insert_host_state_db(host.state)
                host_state_id = self.get_id_for("host_state")

            host_d["fk_host_state"] = host_state_id
            host_d["fk_scan"] = self.scan["pk"]

            # insert host
            self.insert_host_db(host_d)
            host_d["pk"] = self.get_id_for("host")

            hosts_l.append(host_d)

            # host fingerprint
            fp_d = { }
            fp_d["uptime"] = host.uptime["seconds"]
            fp_d["lastboot"] = host.uptime["lastboot"]

            if host.tcpsequence:
                fp_d["tcp_sequence_class"] = host.tcpsequence["class"]
                fp_d["tcp_sequence_index"] = host.tcpsequence["index"]
                fp_d["tcp_sequence_value"] = host.tcpsequence["values"]
                fp_d["tcp_sequence_difficulty"] = host.tcpsequence["difficulty"]

            if host.tcptssequence:
                fp_d["tcp_ts_sequence_class"] = host.tcptssequence["class"]
                fp_d["tcp_ts_sequence_value"] = host.tcptssequence["values"]

            if host.ipidsequence:
                fp_d["ip_id_sequence_class"] = host.ipidsequence["class"]
                fp_d["ip_id_sequence_value"] = host.ipidsequence["values"]

            # insert fingerprint_info
            if len(fp_d) > 2:
                fp_d["fk_host"] = host_d["pk"]
                self.insert_fingerprint_info_db(fp_d)

            # insert hostnames
            for _host in host.hostnames:
                fk_hostname = self.get_hostname_id_from_db(_host)
                if not fk_hostname:
                    self.insert_hostname_db(_host)
                    fk_hostname = self.get_id_for("hostname")

                self.insert_host_hostname_db(host_d["pk"], fk_hostname)

            # insert host addresses (ipv4)
            if host.ip:
                normalize(host.ip)
                # get fk_vendor
                if not host.ip.get("vendor", None):
                    vendor = empty()
                else:
                    vendor = host.ip["vendor"]
                fk_vendor = self.get_vendor_id_from_db(vendor)
                if not fk_vendor:
                    self.insert_vendor_db(vendor)
                    fk_vendor = self.get_id_for("vendor")

                # get fk_address
                fk_address = self.get_address_id_from_db(host.ip["addr"],
                    host.ip["addrtype"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.ip["addr"],
                            host.ip["addrtype"], fk_vendor)
                    fk_address = self.get_id_for("address")

                # insert _host_address
                self.insert_host_address_db(host_d["pk"], fk_address)

            # insert host addresses (ipv6)
            if host.ipv6:
                normalize(host.ipv6)
                # get fk_vendor
                if not host.ipv6["vendor"]:
                    vendor = empty()
                else:
                    vendor = host.ipv6["vendor"]
                fk_vendor = self.get_vendor_id_from_db(vendor)
                if not fk_vendor:
                    self.insert_vendor_db(vendor)
                    fk_vendor = self.get_id_for("vendor")

                # get fk_address
                fk_address = self.get_address_id_from_db(host.ipv6["addr"],
                    host.ipv6["addrtype"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.ipv6["addr"],
                        host.ipv6["addrtype"], fk_vendor)
                    fk_address = self.get_id_for("address")

                # insert _host_address
                self.insert_host_address_db(host_d["pk"], fk_address)

            # insert host addresses (mac)
            if host.mac:
                normalize(host.mac)
                # get fk_vendor
                if not host.ip["vendor"]:
                    vendor = empty()
                else:
                    vendor = host.mac["vendor"]
                fk_vendor = self.get_vendor_id_from_db(vendor)
                if not fk_vendor:
                    self.insert_vendor_db(vendor)
                    fk_vendor = self.get_id_for("vendor")

                # get fk_address
                fk_address = self.get_address_id_from_db(host.mac["addr"],
                    host.mac["addrtype"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.mac["addr"],
                            host.mac["addrtype"], fk_vendor)
                    fk_address = self.get_id_for("address")

                # insert _host_address
                self.insert_host_address_db(host_d["pk"], fk_address)

            # insert host os match
            if host.osmatch:
                # ToFix: Parser is returning only last osmatch ?
                # XXX the new parser stores all osmatches but this is still
                # using only the last osmatch -- for now.
                self.insert_osmatch_db(host_d["pk"], host.osmatch[-1])

            # insert os classes
            for osclass in host.osclass:
                # get fk_osgen
                osgen_id = self.get_osgen_id_from_db(osclass["osgen"])
                if not osgen_id:
                    self.insert_osgen_db(osclass["osgen"])
                    osgen_id = self.get_id_for("osgen")

                # get fk_osfamily
                osfamily_id = self.get_osfamily_id_from_db(osclass["osfamily"])
                if not osfamily_id:
                    self.insert_osfamily_db(osclass["osfamily"])
                    osfamily_id = self.get_id_for("osfamily")

                # get fk_osvendor
                osvendor_id = self.get_osvendor_id_from_db(osclass["vendor"])
                if not osvendor_id:
                    self.insert_osvendor_db(osclass["vendor"])
                    osvendor_id = self.get_id_for("osvendor")

                # get fk_ostype
                ostype_id = self.get_ostype_id_from_db(osclass["type"])
                if not ostype_id:
                    self.insert_ostype_db(osclass["type"])
                    ostype_id = self.get_id_for("ostype")


                self.insert_osclass_db(osclass["accuracy"], osgen_id,
                    osfamily_id, osvendor_id, ostype_id, host_d["pk"])

            # insert ports used
            if host.portused:
                for portused in host.portused:
                    # get fk_port_state
                    port_state_id = self.get_port_state_id_from_db(
                        portused["state"])
                    if not port_state_id:
                        self.insert_port_state_db(portused["state"])
                        port_state_id = self.get_id_for("port_state")

                    # get fk_protocol
                    port_protocol_id = self.get_protocol_id_from_db(
                        portused["proto"])
                    if not port_protocol_id:
                        self.insert_protocol_db(portused["proto"])
                        port_protocol_id = self.get_id_for("protocol")

                    # insert portused
                    self.insert_portused_db(portused["portid"], port_state_id,
                        port_protocol_id, host_d["pk"])

            # some scan may not return any ports
            if host.extraports:
                # insert extraports
                for extraport in host.extraports:
                    port_state = self.get_port_state_id_from_db(
                        extraport["state"])
                    if not port_state:
                        self.insert_port_state_db(extraport["state"])
                        port_state = self.get_id_for("port_state")

                    self.insert_extraports_db(extraport["count"], host_d["pk"],
                        port_state)

            if host.ports:
                # insert ports
                for port in host.ports:
                    # get fk_protocol
                    protocol_id = self.get_protocol_id_from_db(port["protocol"])
                    if not protocol_id:
                        self.insert_protocol_db(port["protocol"])
                        protocol_id = self.get_id_for("protocol")

                    # get fk_port_state
                    port_state_id = self.get_port_state_id_from_db(
                        port["state"])
                    if not port_state_id:
                        self.insert_port_state_db(port["state"])
                        port_state_id = self.get_id_for("port_state")

                    if not "name" in port:
                        port["name"] = empty()

                    service_name_id = self.get_service_name_id_from_db(
                        port["name"])
                    if not service_name_id:
                        self.insert_service_name_db(port["name"])
                        service_name_id = self.get_id_for("service_name")

                    # get fk_service_info
                    keys = ["product", "version", "extrainfo", "method", "conf"]

                    for k in keys:
                        if not k in port:
                            port[k] = empty()


                    service_info_id = self.get_service_info_id_from_db(port,
                        service_name_id)

                    if not service_info_id:
                        data = (
                            port["product"],
                            port["version"],
                            port["extrainfo"],
                            port["method"],
                            port["conf"], service_name_id)

                        self.insert_service_info_db(data)
                        service_info_id = self.get_id_for("service_info")

                    # get fk_port
                    port_id = self.get_port_id_from_db(port["portid"],
                        service_info_id, protocol_id, port_state_id)
                    if not port_id:
                        self.insert_port_db(port["portid"], service_info_id,
                            protocol_id, port_state_id)
                        port_id = self.get_id_for("port")

                    # insert _host_port
                    self.insert_host_port_db(host_d["pk"], port_id)


        return hosts_l


    def scaninfo_from_xml(self):
        """
        Returns a list of dicts compatible with database schema for scaninfo
        and insert scaninfos data.
        """
        parsedsax = self.parsed

        scaninfo_l = [ ]
        for si in parsedsax.nmap["scaninfo"]:
            debug("Building scaninfo table...")

            temp_d = { }
            for key, value in si.items():
                if key == 'type':
                    # try to get scan_type id
                    v = self.get_scan_type_id_from_db(value)
                    if not v: # but it didn't exist
                        self.insert_scan_type_db(value)
                        v = self.get_id_for("scan_type")

                elif key == 'protocol':
                    # try to get protocol id
                    v = self.get_protocol_id_from_db(value)
                    if not v: # but it didn't exist
                        self.insert_protocol_db(value)
                        v = self.get_id_for(key)

                else:
                    v = value

                temp_d[key] = v

            temp_d["fk_scan"] = self.scan["pk"]
            scaninfo_l.append(temp_d)
            self.insert_scaninfo_db(temp_d)


        return scaninfo_l


    def scan_from_xml(self):
        """
        Returns a dict compatible with database schema for scan and
        insert scan data.
        """
        debug("Building scan table..")

        parsedsax = self.parsed

        scan_d = { }
        scan_d["args"] = parsedsax.nmap_command
        timestamp_start = parsedsax.start
        scan_d["start"] = datetime.fromtimestamp(float(timestamp_start))
        scan_d["startstr"] = empty() # ToFix: Parser isnt storing this
        scan_d["finish"] = datetime(*parsedsax.finish_epoch_time[:6])
        scan_d["finishstr"] = parsedsax.finish_time
        scan_d["xmloutputversion"] = (
            parsedsax.nmap["nmaprun"]["xmloutputversion"])
        if self.store_original:
            scan_d["xmloutput"] = '\n'.join(open(self.xml_file,
                'r').readlines())
        else:
            scan_d["xmloutput"] = empty()

        scan_d["verbose"] = parsedsax.verbose_level
        scan_d["debugging"] = parsedsax.debugging_level
        scan_d["hosts_up"] = parsedsax.hosts_up
        scan_d["hosts_down"] = parsedsax.hosts_down

        scanner_name = parsedsax.scanner
        scanner_version = parsedsax.scanner_version

        # get fk_scanner
        scanner_id = self.get_scanner_id_from_db(scanner_name,
            scanner_version)
        if not scanner_id:
            self.insert_scanner_db(scanner_name, scanner_version)
            scanner_id = self.get_id_for("scanner")

        scan_d["scanner"] = scanner_id

        self.insert_scan_db(scan_d)
        # get pk for the just inserted scan.
        scan_d["pk"] = self.get_id_for("scan")

        return scan_d


    def parse(self, valid_xml):
        """
        Parses an existing xml file.
        """
        debug("Parsing file: %s.." % valid_xml)

        p = NmapParser(valid_xml)
        p.parse()

        return p
