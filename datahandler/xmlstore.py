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

from umitCore.NmapParser import NmapParser
from connection import ConnectDB
from store import RawStore
from retrieve import RawRetrieve
from utils import empty
from utils import debug
from utils import normalize

"""
    ToDo: Create methods for doing insertion_on_missing.
"""


class XMLStore(ConnectDB, RawRetrieve, RawStore):
    """
    Stores xml into database.
    """
        
    def __init__(self, database, xml_file=None, store_original=False):
        ConnectDB.__init__(self, database)
        RawRetrieve.__init__(self, self.conn, self.cursor)
        RawStore.__init__(self, self.conn, self.cursor)
        
        self.store_original = store_original
        
        if xml_file:
            self.insert_xml(xml_file)
         
            
    def insert_xml(self, xml_file):
        """
        Inserts xml file into database.
        """
        debug("Inserting file %s" % xml_file)
        
        self.xml_file = xml_file
        self.parsed = self.parse(xml_file)
        self.scan = self.scan_from_xml()
        self.scaninfo = self.scaninfo_from_xml()
        self.hosts = self.hosts_from_xml()
        
        debug("%s inserted into database (hopefully)." % xml_file)

        
    def hosts_from_xml(self):
        """
        Returns a list of dicts compatible with database schema for host,
        and insert hosts data.
        """
        debug("Building host table...")
        
        hosts_l = [ ]
        for host in self.parsed.nmap["hosts"]:
            temp_d = { }
            
            temp_d["distance"] = empty()
            temp_d["uptime"] = host.uptime["seconds"]
            temp_d["lastboot"] = host.uptime["lastboot"]
            temp_d["fk_scan"] = self.scan["pk"]
            
            # get host_state fk
            host_state_id = self.get_host_state_id_from_db(host.state)
            if not host_state_id:
                self.insert_host_state_db(host.state)
                host_state_id = self.get_id_for("host_state")
    
            temp_d["fk_host_state"] = host_state_id
            
            # host fingerprint
            tcp_sequence = host.tcpsequence
            tcp_ts_sequence = host.tcptssequence
            ip_id_sequence = host.ipidsequence
            
            # get fk_tcp_sequence or not
            if tcp_sequence:
                fk_tcp_sequence = self.get_tcp_sequence_id_from_db(tcp_sequence)
                if not fk_tcp_sequence:
                    self.insert_tcp_sequence_db(tcp_sequence)
                    fk_tcp_sequence = self.get_id_for("tcp_sequence")
                    
                temp_d["fk_tcp_sequence"] = fk_tcp_sequence
            else:
                temp_d["fk_tcp_sequence"] = empty()
            # get fk_tcp_ts_sequence or not
            if tcp_ts_sequence:
                fk_tcp_ts_sequence = self.get_tcp_ts_sequence_id_from_db(tcp_ts_sequence)
                if not fk_tcp_ts_sequence:
                    self.insert_tcp_ts_sequence_db(tcp_ts_sequence)
                    fk_tcp_ts_sequence = self.get_id_for("tcp_ts_sequence")
                
                temp_d["fk_tcp_ts_sequence"] = fk_tcp_ts_sequence
            else:
                temp_d["fk_tcp_ts_sequence"] = empty()
            # get fk_ip_id_sequence
            if ip_id_sequence:
                fk_ip_id_sequence = self.get_ip_id_sequence_id_from_db(ip_id_sequence)
                if not fk_ip_id_sequence:
                    self.insert_ip_id_sequence_db(ip_id_sequence)
                    fk_ip_id_sequence = self.get_id_for("ip_id_sequence")
                    
                temp_d["fk_ip_id_sequence"] = fk_ip_id_sequence
            else:
                temp_d["fk_ip_id_sequence"] = empty()
            
            normalize(temp_d)
            
            # insert host
            self.insert_host_db(temp_d)
            temp_d["pk"] = self.get_id_for("host")
            
            hosts_l.append(temp_d)
            
            # insert hostnames
            for _host in host.hostnames:
                fk_hostname = self.get_hostname_id_from_db(_host)
                if not fk_hostname:
                    self.insert_hostname_db(_host)
                    fk_hostname = self.get_id_for("hostname")

                self.insert_host_hostname_db(temp_d["pk"], fk_hostname)
                
            # insert host addresses (ipv4)
            if host.ip:
                normalize(host.ip)
                # get fk_vendor
                if not host.ip["vendor"]:
                    vendor = empty()
                else:
                    vendor = host.ip["vendor"]
                fk_vendor = self.get_vendor_id_from_db(vendor)
                if not fk_vendor:
                    self.insert_vendor_db(vendor)
                    fk_vendor = self.get_id_for("vendor")
        
                # get fk_address
                fk_address = self.get_address_id_from_db(host.ip["addr"],
                                                         host.ip["type"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.ip["addr"], host.ip["type"],
                                           fk_vendor)
                    fk_address = self.get_id_for("address")
              
                # insert _host_address
                self.insert_host_address_db(temp_d["pk"], fk_address)
                
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
                                                         host.ip["type"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.ipv6["addr"], host.ipv6["type"],
                                           fk_vendor)
                    fk_address = self.get_id_for("address")
     
                # insert _host_address
                self.insert_host_address_db(temp_d["pk"], fk_address)
                
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
                                                         host.mac["type"], fk_vendor)
                if not fk_address:
                    self.insert_address_db(host.mac["addr"], host.mac["type"],
                                           fk_vendor)
                    fk_address = self.get_id_for("address")
      
                # insert _host_address
                self.insert_host_address_db(temp_d["pk"], fk_address)
            
            # insert host os match
            if host.osmatch:
                self.insert_osmatch_db(temp_d["pk"], host.osmatch)
                
            # insert os classes
            for osclass in host.osclasses:
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
                                       osfamily_id, osvendor_id, ostype_id, temp_d["pk"])

            # insert ports used
            if host.ports_used:
                for portused in host.ports_used:
                    # get fk_port_state
                    port_state_id = self.get_port_state_id_from_db(portused["state"])
                    if not port_state_id:
                        self.insert_port_state_db(portused["state"])
                        port_state_id = self.get_id_for("port_state")
     
                    # get fk_protocol
                    port_protocol_id = self.get_protocol_id_from_db(portused["proto"])
                    if not port_protocol_id:
                        self.insert_protocol_db(portused["proto"])
                        port_protocol_id = self.get_id_for("protocol")
       
                    # insert portused
                    self.insert_portused_db(portused["portid"], port_state_id, 
                                             port_protocol_id, temp_d["pk"])
                
            # some scan may not return any ports
            if host.ports:
                # insert extraports
                for extraport in host.ports[0]["extraports"]:
                    port_state = self.get_port_state_id_from_db(extraport["state"])
                    if not port_state:
                        self.insert_port_state_db(extraport["state"])
                        port_state = self.get_id_for("port_state")
           
                    self.insert_extraports_db(extraport["count"], temp_d["pk"],
                                              port_state)
                
                # insert ports
                for port in host.ports[0]["port"]:
                    # get fk_protocol
                    protocol_id = self.get_protocol_id_from_db(port["protocol"])
                    if not protocol_id:
                        self.insert_protocol_db(port["protocol"])
                        protocol_id = self.get_id_for("protocol")
         
                    # get fk_port_state
                    port_state_id = self.get_port_state_id_from_db(port["port_state"])
                    if not port_state_id:
                        self.insert_port_state_db(port["port_state"])
                        port_state_id = self.get_id_for("port_state")
                
                    # get fk_service_name
                    service_name_id = self.get_service_name_id_from_db(port["service_name"])
                    if not service_name_id:
                        self.insert_service_name_db(port["service_name"])
                        service_name_id = self.get_id_for("service_name")
 
                    # get fk_service_info
                    service_info_id = self.get_service_info_id_from_db(port, service_name_id)
                    if not service_info_id:
                        data = (port["service_product"], port["service_version"],
                                    port["service_extrainfo"], port["service_method"],
                                    port["service_conf"], service_name_id)
                        self.insert_service_info_db(data)
                        service_info_id = self.get_id_for("service_info")

                    # get fk_port
                    port_id = self.get_port_id_from_db(port["portid"], service_info_id,
                                                       protocol_id, port_state_id)
                    if not port_id:
                        self.insert_port_db(port["portid"], service_info_id,
                                        protocol_id, port_state_id)
                        port_id = self.get_id_for("port")
   
                    # insert _host_port
                    self.insert_host_port_db(temp_d["pk"], port_id)
        
        
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
        scan_d["args"] = parsedsax.nmap["nmaprun"]["args"]
        scan_d["start"] = parsedsax.nmap["nmaprun"]["start"]
        scan_d["startstr"] = empty()
        scan_d["finish"] = parsedsax.nmap["runstats"]["finished_time"]
        scan_d["finishstr"] = empty()
        scan_d["xmloutputversion"] = parsedsax.nmap["nmaprun"]["xmloutputversion"]
        if self.store_original:
            scan_d["xmloutput"] = '\n'.join(open(self.xml_file, 
                                                 'r').readlines())
        else:
            scan_d["xmloutput"] = empty()

        scan_d["verbose"] = parsedsax.nmap["verbose"]
        scan_d["debugging"] = parsedsax.nmap["debugging"]
        scan_d["hosts_up"] = parsedsax.nmap["runstats"]["hosts_up"]
        scan_d["hosts_down"] = parsedsax.nmap["runstats"]["hosts_down"]

        scanner_name = parsedsax.nmap["nmaprun"]["scanner"]
        scanner_version = parsedsax.nmap["nmaprun"]["version"]
        
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

        
    def get_store_orig(self):
        """
        Returns True if it was requested to store original xml file into
        database, otherwise, returns False.
        """
        return self._store_orig


    def set_store_orig(self, store_orig):
        """
        Sets to store or not the original xml file into database.
        """
        self._store_orig = store_original


    def get_xml_file(self):
        """
        Get current working xml file.
        """
        return self._xml_file


    def set_xml_file(self, xml_file):
        """
        Set current working xml file.
        """
        self._xml_file = xml_file
    

    def get_hosts(self):
        """
        Get host list.
        """
        return self._hosts


    def set_hosts(self, lhosts):
        """
        Set a list of hosts.
        """
        self._hosts = lhosts


    def get_scaninfo(self):
        """
        Get scaninfo list.
        """
        return self._scaninfo


    def set_scaninfo(self, scaninfo_dict):
        """
        Set a list of scaninfo.
        """
        self._scaninfo = scaninfo_dict


    def get_scan(self):
        """
        Get scan dict.
        """
        return self._scan


    def set_scan(self, scan_dict):
        """
        Set a dict for scan.
        """
        self._scan = scan_dict


    def parse(self, valid_xml):
        """
        Parses an existing xml file.
        """
        debug("Parsing file: %s.." % valid_xml)
        
        p = NmapParser(valid_xml)
        p.parse()

        return p


    def get_parsed(self):
        """
        Return NmapParserSax object.
        """
        return self._parsed

    
    def set_parsed(self, parsersax):
        """
        Sets a NmapParserSAX.
        """
        self._parsed = parsersax


    # Properties
    store_original = (get_store_orig, set_store_orig)
    xml_file = (get_xml_file, set_xml_file)
    parsed = (get_parsed, set_parsed)
    scan = (get_scan, set_scan)
    scaninfo = (get_scaninfo, set_scaninfo)
    hosts = (get_hosts, set_hosts)
        