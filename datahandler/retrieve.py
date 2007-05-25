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
from utils import normalize

"""
Missing methods for:
    Inventory retrieval.
    Traceroute retrieval.
    And some others.
"""

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

        info["ostype"] = empty() # FIX: Parser not handling this yet.

        data = (info["service_product"], info["service_version"],
                info["service_extrainfo"], info["service_method"],
                info["service_conf"], service_name_id)
        
        id = self.cursor.execute("SELECT pk FROM service_info WHERE \
                    product = ? AND version = ? AND extrainfo = ? AND \
                    method = ? AND conf = ? AND fk_service_name = ?",
                    data).fetchone()

        if id:
           return id[0]


    def get_port_id_from_db(self, portid, fk_service_info, fk_protocol,
                            fk_port_state):
        """
        Get port id from database.
        """
        debug("Getting pk for port..")

        id = self.cursor.execute("SELECT pk FROM port WHERE portid = ? \
                        AND fk_service_info = ? AND fk_protocol = ? AND \
                        fk_port_state = ?", (portid,   fk_service_info, fk_protocol, 
                                             fk_port_state)).fetchone()

        if id:
           return id[0]


    def get_service_name_id_from_db(self, service_name):
        """
        Get id from service_name for service_name.
        """
        debug("Getting pk for service_name..")

        id = self.cursor.execute("SELECT pk FROM service_name \
                            WHERE name = ?",  (service_name, )).fetchone()

        if id:
           return id[0]


    def get_hostname_id_from_db(self, hostname):
        """
        Return hostname id from database based on type and name.
        """
        debug("Getting pk for hostname..")
        
        id = self.cursor.execute("SELECT pk FROM hostname WHERE \
                             type = ? AND name = ?", (hostname["hostname_type"],
                             hostname["hostname"])).fetchone()
                
        if id:
           return id[0]
    

    def get_address_id_from_db(self, address, type, vendor):
        """
        Return address id from database based on address, type and vendor.
        """
        debug("Getting pk for address..")

        id = self.cursor.execute("SELECT pk FROM address WHERE \
                            address = ? AND type = ? AND fk_vendor = ?",
                           (address, type, vendor)).fetchone()
        
        if id:
           return id[0]


    def get_vendor_id_from_db(self, name):
        """
        Return vendor id from database based on name.
        """
        debug("Getting pk for vendor..")
        
        id = self.cursor.execute("SELECT pk FROM vendor WHERE \
                        name = ?", (name, )).fetchone()
        
        if id:
           return id[0]


    def get_host_state_id_from_db(self, state):
        """
        Return state id from database based on state description.
        """
        debug("Getting pk for host_state..")
        
        id = self.cursor.execute("SELECT pk FROM host_state WHERE \
                    state = ?", (state, )).fetchone()

        if id:
           return id[0]


    def get_tcp_sequence_id_from_db(self, tcpseq_dict):
        """
        Return tcp_sequence id from database based on tcpsequence values.
        """
        debug("Getting pk for tcp_sequence..")
        
        id = self.cursor.execute("SELECT pk FROM tcp_sequence WHERE \
                    tcp_values = ?", (tcpseq_dict["values"], )).fetchone()
        
        if id:
           return id[0]


    def get_tcp_ts_sequence_id_from_db(self, tcptsseq_dict):
        """
        Return tcp_sequence id from database based on tcptssequence 
        values, 
        """
        debug("Getting pk for tcp_ts_sequence..")
        
        id = self.cursor.execute("SELECT pk FROM tcp_ts_sequence WHERE \
                    tcp_ts_values = ?", (tcptsseq_dict["values"], )).fetchone()
        
        if id:
           return id[0]


    def get_ip_id_sequence_id_from_db(self, ipidseq_dict):
        """
        Return ip_id_sequence id from database based on ipidseq values.
        """
        debug("Getting pk for ip_id_sequence..")
        
        id = self.cursor.execute("SELECT pk FROM ip_id_sequence WHERE \
                    ip_id_values = ?", (ipidseq_dict["values"], )).fetchone()
        
        if id:
           return id[0]


    def get_scan_type_id_from_db(self, name):
        """
        Return scan_type id from database based on name.
        """
        debug("Getting pk for scan_type..")
        
        id = self.cursor.execute("SELECT pk FROM scan_type \
                                    WHERE name = ?", (name, )).fetchone()
                                    
        if id:
           return id[0]


    def get_port_state_id_from_db(self, state):
        """
        Return port_state id from database based on state..
        """
        debug("Getting pk for port_state..")
        
        id = self.cursor.execute("SELECT pk FROM port_state \
                                WHERE state = ?", (state, )).fetchone()

        if id:
           return id[0]


    def get_protocol_id_from_db(self, name):
        """
        Return protocol id from database based on name.
        """
        debug("Getting pk for protocol..")
        
        id = self.cursor.execute("SELECT pk FROM protocol \
                                    WHERE name = ?", (name, )).fetchone()

        if id:
           return id[0]


    def get_scanner_id_from_db(self, name, version):
        """
        Return scanner id from database based on scanner name and version
        """
        debug("Getting pk for scanner..")    
        
        id = self.cursor.execute("SELECT pk FROM scanner WHERE \
                            name = ? AND  version = ?", (name, version)).fetchone()
       
        if id:
           return id[0]


    def get_osgen_id_from_db(self, osgen):
        """
        Get id from osgen table for osgen.
        """
        debug("Getting pk for osgen..")
        
        id = self.cursor.execute("SELECT pk FROM osgen WHERE gen = ?", 
            (osgen, )).fetchone()

        if id:
           return id[0]
        

    def get_osfamily_id_from_db(self, osfamily):
        """
        Get id from osfamily table for osfamily.
        """
        debug("Getting pk for osfamily..")
        
        id = self.cursor.execute("SELECT pk FROM osfamily \
                        WHERE family = ?", (osfamily, )).fetchone()

        if id:
           return id[0]


    def get_osvendor_id_from_db(self, osvendor):
        """
        Get id from osvendor table for osvendor.
        """
        debug("Getting pk for osvendor..")
        
        id = self.cursor.execute("SELECT pk FROM osvendor \
                        WHERE vendor = ?",  (osvendor, )).fetchone()

        if id:
           return id[0]


    def get_ostype_id_from_db(self, ostype):
        """
        Get id from ostype table for ostype.
        """
        debug("Getting pk for ostype..")
        
        id = self.cursor.execute("SELECT pk FROM ostype WHERE type = ?",
                        (ostype, )).fetchone()

        if id:
           return id[0]

