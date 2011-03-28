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

import sys
import os
import threading
from datetime import datetime

from umit.core.NmapCommand import NmapCommand
from umit.core.Paths import Path

class Nmap(object):
    """
    Class to manipulate Nmap scans.
    """

    def __init__(self, nmap_path, command, host):
        Path.set_umit_conf(os.path.dirname(sys.argv[0]))
        Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
        self.nmap_path = nmap_path
        self.command = command
        self.host = host
        #threading.Thread.__init__(self)
        
    def run(self):
        self.scan_exec = NmapCommand('%s %s %s' % (self.nmap_path,
                                                   self.command,
                                                   self.host))
        
        try:
            self.scan_exec.run_scan()
        except OSError, msg:
            raise(msg)
        
        try:
            while self.scan_exec.scan_state():
                print ">>>", self.scan_exec.get_normal_output()
        except Exception:
            print "Exception caught"
            
            
        from umit.core.UmitDB import Scans

        state = self.scan_exec.scan_state()
        if state == False:
            store = Scans(scan_name="Quick Scan on %s" % self.host,
                          nmap_xml_output=self.scan_exec.get_xml_output(),
                          date=datetime.now())
                
            return self.scan_exec.get_normal_output()
        
        return False

if __name__ == "__main__":
    Path.set_umit_conf(os.path.dirname(sys.argv[0]))
    Path.set_running_path(os.path.abspath(os.path.dirname(sys.argv[0])))
    b = Nmap(Path.nmap_command_path, "Agressive -v", "google.com")
    b.run()
    