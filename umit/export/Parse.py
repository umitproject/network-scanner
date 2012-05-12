# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
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



"""
This module construct
HTML engine of Nmap Results
"""


class Export:
    def __init__(self, parse, filename):
        self.parse = parse
        self.filename = filename
        self._dict = {
            '_osclasses': {'osfamily': 'OS Family',
                           'vendor' : 'Vendor',}, 
            '_osmatch': {'name':'Operation System'},
            '_ip' :{'addr':'Ip Addr'},
            
            }
    # MAIN API 
    def get(self):
        pass
    
    def save(self):
        """ 
        Rewrite subclass 
        """
        file = open(self.filename, "w")
        file.write(self.get())
        file.close()

    
    def get_dname(self, key, section=None):
        if section==None:
            if self._dict.has_key(key):
                return self._dict[key]
            else:
                return key
        else:
            if self._dict.has_key(section):
                if self._dict[section].has_key(key):
                    return self._dict[section][key]
                else:
                    return key
            else:
                return key 
    
    # Parsing API 
    
    def get_list_host(self):
        """ 
        Convert it to a list of dict
        """
        result = []
        for host in self.parse.get_hosts():
            result.append(self.get_hosts_dic(host))
        return result
            
    def get_hosts_dic (self, hostinfo):
        dict = hostinfo.__dict__
        return dict
    
            
