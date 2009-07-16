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

from umit.core.radialnet.Graph import *
from umit.gui.radialnet.RadialNet import NetNode


COLORS = [(0.0, 1.0, 0.0),
          (1.0, 1.0, 0.0),
          (1.0, 0.0, 0.0)]

BASE_RADIUS = 5.5
NONE_RADIUS = 4.5



class GraphBuilder(Graph):
    def __init__(self):
        Graph.__init__(self)
        
    def __set_default_values(self, node):
            
        node.set_info({'ip':'0.0.0.0', 'hostname':'Umit'})
        node.set_draw_info({'color':(1,0,0),
                            'radius':BASE_RADIUS,
                            'line-width':3,
                            'line-color':(0.5,0,0)})
        
        
    def __calc_vulnerability_level(self, node, host):
        """
        """
        ports = host.ports
        number_ports = len(host.ports)
    
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
        for addr in host.address:
            if addr['addrtype'] == 'ipv4':
                host_addresses = addr
                break
        else:
            host_addresses = {}
        if host_addresses.has_key('vendor') and host_addresses['vendor'] == '':
            host_addresses['vendor'] = None

        addresses = list()
    
        addresses.append(host_addresses)
    
        node.set_info({'addresses': addresses})
        node.set_info({'ip': addresses[0]['addr']})
    
        host_hostnames = host.hostnames
        if host_hostnames:
            hostnames = list()
            for host_hostname in host_hostnames:
                hostnames.append(host_hostname.copy())

            node.set_info({'hostnames': hostnames})
            node.set_info({'hostname': hostnames[0]['name']})
    
        # getting uptime
        #xml_uptime = host.search_children('uptime', True)
        host_uptime = host.get_uptime()
        if host_uptime != {}:
            node.set_info({'uptime': host_uptime})
    
        # getting os fingerprint information
    
        os = {}

        host_osfingerprint = host.osfingerprint
        host_osclasses = host.osclass
        host_osmatches = host.osmatch
        host_portsused = host.portused
        os['fingerprint'] = ""
        if host_osfingerprint and host_osfingerprint[0].has_key('fingerprint'):
            os['fingerprint'] = host_osfingerprint[0]['fingerprint']

        if len(host_osclasses) > 0:

            types = ['router', 'wap', 'switch', 'firewall']

            for _type in types:
                if _type in host_osclasses[0]['type'].lower():
                    node.set_info({'device_type': _type})

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
        if len(host_osmatches) > 0:
            os_matches = []

            for host_osmatch in host_osmatches:

                os_match = {}
                os_match['name'] = host_osmatch['name']
                if host_osmatch.get('accuracy', None):
                    os_match['accuracy'] = int(host_osmatch['accuracy'])
                # TODO/FIXME:
                #os_match['db_line'] = int(host_osmatch['line'])
                os_match['db_line'] = 0 
                os_matches.append(os_match)

            os['matches'] = os_matches
        if len(host_portsused) > 0:

            os_portsused = []

            for host_portused in host_portsused:
                host_portused['protocol'] = host_portused['proto']
                host_portused['id'] = int(host_portused['portid'])
                os_portsused.append(host_portused)

            os['used_ports'] = os_portsused

        node.set_info({'os': os})
    
        # getting (copies of) sequences information
        host_tcpsequence = host.tcpsequence.copy()
        host_ipidsequence = host.ipidsequence.copy()
        host_tcptssequence = host.tcptssequence.copy()
        
        sequences = {}
    
        if host_tcpsequence:
            if host_tcpsequence['index']:
                host_tcpsequence['index'] = int(host_tcpsequence['index'])
            host_tcpsequence['values'] = host_tcpsequence['values'].split(',')
            sequences['tcp'] = host_tcpsequence
    
        if host_ipidsequence:
            ip_id = host_ipidsequence
            ip_id['values'] = host_ipidsequence['values'].split(',')
    
            sequences['ip_id'] = ip_id
    
        if host_tcptssequence:
            if host_tcptssequence.get('values', None):
                host_tcptssequence['values'] = \
                        host_tcptssequence['values'].split(',')
    
            sequences['tcp_ts'] = host_tcptssequence

        node.set_info({'sequences': sequences})
    
        # host is host filtered
        filtered = False
        
        host_filtered = host.status['state']
        if host_filtered=="filtered":
            filtered=True
        
        ## Search in ports
        filtered_ports = host.get_filtered_ports()
        
    
        if filtered or filtered_ports > 0:
            node.set_info({'filtered': True})
    
        # getting ports information

        host_ports = host.ports
        host_extraports = host.extraports
        ports = []

        for port in host_ports:
            port = port.copy() # Do not change the original port
            port['id'] = int(port['portid'])
            # TODO: Not ready to integrate right now 
            #for script in xml_scripts:
                #scripts.append(dict())
                #for key in script.get_keys():
                    #scripts[-1][key] = script.get_attr(key)

            service = {}
            # TODO: Get another information - NmapParser update need.
            if 'name' in port:
                service['name'] = port.pop('name')
                service['version'] = port.pop('version', '')
                service['method'] = port.pop('method', '')
                service['product'] = port.pop('product', '')
                service['extrainfo'] = port.pop('extrainfo', '')
                service['conf'] = port.pop('conf', '')

            port['state'] = {'state': port['state']}
            port['scripts'] = {}
            port['service'] = service

            ports.append(port)

        node.set_info({'ports':ports})

        all_extraports = list()
        #print host_extraports
        for extraports in host_extraports:
            extraports = extraports.copy() # Do not change the original eport
            extraports['count'] = int(extraports['count'])
            extraports['reason'] = list()
            extraports['all_reason'] = list()
   
            
            # TODO: implement this
            
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
    
            all_extraports.append(extraports)
    
        node.set_info({'extraports':all_extraports})
    
        # getting traceroute information
        trace = host.trace.copy()
        if trace and trace['hop']:
    
            host_hops = trace['hop']
            hops = []
    
            for host_hop in host_hops:
                hop = host_hop.copy()
                hostname = host_hop.get('host', None)
                hop['ttl'] = int(hop['ttl'])
                hop['host'] = (hostname, '')[hostname is None]
                if 'host' in hop:
                    hop.pop('host')
    
                hops.append(hop)
    
            trace['hops'] = hops
            trace['protocol'] = trace['proto']
    
            node.set_info({'trace':trace})

        
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
            trace = host.trace.copy()
            # if host has traceroute information mount graph
            if trace and trace['hop']:
                
                prev_node = nodes[0]
                
                hops = trace['hop']
                ttls = [int(hop['ttl']) for hop in hops]
                
                # getting nodes of host by ttl
                for ttl in range(1, max(ttls) + 1):
                    if ttl in ttls:
                        _hop = host.get_hop_by_ttl(ttl)
                        if _hop == None:
                            continue
                        hop = _hop.copy()
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
                            if hop.has_key('host') and hop['host'] is not None:
                                node.set_info(\
                                    {'host':hop['host']})
    
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
                        node.set_info({'ip':None, 'host':None})
                        node.set_draw_info({'color':(1,1,1), \
                                            'radius':NONE_RADIUS})
    
                        self.set_connection(node, prev_node)
    
                    prev_node = node                    
            
        # for each full scanned host
        for host in hosts:
    
            for addr in host.address:
                if addr['addrtype'] == 'ipv4':
                    ip = addr
                    break
            else:
                ip = {}
            for node in nodes:
                if ip.has_key('addr') and ip['addr'] == node.get_info('ip'):
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
    from umit.core.NmapParser import NmapParser
    parser = NmapParser("../../umit-within-radialnet/RadialNet2/share/sample/nmap_example.xml")
    #parser = NmapParser("RadialNet2/share/sample/no_trace.xml")
    parser.parse()
    
    graph = GraphBuilder()
    graph.make(parser)
    

if __name__=="__main__":
    main()



