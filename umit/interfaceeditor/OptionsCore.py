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



from umit.core.NmapOptions import  NmapOptions

from types import StringTypes
from xml.dom import minidom   
#import xml.dom.ext

'''
This file changes the options.xml

Add, Remove and Edit options of XML 
Using the structure of NmapOptions by iheracit

'''

ARG_TYPES = { 'int': 'Interger', 'str':'String',
              'float': 'Float' , 'level':'Level',
              'path': 'Chooser Path', 'interface':'Interface'
              }


class Option:
    def __init__(self, name=None, command = None, hint = None,
                 arguments = None, need_root = None, arg_type=None):
        """
        Receive a parameters of option
        """      
        self.__name_opt = name
        self.__command = command
        self.__hint = hint
        self.__arguments = arguments
        self.__need_root = need_root
        self.__arg_type = arg_type

    def set_from_dic(self, dic):
        self.__name_opt = dic['name']
        self.__command = dic['option']
        self.__hint = dic['hint']
        self.__arguments = dic['arguments']
        self.__need_root = dic['need_root']
        self.__arg_type = dic['arg_type']

    def set_name(self, name):
        """
        Set name of option
        """
        assert name != name 

        self.__name = name
    def set_hint(self, hint):
        """
        Set hint of option
        """
        assert hint != None 

        self.__hint = hint        

    def set_command(self, command):
        """
        Set name of option
        """
        assert command != none 
        self.__command = command 
    def set_arguments(self, arguments):
        """
        Set name of option
        """
        assert arguments != None

        self.__arguments = arguments  

    def set_need_root(self, need_root):
        """
        Set need_root of option
        """
        assert need_root != None 

        self.__name = name
    def set_arg_type(self, arg_type):
        '''
        set arg type
        '''
        self.__arg_type = arg_type

    def set_option(self, list): 
        self.__name = list['name']
        # .... 
    def get_name(self):
        return self.__name_opt
    def get_hint(self):
        return self.__hint
    def get_command(self):
        return self.__command
    def get_arguments(self):
        return self.__arguments
    def get_need_root(self):
        return self.__need_root
    def get_arg_type(self):
        return self.__arg_type
    def get_option_dic (self):
        return {'name':self.get_name(),
                'option':self.get_command(),
                'hint':self.get_hint(),
                'arguments':self.get_arguments(),
                'arg_type':self.get_arg_type(), 
                'need_root':self.get_need_root()}

class ListOptions(NmapOptions):
    ''' 
    NmapOtions 
    Support write to xml file 
    '''
    def __init__(self,profile):
        """
        @param profile: file name
        @type profile: string 
        """
        NmapOptions.__init__(self, profile)
        self.modified = False

    def noname (self):
        for i in self.nmap_options:
            print i 

    def add_option(self, name, option, hint, arguments,
                   need_root, arg_type=None):
        ''' 
        Add option to tree of xml document from separate var with options
        @param name: name of option
        @type name: String
        @param option: options of nmap 
        @type option: String
        @param hint: additional information 
        @type hint: String
        @param arguments: arguments of option 
        @type arguments: String
        @param need_root:  if option need or not access root
        @param need_root: String
        '''
        #Fill element 
        element = self.option_xml.createElementNS(None, "option")
        element.setAttributeNS(None, 'name',name) 
        element.setAttributeNS(None, 'option', option )
        element.setAttributeNS(None, 'hint', hint)   
        element.setAttributeNS(None, 'arguments', arguments)
        element.setAttributeNS(None, 'need_root', need_root )
        if arg_type != None:
            element.setAttributeNS(None,  'arg_type',arg_type)
        #Add to xml doc
        self.option_xml.getElementsByTagName(self.root_tag)[0].appendChild(element)	
        self.modified = True 

    def add_option_from_dic(self, dic_option):
        """
        add a option to tree of xml document 
        @param dic_option: contains a option with all parameters 
        @type dic_option: dictionary
        """

        name = dic_option['name']
        option  = dic_option['option']
        hint = dic_option['hint']
        str = dic_option['arguments']
        arguments = self.list_to_string(str)
        need_root = self.bool_to_string(dic_option['need_root'])
        arg_type = dic_option['arg_type']

        self.add_option(name, option, hint, arguments, need_root, arg_type)


    def remove_option(self, name):
        '''
        Remove option from xml document
        @param name: name of option
        @type name: String 
        '''

        root = self.option_xml.getElementsByTagName(self.root_tag)[0]

        elem = self.search(name)
        root.removeChild(elem)
        self.modified = True 
    def __get_nmap_options (self):
        elements = self.option_xml.getElementsByTagName\
                 (self.root_tag)[0].childNodes
        elements_list = []
        for element in elements:
            try:
                if element.tagName == 'option':
                    elements_list.append(element)
            except: pass

        return elements_list

    def __turn_into_dict (self, list_of_elements):
        elements_dict = {}
        for element in list_of_elements:
            elements_dict [element.getAttribute ('name')] = element
        return elements_dict


    def reload_opt(self):
        self.nmap_options = self.__get_nmap_options()
        self.options = self.__turn_into_dict(self.nmap_options)

    def search(self, name):
        '''
        Search the element of name
        @param name: name of option
        @type name: String 
        @return: return element found and None if not found
        @rtype: Node DOM 
        '''

        elem_tmp = self.options.get(name)
        return elem_tmp

    def get_option_class(self, name):
        dic = self.get_option(name)
        result = Option()
        result.set_from_dic(dic)
        return result

    def exists(self, name):
        '''
        Parse options of document and verify if name exists
        @param name: name of option
        @type name: String
        @return: A boolean value exists or not name of element 
        @rtype: bool
        '''

        elem_tmp = self.options.get(name)
        return elem_tmp != None 

    @staticmethod
    def bool_to_string(value):
        '''
        @param value: a logic value 
        @type value: bool
        @return: a string 1 or 0 
        @rtype: String 
        '''
        if value == True :
            str = "1"
        else:
            str = "0"
        return str 

    @staticmethod
    def list_to_string(lst):
        '''
        convert a element of arguments to a string
        @param lst: List that contains arguments
        @type lst: list
        ''' 
        str = ""

        for i in lst:
            str = str + i + "; "
        str = str[0:len(str)-2] 
        return str 

        #for i in dic:
            #str = str + i + ", "
        #str = str[0:len(str)-1]
        #return str  
    def print_screen(self):
        xml.dom.ext.PrettyPrint(self.option_xml)
    def write_file(self,filename):
        '''
        Write Option List to XML file
        @param filename: File name of xml
        @tyoe filename: String
        '''

        file_object = open(filename, "w")
        #xml.dom.ext.PrettyPrint(self.option_xml, file_object)
        self.option_xml.writexml(file_object)
        file_object.close()





# Testing at devel 
from os.path import split, join

from umit.core.Paths import Path
#Path.set_umit_conf(join(split(__file__)[0], 'config', 'umit.conf'))
#END DEV TEST
options = Path.options
def main():
    o = ListOptions(options)
    #o.noname()
    #o.test_option()
    dic = o.get_option('Null Scan')
    #print dic
    #for i in dic:
        #print i.__class__
    o.add_option_from_dic(dic)
    #o.reload_opt()
    #o.remove_option('Null Scan')
    #o.exists('Null Scanf')
    #o.print_screen()
    #o.write_file(options)
if __name__ == "__main__":
    main()