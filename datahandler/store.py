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


from utils import empty
from utils import debug
    
    
"""
Missing methods for:
    Inventory insertion.
    Traceroute insertion.
"""

class RawStore:
    """
    Store data into database.
    """
    
    def __init__(self, conn, cursor):
        self.conn = conn
        self.cursor = cursor


    def insert_scan_db(self, scan_d):
        """
        Creates new record in scan with data from scan dict.
        """
        debug("Inserting new scan into database")

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

    
    def insert_scaninfo_db(self, scaninfo):
        """
        Creates new record in scaninfo with data from scaninfo dict.
        """
        debug("Inserting new scaninfo into database")

        #for scaninfo in scaninfo_l:
        self.cursor.execute("INSERT INTO scaninfo (numservices, services, \
                        fk_scan, fk_scan_type, fk_protocol) VALUES \
                        (?, ?, ?, ?, ?)", (scaninfo["numservices"], 
                        scaninfo["services"], scaninfo["fk_scan"],
                        scaninfo["type"], scaninfo["protocol"]))
        self.conn.commit()


    def insert_scan_type_db(self, scan_name):
        """
        Insert new record in scan_type.
        """
        self.cursor.execute("INSERT INTO scan_type (name) VALUES \
                                 (?)", (scan_name, ))
        self.conn.commit()


    def insert_scanner_db(self, scanner_name, scanner_version):
        """
        Creates new record in scanner.
        """
        self.cursor.execute("INSERT INTO scanner (name, version) VALUES \
                                 (?, ?)", (scanner_name, scanner_version))
        self.conn.commit()
        

    def insert_port_db(self, portid, service_info_id, protocol_id, 
                                      port_state_id):
        """
        Creates new record in port.
        """
        self.cursor.execute("INSERT INTO port (portid, fk_service_info, \
                       fk_protocol, fk_port_state) VALUES (?, ?, ?, ?)",
                       (portid, service_info_id, protocol_id,
                        port_state_id))
        self.conn.commit()
            
    
    def insert_port_state_db(self, port_state):
        """
        Creates new record in port_state.
        """
        self.cursor.execute("INSERT INTO port_state (state) VALUES \
                                (?)", (port_state, ))
        self.conn.commit()
    
    
    def insert_protocol_db(self, protocol):
        """
        Creates new record in protocol.
        """
        self.cursor.execute("INSERT INTO protocol (name) VALUES \
                                 (?)", (protocol, ))
        self.conn.commit()
        
    
    def insert_host_port_db(self, fk_host, fk_port):
        """
        Creates new record in _host_port based on fk_host and fk_port.
        """
        debug("Inserting new _host_port into database")
        
        # insert new port id in _host_port
        self.cursor.execute("INSERT INTO _host_port (fk_host, fk_port) \
                    VALUES (?, ?)", (fk_host, fk_port))
        self.conn.commit()
        

    def insert_extraports_db(self, count, fk_host, fk_port_state):
        """
        Creates new record in extraports.
        """
        debug("Inserting new extraports into database")
        self.cursor.execute("INSERT INTO extraports (count, fk_host, \
                            fk_port_state) VALUES (?, ?, ?)",
                            (count, fk_host, fk_port_state))
        self.conn.commit()


    def insert_portused_db(self, portid, fk_port_state, fk_protocol, 
                           fk_host):
        """
        Create new record in portused.
        """
        debug("Inserting new portused into database")
        self.cursor.execute("INSERT INTO portused (portid, fk_port_state, \
                        fk_protocol, fk_host) VALUES (?, ?, ?, ?)",
                        (portid, fk_port_state, fk_protocol, fk_host))
        self.conn.commit()


    def insert_osclass_db(self, osclass_accuracy, fk_osgen, fk_osfamily, 
                          fk_osvendor, fk_ostype, fk_host):
        """
        Create new record in osclass.
        """
        debug("Inserting new osclass into database")
        self.cursor.execute("INSERT INTO osclass (accuracy, fk_osgen, \
                        fk_osfamily, fk_osvendor, fk_ostype, fk_host) VALUES \
                        (?, ?, ?, ?, ?, ?)", (osclass_accuracy, fk_osgen,
                        fk_osfamily, fk_osvendor, fk_ostype, fk_host))
        self.conn.commit()

   
    def insert_osmatch_db(self, host, osmatch):
        """
        Create new record in osmatch with data from osmatch dict.
        """
        osmatch["line"] = empty() # FIX: it seems parser isnt storing this

        debug("Inserting new osmatch into database")
        self.cursor.execute("INSERT INTO osmatch (name, accuracy, line, \
                    fk_host) VALUES (?, ?, ?, ?)", (osmatch["name"], 
                    osmatch["accuracy"], osmatch["line"], host))
        self.conn.commit()
        
        
    def insert_osgen_db(self, osgen):
        """
        Creates new record in osgen.
        """
        self.cursor.execute("INSERT INTO osgen (gen) VALUES (?)", (osgen, ))
        self.conn.commit()
        
    def insert_osfamily_db(self, osfamily):
        """
        Creates new record in osfamily.
        """
        self.cursor.execute("INSERT INTO osfamily (family) VALUES (?)", 
                        (osfamily, ))
        self.conn.commit()
            

    def insert_osvendor_db(self, osvendor):
        """
        Creates new record in osvendor.
        """
        self.cursor.execute("INSERT INTO osvendor (vendor) VALUES (?)", 
                        (osvendor, ))
        self.conn.commit()

    
    def insert_ostype_db(self, ostype):
        """
        Creates new record in ostype.
        """
        self.cursor.execute("INSERT INTO ostype (type) VALUES (?)", 
                        (ostype, ))
        self.conn.commit()
        

    def insert_host_db(self, host):
        """
        Create new record in host with data from host dict.
        """
        if host["fk_tcp_sequence"] != empty():
            debug("Inserting new host with fingerprint information \
into database")

            self.cursor.execute("INSERT INTO host (distance, uptime, \
                    lastboot, fk_scan, fk_host_state, fk_tcp_sequence, \
                    fk_tcp_ts_sequence, fk_ip_id_sequence) VALUES \
                    (?, ?, ?, ?, ?, ?, ?, ?)", (host["distance"],
                    host["uptime"], host["lastboot"], host["fk_scan"],
                    host["fk_host_state"], host["fk_tcp_sequence"],
                    host["fk_tcp_ts_sequence"], host["fk_ip_id_sequence"]))
        else:
            debug("Inserting new host without fingerprint \
information into database")

            self.cursor.execute("INSERT INTO host (distance, uptime, \
                    lastboot, fk_scan, fk_host_state) VALUES \
                    (?, ?, ?, ?, ?)", (host["distance"], host["uptime"],
                    host["lastboot"], host["fk_scan"],
                    host["fk_host_state"]))

        self.conn.commit()


    def insert_host_address_db(self, fk_host, fk_address):
        """
        Creates new record in _host_address.
        """
        debug("Inserting new _host_address into database")
        self.cursor.execute("INSERT INTO _host_address (fk_host, fk_address) \
                            VALUES (?, ?)", (fk_host, fk_address))
        self.conn.commit()


    def insert_host_hostname_db(self, fk_host, fk_hostname):
        """
        Creates new record in _host_hostname.
        """
        debug("Inserting new _host_hostname into database")
        self.cursor.execute("INSERT INTO _host_hostname (fk_host, \
                                fk_hostname) VALUES (?, ?)", (fk_host, 
                                fk_hostname))
        self.conn.commit()
    
    
    def insert_hostname_db(self, hostname):
        """
        Insert new record in hostnamed based on data from hostname.
        """
        self.cursor.execute("INSERT INTO hostname (type, name) VALUES \
                                 (?, ?)", (hostname["hostname_type"], 
                                           hostname["hostname"]))
        self.conn.commit()
    
    
    def insert_service_name_db(self, service_name):
        """
        Creates new record in service_name.
        """        
        self.cursor.execute("INSERT INTO service_name (name) VALUES \
                            (?)", (service_name, ))
        self.conn.commit()
        
        
    def insert_service_info_db(self, service_data):
        """
        Creates new record in service_info based on service_data
        """
        self.cursor.execute("INSERT INTO service_info (product, version, \
                    extrainfo, method, conf, fk_service_name) VALUES (?, ?, ?,\
                    ?, ?, ?)", service_data)
        self.conn.commit()
        
    
    def insert_address_db(self, address_addr, address_type, vendor):
        """
        Creates new record on address.
        """
        self.cursor.execute("INSERT INTO address (address, type, \
                        fk_vendor) VALUES (?, ?, ?)", (address_addr,
                        address_type, vendor))
        self.conn.commit()

    
    def insert_vendor_db(self, vendor_name):
        """
        Creates new record in  vendor.
        """
        self.cursor.execute("INSERT INTO vendor (name) \
                                         VALUES (?)", (vendor_name, ))
        self.conn.commit()

        
    def insert_host_state_db(self, host_state):
        """
        Creates new record in host_state.
        """
        self.cursor.execute("INSERT INTO host_state (state) \
                        VALUES (?)", (host_state, ))
        self.conn.commit()


    def insert_tcp_sequence_db(self, tcpseq_dict):
        """
        Insert new record in tcp_sequence based on data from tcpseq_dict.
        """
        self.cursor.execute("INSERT INTO tcp_sequence (tcp_index, \
                        class, difficulty, tcp_values) VALUES (?, ?, ?, ?)", (
                        tcpseq_dict["index"], tcpseq_dict["class"], 
                        tcpseq_dict["difficulty"], tcpseq_dict["values"]))
        self.conn.commit()

    def insert_tcp_ts_sequence_db(self, tcptsseq_dict):
        """
        Insert new record in tcp_ts_sequence based on data from tcptsseq
        dict.
        """
        self.cursor.execute("INSERT INTO tcp_ts_sequence (class, \
                      tcp_ts_values)  VALUES (?, ?)", (tcptsseq_dict["class"], 
                      tcptsseq_dict["values"]))
        self.conn.commit()

    def insert_ip_id_sequence_db(self, ipidseq_dict):
        """
        Insert new record in ip_id_sequence based on data from ipidseq dict.
        """
        self.cursor.execute("INSERT INTO ip_id_sequence (class, \
                      ip_id_values)  VALUES (?, ?)", (ipidseq_dict["class"], 
                      ipidseq_dict["values"]))
        self.conn.commit()

        