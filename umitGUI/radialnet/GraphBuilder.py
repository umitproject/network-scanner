# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques.
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
from umitGUI.radialnet.RadialNet import NetNode


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
        
        
    def __calc_vulnerability_level(self, node, host):
        """
        """
        ports = host.get_ports()
        number_ports = 0 
        for port in ports:
            number_ports = number_ports + len(port['port'])
    
        node.set_info({'number_of_scanned_ports': number_ports})
    
        if number_ports < 3:
            node.set_info({'vulnerability_score': 0})
    
        elif number_ports < 7:
            node.set_info({'vulnerability_score': 1})
    
        else:
            node.set_info({'vulnerability_score': 2})
    
    def __set_node_info(self, node, host):
        """
        """
        node.set_info({'host_reference': host})
    
        # getting vulnerability score
        self.__calc_vulnerability_level(node, host)
    
        radius = BASE_RADIUS + node.get_info('number_of_scanned_ports') / 2
        node.set_draw_info({'color':COLORS[\
            node.get_info('vulnerability_score')],\
                            'radius':radius})
    
        # getting address and hostnames
        host_addresses = host.get_ip()
        if host_addresses.has_key('vendor') and host_addresses['vendor'] == '':
            host_addresses['vendor'] = None
            
        addresses = list()
    
        addresses.append(host_addresses)
    
        node.set_info({'addresses': addresses})
        node.set_info({'ip': addresses[0]['addr']})
    
        host_hostnames = host.get_hostnames()
        if len(host_hostnames) > 0:
    
            hostnames = list()
    
            for host_hostname in host_hostnames:
    
                hostname = dict()
    
                hostname['name'] = host_hostname['hostname']
                hostname['type'] = host_hostname['hostname_type']
    
                hostnames.append(hostname)
            node.set_info({'hostnames': hostnames})
            node.set_info({'hostname': hostnames[0]['name']})
    
        # getting uptime
        #xml_uptime = host.search_children('uptime', True)
        host_uptime = host.get_uptime()
        if host_uptime != {}:
            node.set_info({'uptime': host_uptime})
    
        # getting os fingerprint information
    
        os = {}

        host_osfingerprint = host.get_osfingerprint()
        host_osclasses = host.get_osclasses()
        host_osmatches = host.get_osmatch()
        host_portsused = host.get_ports_used()
        
        os['fingerprint'] = host_osfingerprint['fingerprint']
        if len(host_osclasses) > 0:

            types = ['router', 'wap', 'switch', 'firewall']

            for type in types:
                if type in host_osclasses[0]['type'].lower():
                    node.set_info({'device_type': type})

            os_classes = []

            for host_osclass in host_osclasses:

                os_class = {}

                os_class['type'] = host_osclass['type']
                os_class['vendor'] = host_osclass['vendor']
                os_class['accuracy'] = int(host_osclass['accuracy'])
                os_class['os_family'] = host_osclass['osfamily']

                if host_osclass.has_key('osgen'):
                    os_class['os_gen'] = host_osclass['osgen']

                os_classes.append(os_class)

            os['classes'] = os_classes
        #if len(host_osmatches) > 0:

            #os_matches = []

            #for host_osmatch in host_osmatches:

                #os_match = {}

                #os_match['name'] = host_osmatch['name']
                #os_match['accuracy'] = int(host_osmatch['accuracy'])
                #os_match['db_line'] = int(host_osmatch['line'])

                #os_matches.append(os_match)

            #os['matches'] = os_matches
        if len(host_portsused) > 0:

            os_portsused = []

            for host_portused in host_portsused:
                host_portused['id'] = int(host_portused['portid'])

                os_portsused.append(host_portused)

            os['used_ports'] = os_portsused

        node.set_info({'os': os})
    
        # getting sequences information
        host_tcpsequence = host.get_tcpsequence()
        host_ipidsequence = host.get_ipidsequence()
        host_tcptssequence = host.get_tcptssequence()
        
        sequences = {}
    
        if host_tcpsequence != {}:
    
            tcp = host_tcpsequence
            tcp['index'] = int(host_tcpsequence['index'])
            tcp['class'] = host_tcpsequence['class']
            tcp['values'] = host_tcpsequence['values'].split(',')
            tcp['difficulty'] = host_tcpsequence['difficulty']
    
            sequences['tcp'] = tcp
    
        if host_ipidsequence != {}:
    
            ip_id = host_ipidsequence
            ip_id['values'] = host_ipidsequence['values'].split(',')
    
            sequences['ip_id'] = ip_id
    
        if host_tcptssequence != {}:
    
            if host_tcptssequence.has_key('values') and \
               host_tcptssequence['values'] != None:
                host_tcptssequence['values'] = \
                                  host_tcptssequence['values'].split(',')
    
            sequences['tcp_ts'] = host_tcptssequence
    
        node.set_info({'sequences': sequences})
    
        # host is host filtered
        filtered = False
        
        host_filtered = host.get_state()
        if host_filtered=="filtered":
            filtered=True
        
        ## Search in ports
        filtered_ports = host.get_filtered_ports()
        
    
        if filtered or filtered_ports > 0:
            node.set_info({'filtered': True})
    
        # getting ports information
        #xml_ports = host.search_children('port', deep=True)
        #xml_extraports = host.search_children('extraports', deep=True)
   
        host_ports = host.get_ports()
        host_extraports = host.get_extraports()
        print host_ports
        ports = list()
    
        for host_port in host_ports:
    
            port = dict()
            state = dict()
            scripts = list()
            service = dict()
    
            #xml_state = xml_port.search_children('state', True, True)
            #xml_scripts = xml_port.search_children('script', deep=True)
            #xml_service = xml_port.search_children('service', True, True)
    
            #port['id'] = int(xml_port.get_attr('portid'))
            #port['protocol'] = xml_port.get_attr('protocol')
    
            #if xml_state != None:
                #for key in xml_state.get_keys():
                    #state[key] = xml_state.get_attr(key)
    
            #for script in xml_scripts:
    
                #scripts.append(dict())
    
                #for key in script.get_keys():
                    #scripts[-1][key] = script.get_attr(key)
    
            #if xml_service != None:
                #for key in xml_service.get_keys():
                    #service[key] = xml_service.get_attr(key)
            
            #port['state'] = state
            #port['scripts'] = scripts
            #port['service'] = service
    
            #ports.append(port)
    
        #node.set_info({'ports':ports})
    
        #all_extraports = list()
    
        #for xml_extraport in xml_extraports:
    
            #extraports = dict()
            #extraports['count'] = int(xml_extraport.get_attr('count'))
            #extraports['state'] = xml_extraport.get_attr('state')
            #extraports['reason'] = list()
            #extraports['all_reason'] = list()
    
            #xml_extrareasons = xml_extraport.search_children('extrareasons',
                                                             #deep=True)
    
            #for extrareason in xml_extrareasons:
    
                #extraports['reason'].append(extrareason.get_attr('reason'))
                #extraports['all_reason'].append(dict())
            
                #for key in extrareason.get_keys():
    
                    #value = extrareason.get_attr(key)
    
                    #if key == 'count':
                        #value = int(value)
    
                    #extraports['all_reason'][-1][key] = value
    
            #all_extraports.append(extraports)
    
        #node.set_info({'extraports':all_extraports})
    
        ## getting traceroute information
        #xml_trace = host.search_children('trace', first=True)
    
        #if xml_trace != None:
    
            #xml_hops = xml_trace.search_children('hop')
    
            #trace = {}
            #hops = []
    
            #for xml_hop in xml_hops:
    
                #hop = {}
    
                #hop['ip'] = xml_hop.get_attr('ipaddr')
                #hop['ttl'] = int(xml_hop.get_attr('ttl'))
                #hop['rtt'] = xml_hop.get_attr('rtt')
    
                #hostname = xml_hop.get_attr('host')
                #hop['hostname'] = (hostname, '')[hostname == None]
    
                #hops.append(hop)
    
            #trace['hops'] = hops
            #trace['port'] = xml_trace.get_attr('port')
            #trace['protocol'] = xml_trace.get_attr('proto')
    
            #node.set_info({'trace':trace})

    
    
    
        
    def make(self, parse):
        """
        Make a Graph
        """
        #Get Hosts 
        hosts = parse.get_hosts()
        
        nodes = list()
        index = 1
        
        # setting initial reference host
        nodes.append(NetNode(0))
        node = nodes[-1]

        self.__set_default_values(node)
        
        # for each host in hosts just mount the graph
        for host in hosts:
            trace = host.get_trace()
            # if host has traceroute information mount graph
            if trace != []:
                
                prev_node = nodes[0]
                
                hops = host.get_hops()
                ttls = [int(hop['ttl']) for hop in hops]
                
                # getting nodes of host by ttl
                for ttl in range(1, max(ttls) + 1):
                        
                    if ttl in ttls:
    
                        hop = host.get_hop_by_ttl(ttl)
                        
                        # FIXME: Protect if hop == None
                        for node in nodes:
                            if hop['ipaddr'] == node.get_info('ip'):
                                break
    
                        else:
    
                            nodes.append(NetNode(index))
                            node = nodes[-1]
                            index += 1
    
                            node.set_draw_info({'valid':True})
                            node.set_info({'ip':hop['ipaddr']})
                            node.set_draw_info({'color':(1,1,1),
                                                'radius':NONE_RADIUS})
                            if hop.has_key('host') and hop['host'] != None:
                                node.set_info(\
                                    {'hostname':hop['host']})
    
                        rtt = hop['rtt']
    
                        if rtt != '--':
                            self.set_connection(node, prev_node, float(rtt))
    
                        else:
                            self.set_connection(node, prev_node)
    
                    else:
    
                        nodes.append(NetNode(index))
                        node = nodes[-1]
                        index += 1
    
                        node.set_draw_info({'valid':False})
                        node.set_info({'ip':None, 'hostname':None})
                        node.set_draw_info({'color':(1,1,1), \
                                            'radius':NONE_RADIUS})
    
                        self.set_connection(node, prev_node)
    
                    prev_node = node                    
            
        # for each full scanned host
        for host in hosts:
    
            ip = host.get_ip()
            
            
            for node in nodes:
                if ip['addr'] == node.get_info('ip'):
                    break
    
            else:
    
                nodes.append(NetNode(index))
                node = nodes[-1]
                index += 1
    
                node.set_draw_info({'no_route':True})
    
                self.set_connection(node, nodes[0])
    
            node.set_draw_info({'valid':True})
            node.set_info({'scanned':True})
            self.__set_node_info(node, host)
    
        self.set_nodes(nodes)
        self.set_main_node_by_id(0)
        

# Test Develpment
def main():
    from umitCore.NmapParser import NmapParser
    parser = NmapParser("RadialNet2/share/sample/nmap_example.xml")
    #parser = NmapParser("RadialNet2/share/sample/no_trace.xml")
    parser.parse()
    
    graph = GraphBuilder()
    graph.make(parser)
    

if __name__=="__main__":
    main()



