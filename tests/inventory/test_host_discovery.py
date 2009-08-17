#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import unittest

# Setting up Paths so UmitConf can be correctly loaded
from os.path import join
import os
import sys
from umit.core.Paths import Path
Path.set_umit_conf(os.path.dirname(sys.argv[0]))

# Loading Host Discovery
from umit.inventory.HostDiscovery import tryto_detect_networks, _darwin_get_addresses
from umit.inventory.HostDiscovery import NetIface


class TestGetIPv4(unittest.TestCase):
    
    def testGetIP(self):
        ifaces = tryto_detect_networks() # No Loopback

        # Get Real IP address
        import subprocess
        import tempfile
        
        # Create temporary files 
        stdout_output = tempfile.NamedTemporaryFile(delete=False)
        stderr_output = tempfile.NamedTemporaryFile(delete=False)
        
        command = "ifconfig" # POSIX
        if os.name == "nt":
            command = "ipconfig" # Windows 
            
        shell_state = (sys.platform == "win32")
        subprocess.Popen(command, bufsize= 1,
                                         stdin=subprocess.PIPE,
                                         stdout=stdout_output.fileno(),
                                         stderr=stderr_output.fileno(),
                                         shell=shell_state)

        # Read contents of 
        normal_desc = open(stdout_output.name, "r")
        normal = normal_desc.read()
        normal_desc.close()
        # Now look for ips:
        for i in ifaces:
            found = normal.rfind(i.ipv4_addr)
            self.assert_(found != -1, 
                         "Failing: IP %s not found" % i.ipv4_addr)
            
        
        
        # Remove Temporary Files
        stderr_output.close()
        os.remove(stderr_output.name)
        stdout_output.close()
        os.remove(stdout_output.name)
        
    def testGetIPLoopback(self):
        
        # Just check loopback
        
        ifaces = tryto_detect_networks(no_loopback=False)
        loopback = False
        for i in ifaces:
            if i.ipv4_addr == "127.0.0.1":
                loopback = True
                break 
        self.assert_(loopback==True,
                     "Failed because loopback doesn't exists!")
            


if __name__ == "__main__":
    print ">>> Testing Host Discovery "
    test_ipv4 = unittest.TestLoader().loadTestsFromTestCase(TestGetIPv4)
    unittest.TextTestRunner(verbosity=5).run(test_ipv4)
    print
#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Adriano Monteiro Marques.
#
# Author: Luís A. Bastião Silva <luis.kop@gmail.com>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import unittest

# Setting up Paths so UmitConf can be correctly loaded
from os.path import join
import os
import sys
from umit.core.Paths import Path
Path.set_umit_conf(os.path.dirname(sys.argv[0]))

# Loading Host Discovery
from umit.inventory.HostDiscovery import tryto_detect_networks, _darwin_get_addresses
from umit.inventory.HostDiscovery import NetIface


class TestGetIPv4(unittest.TestCase):
    
    def testGetIP(self):
        ifaces = tryto_detect_networks() # No Loopback

        # Get Real IP address
        import subprocess
        import tempfile
        
        # Create temporary files 
        stdout_output = tempfile.NamedTemporaryFile(delete=False)
        stderr_output = tempfile.NamedTemporaryFile(delete=False)
        
        command = "ifconfig" # POSIX
        if os.name == "nt":
            command = "ipconfig" # Windows 
            
        shell_state = (sys.platform == "win32")
        subprocess.Popen(command, bufsize= 1,
                                         stdin=subprocess.PIPE,
                                         stdout=stdout_output.fileno(),
                                         stderr=stderr_output.fileno(),
                                         shell=shell_state)

        # Read contents of 
        normal_desc = open(stdout_output.name, "r")
        normal = normal_desc.read()
        normal_desc.close()
        # Now look for ips:
        for i in ifaces:
            found = normal.rfind(i.ipv4_addr)
            self.assert_(found != -1, 
                         "Failing: IP %s not found" % i.ipv4_addr)
            
        
        
        # Remove Temporary Files
        stderr_output.close()
        os.remove(stderr_output.name)
        stdout_output.close()
        os.remove(stdout_output.name)
        
    def testGetIPLoopback(self):
        
        # Just check loopback
        
        ifaces = tryto_detect_networks(no_loopback=False)
        loopback = False
        for i in ifaces:
            if i.ipv4_addr == "127.0.0.1":
                loopback = True
                break 
        self.assert_(loopback==True,
                     "Failed because loopback doesn't exists!")
            


if __name__ == "__main__":
    print ">>> Testing Host Discovery "
    test_ipv4 = unittest.TestLoader().loadTestsFromTestCase(TestGetIPv4)
    unittest.TextTestRunner(verbosity=5).run(test_ipv4)
    print
