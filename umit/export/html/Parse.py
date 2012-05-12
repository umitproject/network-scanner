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

import sys

BR = Node(None, None, "<br />")

class ExportHTML(Export):

    def __init__(self, parse, filename):
        Export.__init__(self, parse, filename)
        
        # Head Structure 
        self.head = Node('html')
        head = Node('head')
        self.head.add_child(head)
        self.add_style()
        self.html = None

    def add_style(self):
        headtag = self.head.get_childs()[0]
        style = Node( 'style', 
                      [{ 'name':'type', 'value':'text/css' }], STYLE )
        headtag.add_child(style)

    def get(self):
        return self.html

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
        body = self.get_body()
        self.head.add_child(body)
      
        # Main Container
        main_container = Node('div', [{'name':'class', 'value':'container'}])
        # Main Title
        main_title = self.get_main_title(np)
        # Nmap Command
        nmap_command = self.get_nmap_command()
        # Available Hosts
        available_hosts = self.get_available_hosts()
        # Services
        services = self.get_port_services()

        # Packing Body 
        main_container.add_child(main_title)
        main_container.add_child(nmap_command)
        main_container.add_child(Node('hr'))
        main_container.add_child(available_hosts)
        main_container.add_child(Node('hr'))
        main_container.add_child(services)
        main_container.add_child(Node('hr'))
        main_container.add_child(self.get_nmap_output())
        body.add_child(main_container)

        # Assign html code to variable which will be used for saving.
        self.html = self.head.get_html()

    def get_body(self):
        # Customize Page
        body = Node('body')
        return body
    
    def get_nmap_command(self):
        row = self.get_row()
        nmap_title = Node( 'h3', 
                           attr=[{'name':'class','value':'nmap-command'}], 
                           text="Nmap command : " + self.parse.nmap_command )
        row.add_child(nmap_title)
        return row
    
    def get_row(self):
        return Node('div',[{'name':'class', 'value':'row-fluid'}])

    def get_main_title(self, np):

        # main title hero-unit
        hero_unit = Node('div', [{'name':'class', 'value':'hero-unit'}])
        
        #1 TODO: PEP8!
        #2 TODO: Put logo and css location in an exact place and 
        #        load from there

        # main title div
        title_div = Node('div')
        title = Node( 'h2', 
                      attr = [{'name':'class', 'value':'umit-title'}], 
                      text = self.get_name() + " - " + np.profile_name )
        title_div.add_child(title) 

        # add div to hero-unit
        hero_unit.add_child(title_div)

        # wrap everything in a row  
        row = self.get_row()
        row.add_child(hero_unit)

        return row   

    def get_available_hosts(self):

        table = Node('table', [{'name':'class', 'value':'table'}])

        # Header host table
        thead = Node('thead')
        tbody = Node('tbody')
        tr = Node('tr')
        th = Node('th')
        th = Node('th')
        th.add_child(Node(None, None, self.get_dname('addr', '_ip')))
        tr.add_child(th)
        th = Node('th')
        th.add_child(Node(None, None, "OS"))
        tr.add_child(th)

        thead.add_child(tr) 
        table.add_child(thead)

        res = self.get_list_host()

        for r in res:
            tr = Node('tr')
            # Ip
            td = Node('td')
            td.add_child(Node(None, None, r['address'][0]['addr']))
            tr.add_child(td)
            
            # OS Matches Values
            if r.has_key('osmatch'):
                for i in range(len(r['osmatch'])):
                    for key in r['osmatch'][i].keys():
                        td = Node('td')
                        if key == 'osclass':
                            osclass = r['osmatch'][i][key]
                            if osclass:
                                value = osclass[0]['osfamily']
                            else:
                                value = "---"    
                            td.add_child(Node(None, None, value))
                            tr.add_child(td)
            tbody.add_child(tr)
        table.add_child(tbody)

        well_div = Node('div', [{'name':'class', 'value':'well'}])
        available_hosts = Node( 'h3', 
                                [{'name':'class','value':'umit-result-title'}],
                                'Available hosts : ')
        # pack all components
        row = self.get_row()
        row.add_child(table)
        well_div.add_child(available_hosts)
        well_div.add_child(row)

        return well_div
    
    def get_port_services(self):
        """
        Returns port and services
        """
        
        well_div = Node('div', [{'name':'class', 'value':'well'}])
        row = self.get_row()
        services_title = Node( "h3",
                      [{'name':'class','value':'umit-result-title'}], 
                      'Services : ' )
        row.add_child(services_title)

        # Table Part
        res = self.get_list_host()

        for host in res:
            # Add host ip
            ip_addr = Node( "h4", 
                            [{'name':'class', 'value':'umit-ip'}], 
                            "IP:" + host['address'][0]['addr'] )
            row.add_child(ip_addr)

            # Hosts table
            # TODO : Check if these definitons should be here or not?
            table = Node('table', [{'name':'class', 'value':'table'}])
            thead = Node('thead')
            tbody = Node('tbody')
            
            # Header Preparation
            tr = None
            for portlist in host['ports']:
                tr = Node('tr')
                for port in portlist:
                    th = Node('th')
                    th.add_child(Node(None, None, port))
                    tr.add_child(th)
            if tr:
                thead.add_child(tr)
                table.add_child(thead)

                for portlist in host['ports']:
                    tr = Node('tr')
                    for port in portlist:
                        td = Node('td')
                        td.add_child(Node(None, None, portlist[port]))
                        tr.add_child(td)
                    tbody.add_child(tr)
                    
            table.add_child(tbody)
            row.add_child(table)
       
        well_div.add_child(row)         
        return well_div

    def get_nmap_output(self):
        """
            Return Node with nmap output 
        """
        
        nmap_title = Node( 'h3', 
                           [{'name':'class','value':'umit-result-title'}],
                           'Nmap Output : ')
        nmap_output = ""
        output = self.parse.nmap_output
        for output in self.parse.nmap_output.split("\n")[1:]:
            nmap_output += output + '<br>'
        nmap_output = Node(None, None, nmap_output)
        well_div = Node('div', [{'name':'class', 'value':'well'}])
        row = self.get_row()
        row.add_child(nmap_title)
        row.add_child(nmap_output)
        well_div.add_child(row)
        
        return well_div
