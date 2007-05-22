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

"""
What is missing in this:
  - If you have a xml file with traceroute, traceroute info isn't being added
    for now.
  - Everything related to pop data, right now it is just inserting on
    database.
"""

import os
from umitCore.NmapParser import NmapParser
from _sqlite import sqlite

class DBDataHandler:
    """
    This handles all operations possible in umit database.
    """

    def __init__(self, db):
        """
        Open connection to database and acquire an cursor.
        """
        self.conn = sqlite.connect(db)
        self.cursor = self.conn


    def __del__(self):
        """
        Closes connection to database.
        """
        self.cursor.close()
        self.conn.close()


    def insert_xml(self, xml_file):
        """
        Inserts an nmap xml output into database.
        """
        try:
            os.stat(xml_file)
        except OSError, e:
            print "OSError: %s" % e
            return None

        self.xml_file = xml_file
        self.parsed = self.parse(xml_file)
        self.scan = self.scan_from_xml()
        self.scaninfo = self.scaninfo_from_xml()
        self.hosts = self.hosts_from_xml()


    def hosts_from_xml(self):
        """
        Builds a list of dicts compatible with database schema for host.
        """
        hosts_l = [ ]
        for host in self.parsed.nmap["hosts"]:
            temp_d = { }

            #print "Comment:", host.comment
            temp_d["distance"] = 'Empty'
            temp_d["uptime"] = host.uptime["seconds"]
            temp_d["lastboot"] = host.uptime["lastboot"]
            temp_d["fk_scan"] = self.scan["pk"]
            temp_d["fk_host_state"] = self.get_hoststate_id_from_db(host.state)

            # host fingerprint
            tcp_sequence = host.tcpsequence
            tcp_ts_sequence = host.tcptssequence
            ip_id_sequence = host.ipidsequence

            if tcp_sequence:
                temp_d["fk_tcp_sequence"] = self.get_tcpsequence_id_from_db(tcp_sequence)
            else:
                temp_d["fk_tcp_sequence"] = 'Empty'

            if tcp_ts_sequence:
                temp_d["fk_tcp_ts_sequence"] = self.get_tcptssequence_id_from_db(tcp_ts_sequence)
            else:
                temp_d["fk_tcp_ts_sequence"] = 'Empty'

            if ip_id_sequence:
                temp_d["fk_ip_id_sequence"] = self.get_ipidsequence_id_from_db(ip_id_sequence)
            else:
                temp_d["fk_ip_id_sequence"] = 'Empty'

            self.__normalize(temp_d)
            # insert host
            self.insert_host_db(temp_d)

            hosts_l.append(temp_d)

            # insert hostname
            if host.hostnames:
                self.insert_host_hostname_db(temp_d["pk"], host.hostnames)

            # insert host addresses
            if host.ip:
                self.__normalize(host.ip)
                self.insert_host_address_db(temp_d["pk"], host.ip)
            if host.ipv6:
                self.__normalize(host.ipv6)
                self.insert_host_address_db(temp_d["pk"], host.ipv6)
            if host.mac:
                self.__normalize(host.mac)
                self.insert_host_address_db(temp_d["pk"], host.mac)

            # insert host os match
            if host.osmatch:
                self.insert_osmatch_db(temp_d["pk"], host.osmatch)
                self.insert_osclass_db(temp_d["pk"], host.osclasses)
                self.insert_portsused_db(temp_d["pk"], host.ports_used)

            # insert extraports
            self.insert_extraports_db(temp_d["pk"], 
                                      host.ports[0]["extraports"])
            
            # insert ports
            self.insert_ports_db(temp_d["pk"], host.ports[0]["port"])

        return hosts_l

 
    def scaninfo_from_xml(self):
        """
        Builds a list of dicts compatible with database schema for scaninfo.
        """
        parsedsax = self.parsed

        scaninfo_l = [ ]
        for si in parsedsax.nmap["scaninfo"]:
            temp_d = { }
            for key, value in si.items():
                if key == 'type':
                    v = self.get_scan_type_id_from_db(value)
                elif key == 'protocol':
                    v = self.get_protocol_id_from_db(value)
                else:
                    v = value

                temp_d[key] = v
            
            temp_d["fk_scan"] = self.scan["pk"]
            scaninfo_l.append(temp_d)

        self.insert_scaninfo_db(scaninfo_l)
        return scaninfo_l


    def scan_from_xml(self):
        """
        Builds a dict compatible with database schema for scan.
        """
        parsedsax = self.parsed

        scan_d = { }
        scan_d["args"] = parsedsax.nmap["nmaprun"]["args"]
        scan_d["start"] = parsedsax.nmap["nmaprun"]["start"]
        scan_d["startstr"] = 'Empty'
        scan_d["finish"] = parsedsax.nmap["runstats"]["finished_time"]
        scan_d["finishstr"] = 'Empty'
        scan_d["xmloutputversion"] = parsedsax.nmap["nmaprun"]["xmloutputversion"]
        scan_d["xmloutput"] = '\n'.join(open(self.xml_file, 'r').readlines())
        scan_d["verbose"] = parsedsax.nmap["verbose"]
        scan_d["debugging"] = parsedsax.nmap["debugging"]
        scan_d["hosts_up"] = parsedsax.nmap["runstats"]["hosts_up"]
        scan_d["hosts_down"] = parsedsax.nmap["runstats"]["hosts_down"]
        scan_d["scanner"] = self.get_scanner_id_from_db()

        self.insert_scan_db(scan_d)

        return scan_d


    def insert_scan_db(self, scan_d):
        """
        Creates new record in scan with data from scan dict.
        """
        self.cursor.execute("INSERT INTO scan (args, start, startstr, finish, \
                    finishstr, xmloutputversion, xmloutput, verbose, \
                    debugging, hosts_up, hosts_down, fk_scanner) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (scan_d["args"],
                    scan_d["start"], scan_d["startstr"], scan_d["finish"],
                    scan_d["finishstr"], scan_d["xmloutputversion"],
                    scan_d["xmloutput"], scan_d["verbose"], 
                    scan_d["debugging"], scan_d["hosts_up"], 
                    scan_d["hosts_down"], scan_d["scanner"]))

        self.conn.commit()
        # get scan id
        id = self.get_id_for("scan")
        scan_d["pk"] = id[0]

    
    def insert_scaninfo_db(self, scaninfo_l):
        """
        Creates new records in scaninfo for each scaninfo item.
        """
        for scaninfo in scaninfo_l:
            self.cursor.execute("INSERT INTO scaninfo (numservices, services, \
                        fk_scan, fk_scan_type, fk_protocol) VALUES \
                        (?, ?, ?, ?, ?)", (scaninfo["numservices"], 
                        scaninfo["services"], scaninfo["fk_scan"],
                        scaninfo["type"], scaninfo["protocol"]))
            self.conn.commit()


    def insert_ports_db(self, host, ports):
        """
        Creates new records in port, _host_port and possibly on service_name
        and service_info based on data from ports.
        """
        for port in ports:
            protocol_id = self.get_protocol_id_from_db(port["protocol"])
            port_state_id = self.get_port_state_id_from_db(port["port_state"])
            service_info_id = self.get_service_info_id_from_db(port)
            
            # insert new port
            self.cursor.execute("INSERT INTO port (portid, fk_service_info, \
                    fk_protocol, fk_port_state) VALUES (?, ?, ?, ?)",
                    (port["portid"], service_info_id, protocol_id,
                    port_state_id))
            self.conn.commit()

            id = self.get_id_for("port")

            # insert new port id in _host_port
            self.cursor.execute("INSERT INTO _host_port (fk_host, fk_port) \
                    VALUES (?, ?)", (host, id[0]))
            self.conn.commit()
        

    def insert_extraports_db(self, host, extraports):
        """
        Creates new records in extraports with data from extraports list.
        """
        for extraport in extraports:
            port_state_id = self.get_port_state_id_from_db(extraport["state"])

            self.cursor.execute("INSERT INTO extraports (count, fk_host, \
                            fk_port_state) VALUES (?, ?, ?)",
                            (extraport["count"], host, port_state_id))
            self.conn.commit()


    def insert_portsused_db(self, host, ports_used):
        """
        Create new records in portused with data from ports_used list.
        """
        for port in ports_used:
            port_state_id = self.get_port_state_id_from_db(port["state"])
            port_protocol_id = self.get_protocol_id_from_db(port["proto"])

            self.cursor.execute("INSERT INTO portused (portid, fk_port_state, \
                        fk_protocol, fk_host) VALUES (?, ?, ?, ?)",
                        (port["portid"], port_state_id, port_protocol_id,
                         host))
            self.conn.commit()


    def insert_osclass_db(self, host, osclasses):
        """
        Create new record in osgen with data from osclasses list
        """
        for osclass in osclasses:
            osgen_id = self.get_osgen_id_from_db(osclass["osgen"])
            osfamily_id = self.get_osfamily_id_from_db(osclass["osfamily"])
            osvendor_id = self.get_osvendor_id_from_db(osclass["vendor"])
            ostype_id = self.get_ostype_id_from_db(osclass["type"])

            self.cursor.execute("INSERT INTO osclass (accuracy, fk_osgen, \
                        fk_osfamily, fk_osvendor, fk_ostype, fk_host) VALUES \
                        (?, ?, ?, ?, ?, ?)", (osclass["accuracy"], osgen_id,
                        osfamily_id, osvendor_id, ostype_id, host))
            self.conn.commit()

   
    def insert_osmatch_db(self, host, osmatch):
        """
        Create new record in osmatch with data from osmatch dict.
        """
        osmatch["line"] = 'Empty' # check this, it seems parser isnt storing this
        self.cursor.execute("INSERT INTO osmatch (name, accuracy, line, \
                    fk_host) VALUES (?, ?, ?, ?)", (osmatch["name"], 
                    osmatch["accuracy"], osmatch["line"], host))
        self.conn.commit()
        

    def insert_host_db(self, host):
        """
        Create new record in host with data from host dict.
        """
        if host["fk_tcp_sequence"]:
            self.cursor.execute("INSERT INTO host (distance, uptime, \
                    lastboot, fk_scan, fk_host_state, fk_tcp_sequence, \
                    fk_tcp_ts_sequence, fk_ip_id_sequence) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?)", (host["distance"],
                    host["uptime"], host["lastboot"], host["fk_scan"],
                    host["fk_host_state"], host["fk_tcp_sequence"],
                    host["fk_tcp_ts_sequence"], host["fk_ip_id_sequence"]))
        else:
            self.cursor.execute("INSERT INTO host (distance, uptime, \
                    lastboot, fk_scan, fk_host_state) VALUES \
                    (?, ?, ?, ?, ?)", (host["distance"], host["uptime"],
                    host["lastboot"], host["fk_scan"],
                    host["fk_host_state"]))

        self.conn.commit()
        # get host id
        id = self.get_id_for("host")
        host["pk"] = id[0]


    def insert_host_address_db(self, fk_host, address):
        """
        Creates new record in _host_address with fk_host = fk_host,
        and discover fk_address for address data.
        """
        fk_address = self.get_address_id_from_db(address)

        self.cursor.execute("INSERT INTO _host_address (fk_host, fk_address) \
                            VALUES (?, ?)", (fk_host, fk_address))
        self.conn.commit()


    def insert_host_hostname_db(self, fk_host, hostname):
        """
        Creates new record in _host_hostname with fk_host = fk_host,
        and discover fk_hostname for hostname data.
        """
        fk_hostname = self.get_hostname_id_from_db(hostname)

        self.cursor.execute("INSERT INTO _host_hostname (fk_host, fk_hostname) \
                             VALUES (?, ?)", (fk_host, fk_hostname))
        self.conn.commit()


    def get_service_info_id_from_db(self, info):
        """
        Get service_info id based on data from info, if there is no
        corresponding service_info, create a new one for storing data.
        """
        self.__normalize(info)

        service_name_id = self.get_service_name_id_from_db(info["service_name"])
        # NOT USING ostype FOR NOW
        info["ostype"] = 'Empty'

        data = (info["service_product"], info["service_version"],
                info["service_extrainfo"], info["service_method"],
                info["service_conf"], service_name_id)
        
        id = self.cursor.execute("SELECT product, version, extrainfo, method, \
                    conf, fk_service_name FROM service_info WHERE \
                    product = ? AND version = ? AND extrainfo = ? AND \
                    method = ? AND conf = ? AND fk_service_name = ?",
                    data).fetchone()

        if not id: # info not in database yet
            self.cursor.execute("INSERT INTO service_info (product, version, \
                    extrainfo, method, conf, fk_service_name) VALUES (?, ?, ?,\
                    ?, ?, ?)", data)
            self.conn.commit()

            id = self.get_id_for("service_info")

        return id[0]


    def get_service_name_id_from_db(self, service_name):
        """
        Get id from service_name for service_name if it exists, otherwise,
        create new record for service_name and return its id.
        """
        id = self.cursor.execute("SELECT pk FROM service_name WHERE name = ?",
                            (service_name, )).fetchone()

        if not id: # service_name not in database yet.
            self.cursor.execute("INSERT INTO service_name (name) VALUES \
                            (?)", (service_name, ))
            self.conn.commit()

            id = self.get_id_for("service_name")

        return id[0]


    def get_hostname_id_from_db(self, hostname):
        """
        Return hostname id from database based on type and name,
        if hostname isn't in database, a new record is created.
        """

        hostname = hostname[0] # verify if one host can have more than one
                               # hostname in nmap xml output
                               # Rev 2: yes it can, fix this later.
       
        id = self.cursor.execute("SELECT pk FROM hostname WHERE \
                             type = ? AND name = ?", (hostname["hostname_type"],
                             hostname["hostname"])).fetchone()
        
        if not id: # hostname is not in database yet
            self.cursor.execute("INSERT INTO hostname (type, name) VALUES \
                                 (?, ?)", (hostname["hostname_type"], 
                                           hostname["hostname"]))
            self.conn.commit()
            id = self.get_id_for("hostname")
        
        return id[0]
    

    def get_address_id_from_db(self, address):
        """
        Return address id from database based on address, type and vendor.
        If address isn't in database, a new record is created.
        """
        if not address["vendor"]:
            vendor = 'Empty'
        else:
            vendor = address["vendor"]

        fk_vendor = self.get_vendor_id_from_db(vendor)

        id = self.cursor.execute("SELECT pk FROM address WHERE \
                            address = ? AND type = ? AND fk_vendor = ?",
                           (address["addr"], address["type"], 
                           fk_vendor)).fetchone()

        if not id: # address isn't in database yet
            self.cursor.execute("INSERT INTO address (address, type, \
                        fk_vendor) VALUES (?, ?, ?)", (address["addr"],
                        address["type"], fk_vendor))
            self.conn.commit()

            id = self.get_id_for("address")
        
        return id[0]


    def get_vendor_id_from_db(self, name):
        """
        Return vendor id from database based on name. If name isn't
        in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM vendor WHERE \
                        name = ?", (name, )).fetchone()
        
        if not id: # vendor name is not in database yet
            self.cursor.execute("INSERT INTO vendor (name) \
                        VALUES (?)", (name, ))
            self.conn.commit()

            id = self.get_id_for("vendor")

        return id[0]


    def get_hoststate_id_from_db(self, state):
        """
        Return state id from database based on state description,
        if state isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM host_state WHERE \
                    state = ?", (state, )).fetchone()

        if not id: # state is not in database yet
            self.cursor.execute("INSERT INTO host_state (state) \
                        VALUES (?)", (state, ))
            self.conn.commit()

            id = self.get_id_for("host_state")

        return id[0]


    def get_tcpsequence_id_from_db(self, tcpseq_dict):
        """
        Return tcp_sequence id from database based on tcpsequence values, 
        if tcpsequence values isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM tcp_sequence WHERE \
                    tcp_values = ?", (tcpseq_dict["values"], )).fetchone()
        
        if not id: # tcp_sequence is not in database yet
            self.cursor.execute("INSERT INTO tcp_sequence (tcp_index, \
                        class, difficulty, tcp_values) VALUES (?, ?, ?, ?)", (
                        tcpseq_dict["index"], tcpseq_dict["class"], 
                        tcpseq_dict["difficulty"], tcpseq_dict["values"]))
            self.conn.commit()

            id = self.get_id_for("tcp_sequence")

        return id[0] 


    def get_tcptssequence_id_from_db(self, tcptsseq_dict):
        """
        Return tcp_sequence id from database based on tcpsequence values, 
        if tcpsequence values isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM tcp_ts_sequence WHERE \
                    tcp_ts_values = ?", (tcptsseq_dict["values"], )).fetchone()
        
        if not id: # tcp_sequence is not in database yet
            self.cursor.execute("INSERT INTO tcp_ts_sequence (class, \
                      tcp_ts_values)  VALUES (?, ?)", (tcptsseq_dict["class"], 
                      tcptsseq_dict["values"]))
            self.conn.commit()

            id = self.get_id_for("tcp_ts_sequence")

        return id[0]


    def get_ipidsequence_id_from_db(self, ipidseq_dict):
        """
        Return ip_id_sequence id from database based on tcpsequence values, 
        if tcpsequence values isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM ip_id_sequence WHERE \
                    ip_id_values = ?", (ipidseq_dict["values"], )).fetchone()
        
        if not id: # ip_id_sequence is not in database yet
            self.cursor.execute("INSERT INTO ip_id_sequence (class, \
                      ip_id_values)  VALUES (?, ?)", (ipidseq_dict["class"], 
                      ipidseq_dict["values"]))
            self.conn.commit()

            id = self.get_id_for("ip_id_sequence")

        return id[0]


    def get_scan_type_id_from_db(self, name):
        """
        Return scan_type id from database based on name, if scan_type name
        isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM scan_type WHERE name = ?",
                                  (name, )).fetchone()
        if not id: # scan_type is not in database yet
            self.cursor.execute("INSERT INTO scan_type (name) VALUES \
                                 (?)", (name, ))
            self.conn.commit()

            id = self.get_id_for("scan_type")
        
        return id[0]


    def get_port_state_id_from_db(self, state):
        """
        Return port_state id from database based on state, if state
        name isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM port_state WHERE state = ?",
                                (state, )).fetchone()

        if not id: # state is not in database yet
            self.cursor.execute("INSERT INTO port_state (state) VALUES \
                                (?)", (state, ))
            self.conn.commit()
            id = self.get_id_for("port_state")

        return id[0]


    def get_protocol_id_from_db(self, name):
        """
        Return protocol id from database based on name, if protocol name
        isn't in database, a new record is created.
        """
        id = self.cursor.execute("SELECT pk FROM protocol WHERE name = ?",
                                  (name, )).fetchone()
        if not id: # protocol is not in database yet
            self.cursor.execute("INSERT INTO protocol (name) VALUES \
                                 (?)", (name, ))
            self.conn.commit()

            id = self.get_id_for("protocol")

        return id[0]


    def get_scanner_id_from_db(self):
        """
        Return scanner id from database based on scanner name and version,
        if scanner name and version isn't in database, a new record is created.
        """
        parsedsax = self.parsed
        name = parsedsax.nmap["nmaprun"]["scanner"]
        version = parsedsax.nmap["nmaprun"]["version"]
        
        id = self.cursor.execute("SELECT pk FROM scanner WHERE name = ? AND \
                             version = ? LIMIT 1", (name, version)).fetchone()
       
        if not id: # scanner is not in database yet
            self.cursor.execute("INSERT INTO scanner (name, version) VALUES \
                                 (?, ?)", (name, version))
            self.conn.commit()

            id = self.get_id_for("scanner")

        return id[0]


    def get_osgen_id_from_db(self, osgen):
        """
        Get id from osgen table for osgen if it exists, otherwise create new 
        record in osgen and return it.
        """
        id = self.cursor.execute("SELECT pk FROM osgen WHERE gen = ?", 
            (osgen, )).fetchone()

        if not id: # osgen not in database yet.
            self.cursor.execute("INSERT INTO osgen (gen) VALUES (?)", (osgen, ))
            self.conn.commit()

            id = self.get_id_for("osgen")

        return id[0]
        

    def get_osfamily_id_from_db(self, osfamily):
        """
        Get id from osfamily table for osfamily if it exists, otherwise 
        create new record in osfamily and return it.
        """
        id = self.cursor.execute("SELECT pk FROM osfamily WHERE family = ?",
                        (osfamily, )).fetchone()

        if not id: # osfamily not in database yet.
            self.cursor.execute("INSERT INTO osfamily (family) VALUES (?)", 
                        (osfamily, ))
            self.conn.commit()

            id = self.get_id_for("osfamily")

        return id[0]


    def get_osvendor_id_from_db(self, osvendor):
        """
        Get id from osvendor table for osvendor if it exists, otherwise 
        create new record in osvendor and return it.
        """
        id = self.cursor.execute("SELECT pk FROM osvendor WHERE vendor = ?",
                        (osvendor, )).fetchone()

        if not id: # osvendor not in database yet.
            self.cursor.execute("INSERT INTO osvendor (vendor) VALUES (?)", 
                        (osvendor, ))
            self.conn.commit()

            id = self.get_id_for("osvendor")

        return id[0]


    def get_ostype_id_from_db(self, ostype):
        """
        Get id from ostype table for ostype if it exists, otherwise 
        create new record in ostype and return it.
        """
        id = self.cursor.execute("SELECT pk FROM ostype WHERE type = ?",
                        (ostype, )).fetchone()

        if not id: # osfamily not in database yet.
            self.cursor.execute("INSERT INTO ostype (type) VALUES (?)", 
                        (ostype, ))
            self.conn.commit()

            id = self.get_id_for("ostype")


        return id[0]


    def get_id_for(self, table_name):
        """
        Return last insert rowid in a table.
        """
        return self.cursor.execute("SELECT last_insert_rowid() \
                FROM %s" % table_name).fetchone()


    def get_xml_file(self):
        """
        Get current working xml file
        """
        return self._xml_file


    def set_xml_file(self, xml_file):
        """
        Set current working xml file.
        """
        self._xml_file = xml_file
    

    def get_hosts(self):
        """
        Get host list
        """
        return self._hosts


    def set_hosts(self, lhosts):
        """
        Set a list of hosts
        """
        self._hosts = lhosts


    def get_scaninfo(self):
        """
        Get scaninfo list
        """
        return self._scaninfo


    def set_scaninfo(self, scaninfo_dict):
        """
        Set a list of scaninfo
        """
        self._scaninfo = scaninfo_dict


    def get_scan(self):
        """
        Get scan dict
        """
        return self._scan


    def set_scan(self, scan_dict):
        """
        Set a dict for scan
        """
        self._scan = scan_dict


    def parse(self, valid_xml):
        """
        Parses an existent xml file.
        """
        p = NmapParser(valid_xml)
        p.parse()

        return p


    def get_parsed(self):
        """
        Get xml file parsed.
        """
        return self._parsed

    
    def set_parsed(self, parsersax):
        """
        Sets a NmapParserSAX
        """
        self._parsed = parsersax


    def __normalize(self, dictun):
        """
        Call this to normalize a dict, what it does: any empty value 
        will be changed to 'Empty'.
        """
        # normalize hosts
        for key, value in dictun.items():
            if not value:
                 #dictun[key] = None # ! having problems with this on sqlite
                 dictun[key] = 'Empty'



    # Properties
    xml_file = (get_xml_file, set_xml_file)
    parsed = (get_parsed, set_parsed)
    scan = (get_scan, set_scan)
    scaninfo = (get_scaninfo, set_scaninfo)
    hosts = (get_hosts, set_hosts)


# demo
if __name__ == "__main__":
    a = DBDataHandler("schema-testing.db")
    a.insert_xml("xml_test3.xml")
