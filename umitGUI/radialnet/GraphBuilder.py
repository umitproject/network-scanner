# -*- coding: utf-8 -*-
#Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: João Paulo de Souza Medeiros <ignotus21@gmail.com>
#         Luis A. Bastiao Silva <luis.kop@gmail.com>
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

A GraphBuilder is a class that make a Graph across NmapParser

"""

from umitCore.radialnet.Graph import *
#from umitGUI.radialnet.RadialNet import NetNode


COLORS = [(0.0, 1.0, 0.0),
          (1.0, 1.0, 0.0),
          (1.0, 0.0, 0.0)]

BASE_RADIUS = 5.5
NONE_RADIUS = 4.5



class GraphBuilder(Graph):
    def __init__(self):
        Graph.__init__(self)
        
    def __set_default_values(self, node):
            
        node.set_info({'ip':'127.0.0.1/8', 'hostname':'localhost'})
        node.set_draw_info({'color':(0,0,0), 'radius':NONE_RADIUS})
        
    def make(self, parse):
        """
        Make a Graph
        """
        #Get Hosts 
        #hosts = 
        
        nodes = list()
        index = 1
        
        # setting initial reference host
        nodes.append(NetNode(0))
        node = nodes[-1]

        self.__set_default_values(node)
        
        
        
        

# Test Develpment
def main():
    from umitCore.NmapParser import NmapParser
    parser = NmapParser("RadialNet/share/sample/nmap_example.xml")
    parser.parse()
    
    graph = GraphBuilder()
    

if __name__=="__main__":
    main()



