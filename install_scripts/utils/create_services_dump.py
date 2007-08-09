#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

import re
import cPickle
import os.path

def create_services_dump(services, services_dump):
    services_dump = os.path.join("share", "umit", "misc", services_dump)

    services_dict = {}
    serv_file = open(services, 'r')
    regex = re.compile("(\w+)\s+(\d+)/(\w{3})\s+#\s*(.*)$")
        
    for s in serv_file.readlines():
        m = regex.match(s)
        if m:
            serv = m.groups()
            tcp, udp, ddp = False, False, False
            
            if serv[2] == "tcp":
                tcp = True
            elif serv[2] == "udp":
                udp = True
            elif serv[2] == "ddp":
                ddp = True

            try:
                services_dict[serv[0]]
            except:
                services_dict[serv[0]] = {"ports":[int(serv[1])],
                                     "comment":serv[3],
                                     "tcp":tcp,
                                     "udp":udp,
                                     "ddp":ddp}
            else:
                if int(serv[1]) not in services_dict[serv[0]]["ports"]:
                    services_dict[serv[0]]["ports"].append(int(serv[1]))
                    
                if tcp:
                    services_dict[serv[0]]["tcp"] = tcp
                elif udp:
                    services_dict[serv[0]]["udp"] = udp
                elif ddp:
                    services_dict[serv[0]]["ddp"] = ddp
    serv_file.close()

    print ">>> Creating %s file" % services_dump
    serv_dump = open(services_dump, "w")
    cPickle.dump(services_dict, serv_dump)
    serv_dump.close()
    print ">>> Created!"

if __name__ == "__main__":
    services = os.path.join("install_scripts", "utils", "nmap-services")
    services_dump = "services.dmp"

    create_services_dump(services, services_dump)
