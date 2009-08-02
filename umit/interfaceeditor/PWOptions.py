#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
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
from xml.dom import minidom



class PWOptions: 
    """
    This works with profile and wizard options xml files 
    Read and write
    """
    def __init__(self, filename):
        #xml_desc = open(filename)
        self.filename=filename
        self.doc = minidom.parse(filename)
        #xml_desc.close()
    def read(self,tag="option",name="name",option="option"):
        #print tag, name, option	
        result = []
        for node in self.doc.getElementsByTagName(tag):
            tmp_name= node.getAttribute(name)
            tmp_option = node.getAttribute(option)
            #print option
            result.append((tmp_name,tmp_option))
        return result


if __name__ == '__main__':
    p = PWOptions("/home/kop/.umit/wizard.xml")
    print p.read()
    print p.read("group", "name", "group")

