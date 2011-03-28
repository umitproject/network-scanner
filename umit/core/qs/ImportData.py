# -*- coding: utf-8 -*-

# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Daniel Mendes Cassiano <dcassiano@umitproject.org>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os
import sys
import gtk

from tempfile import TemporaryFile

#TODO: implement logging

from umit.core.Paths import Path
from umit.core.RecentScans import RecentScans
from umit.core.TargetList import TargetList

from umit.core.OptionsConf import options_file
from umit.core.NmapOptions import NmapOptions
from umit.core.NmapParser import NmapParser
from umit.core.ScanProfileConf import scan_profile_file

"""
This class is responsible to import all data to QS.
"""

class QSData(object):
    """
    Class responsible to import all stored data of scans, profiles and of nmap
    to QS.
    """

    def __init__(self):
        self.r_scans = RecentScans()
        self.t_list = TargetList()
        self.nmap_options = NmapOptions(options_file)

    def get_recent_scans(self):
        """Return the recent scans"""
        return self.r_scans.get_recent_scans_list()

    def get_target_list(self):
        """Return the list of targets previously scanned"""
        return self.t_list.get_target_list()

    def get_nmap_options(self):
        """Get Nmap options to display to user"""
        return self.nmap_options.get_options_list()

    def get_nmap_command_option(self, option="", args=[]):
        """Return the Nmap command option"""
        if option:
            return self.nmap_options.get_command_option(option, args)
        else:
            return ""
        
    def get_from_db(self):
        """Getting results from database"""
        from umit.core.UmitDB import UmitDB # change when this module is ok
        db = UmitDB()
        self.db_data = {}
        
        for scan in db.get_scans():
            
            #creating temporary file to store nmap xml
            temp_file = TemporaryFile()
            temp_file.write(scan.nmap_xml_output)
            #temp_file.seek(0) #---> really need this?
            
            try:
                parsed = NmapParser()
                parsed.set_xml_file(temp_file)
                parsed.parse()
                self.db_data[parsed.get_target()] = \
                    ((u'ip',parsed.get_hosts()[0].get_hostname()),
                     (u'date', parsed.get_formated_date()),
                     (u'nmap_command', parsed.get_nmap_command()),
                     (u'num_open_ports', parsed.get_open_ports()),
                     (u'ports', parsed.get_ports()),
                     (u'profile_name', parsed.get_profile_name()),
                     (u'stats', parsed.get_runstats()),
                     )
                
                # Remove temporary file reference
                parsed.nmap_xml_file = ""
                temp_file.close()
                
            except IndexError:
                #log the error
                #TODO: fix the bug with reg without ip
                pass

        del db
        return self.db_data
        
    def get_profiles(self, option):
        """Get the existing profiles and respective Nmap commands"""
        profiles = open(scan_profile_file, "r").readlines()
        self.profiles = []
        self.commands = {}
        last_profile = ""

        for p in profiles:
            if p.startswith("[Nmap"):
                self.profiles.append(p[1:-2])
                last_profile = p[1:-2]
            if p.startswith("command"):
                self.commands[last_profile] = p.split("=")[1].strip("%s").strip()

        if option == "profile_name":
            return self.profiles
        elif option == "profile_commands":
            return self.commands
        else:
            return False
        

    def get_all(self):
        """Get all data on a single method"""
        self.all_data = {
            'nmap_options': sorted(self.get_nmap_options()),
            'nmap_command_option': sorted(self.get_nmap_command_option()),
            #'recent_scans': sorted(self.get_recent_scans()),
            'target_list': sorted(self.get_target_list()),
            'profiles': sorted(self.get_profiles("profile_name"))
        }

        return self.all_data

if __name__ == "__main__":
    Path.set_umit_conf(os.path.dirname(sys.argv[0]))
    Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
    a = QSData()
    print a.get_profiles("profile_commands")
    print a.get_target_list()
