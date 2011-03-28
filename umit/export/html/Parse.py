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


from umit.export.Parse import Export
from umit.export.html.Node import Node, STYLE

BR = Node(None, None, "<br />")

class ExportHTML(Export):
    def __init__(self, parse, filename):
        Export.__init__(self, parse, filename)
        
        # Head Structure 
        self.head = Node('html')
        head = Node('head')
        self.head.add_child(head)
        self.add_style(STYLE)
    def add_style(self, style_t):
        headtag = self.head.get_childs()[0]
        style = Node('style', [{'name':'type', 'value':'text/css'}])
        style.add_child(Node(None, None ,style_t))
        headtag.add_child(style)
    def get(self):
        return self.generate_html()
    def get_name(self):
        np = self.parse 
        if np.scan_name == "":
            name = "Unnamed"
        else:
            name = np.scan_name
        return name
    def generate_html(self):
        
        # Header / Title 
        np = self.parse 
        head = self.head.get_childs()[0]

        head.add_child(Node('title',text = self.get_name()\
                            + " - "  + np.profile_name ))
        body = self.get_body(head)
        self.head.add_child(body)
        hosts = self.get_hosts()
        
        
        # Packing Body 
        body.add_child(Node(None, text="<h1><b>"+self.get_name()+" - "+\
                            np.profile_name+\
                            "</b></h1>"+"</br></br>" ))
        body.add_child(self.get_nmap_command())
        
        title = Node(None, None, '<b><h2>Available hosts:</h2></b> <br />')
        body.add_child(title)
        body.add_child(hosts)
        # Services
        
        title = Node(None, None, '<b><h2>Services:</h2></b> <br />')
        body.add_child(title)
        services = self.get_port_services()
        body.add_child(services)
        body.add_child(self.get_nmap_output())
        return self.head.get_html()
    def get_body(self, head):
        # Customize Page
        body = Node('body')
        return body
    
    def get_nmap_command(self):
        nmap = Node(None,None, "Nmap command: <b>" + self.parse.nmap_command + \
                    "</b><br /><br />")
        return nmap 
    
    def get_hosts(self):
        
        
        
        table = Node('table', [{'name':'border', 'value':'1'}])
        
        res = self.get_list_host()
        
        # Header host table 
        tr = Node('tr')
        td = Node('td')
        td.add_child(Node(None, None, "<b>"+\
                          self.get_dname('addr', '_ip')+"</b>"))
        tr.add_child(td)
        td = Node('td')
        td.add_child(Node(None, None, "OS"))
        tr.add_child(td)        
        
        table.add_child(tr)
        
        for i in res:
            tr = Node('tr')
            # Ip
            td = Node('td')
            td.add_child(Node(None, None, i['_ip']['addr']))
            tr.add_child(td)
            
            
            # OS Classes Values
            #for j in i['_osclasses']:
                #for key in j:
                    #value =  j[key]
                    #td = Node('td')
                    #td.add_child(Node(None, None, value))
                    #tr.add_child(td)
                
                        
            # OS Matches Values
            if i.has_key('_osmatch'):
                for key in i['_osmatch']:
                    value =  i['_osmatch'][key]
                    td = Node('td')
                    if value is list:
                        value = value[0]['osfamily']
                        print value
                    if not (value is str):
                        value = " - "
                    td.add_child(Node(None, None, value))
                    tr.add_child(td)
                table.add_child(tr)
            
        return table
    
    def get_port_services(self):
        """
        Returns port and services
        """
        
        
        group = Node('div', [{'name':'width', 'value':'60%'}])
        
        res = self.get_list_host()
        
        for host in res:
            
            title = Node(None, None, "<b>IP:" +host['_ip']['addr'] + "</b>")
            group.add_child(title)
            
            table = Node('table', [{'name':'border', 'value':'1'}, \
                                   {'name':'width', 'value':'60%'}])
            # ###### Header #########
            for portlist in host['_ports'][0]['port']:
                tr = Node('tr')
                for port in portlist:
                    td = Node('td')
                    td.add_child(Node(None, None, \
                                      port))
                    tr.add_child(td)
            table.add_child(tr)
            # ######################
            
            for portlist in host['_ports'][0]['port']:
                tr = Node('tr')
                for port in portlist:
                    
                    td = Node('td')
                    td.add_child(Node(None, None, \
                                      portlist[port]))
                    tr.add_child(td)
                table.add_child(tr)
                
            group.add_child(table)
            group.add_child(BR)
        return group
    def get_nmap_output(self):
        """ Return Node with nmap output """
        
        div = Node('div',[{'name':'width', 'value':'60%'}])
        title = Node(None, None, '<b><h2>Nmap outpuut:</h2></b> <br />')
        div.add_child(title)
        
        pre = Node('pre' , [{'name':'width', 'value':'60%'}])
        output = Node(None, None, self.parse.nmap_output)
        pre.add_child(output)
        div.add_child(pre)
        
        return div