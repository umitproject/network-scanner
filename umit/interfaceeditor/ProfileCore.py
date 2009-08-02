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

from types import StringTypes
from xml.dom import minidom   

from os.path import split, join

from umit.core.Paths import Path

options = Path.options
from umit.core.NmapOptions import NmapOptions


'''
ProfileCore manage all of the profile.xml
- Supports the reading of options
- Supports the writing ordenabled options and groups 
- Add/Remove a group
- Add options for each group 

## Special info: 
- If delete a group all options on this group should be 
  deleted too. 
- A feauture that should be have it's delete a option 
  if it's deleted by options.xml 
- Solve all problems with options dependentions 
'''


class ProfileOption(object):
    '''
    This class contains a option on Profile and Wizard 
    It is a bridge between ProfileCore and Profile (Editable Box)
    '''
    def __init__(self, type, label, option=None, arg_type=None , option_list=None ):
        self._type = type
        self._label = label 
        self._option = option
        self._arg_type = arg_type
        self._option_list = option_list
        self._section = None
        self._next_opt = None
    def set_option_list(self, optionlist):
        self._option_list = optionlist
    def set_label(self, name):
        self._label= name
    def set_section(self, section):
        self._section = section
    def set_type(self, type):
        self._type = type
    def set_next_opt(self, opt):
        self._next_opt= opt
    def get_next_opt(self):
        return self._next_opt
    def get_type(self):
        return self._type 
    def get_label(self):
        return self._label
    def get_option(self):
        return self._option
    def get_arg_type(self):
        return self._arg_type
    def get_option_list(self):
        return self._option_list
    def get_hint(self):
        pass
    def get_section(self):
        return self._section


def option_to_profileoption(option):
    '''
    This is a simples method to create a new ProfileOption from 
    a new Option.
    It's a very primitive and useful when you create a new option at 
    profile based on a option
    WHEN USE: example when do drag-n-drop, and received a Option
    as we working with Profile, it's need a ProfileOption
    '''
    from umit.interfaceeditor.OptionsCore import Option
    o = option
    result = ProfileOption('option_check', o.get_name(), o.get_name(),
                           o.get_arg_type())
    return result





class ProfileCore(object):
    def __init__(self, xml_file):
        '''
        Open XML file 
        It should be inheritance of OptionBuilder But I don't need 
        a function that update command.
        So I implement a new way of read elements like OptionBuilder 
        with support of write in XML 


        @param xml_file: String with a path of file 
        @type xml_file: str 
        '''

        xml_desc = open(xml_file)
        self.xml_parse = minidom.parse(xml_desc)
        xml_desc.close()
        self.root_tag = "interface"
        self.xml = self.xml_parse.getElementsByTagName(self.root_tag)[0]
        self.options = NmapOptions(options)

        self.groups = self.__parse_groups()
        self.section_names = self.__parse_section_names()
        self.tabs = self.__parse_tabs()

    # Private API 

    def __parse_section_names(self):
        dic = {}
        for group in self.groups:
            grp = self.xml.getElementsByTagName(group)[0]
            dic[group] = grp.getAttribute(u'label')
        return dic

    def __parse_groups(self):
        return [g_name.getAttribute(u'name') for g_name in \
                self.xml.getElementsByTagName(u'groups')[0].\
                getElementsByTagName(u'group')]

    def __parse_tabs(self):
        ''' 

        This part should be interact with BoxEditable of Items
        '''

        #XXX fix OptionTab - implement new way
        dic = {}
        for tab_name in self.groups:
            #dic[tab_name] = OptionTab(self.xml.getElementsByTagName(tab_name)[0],
            #                          self.options, self.constructor, self.update_func)
            dic[tab_name] = self.xml.getElementsByTagName(tab_name)[0]
        return dic



    #Public API 
    def get_group(self):

        for root_tab in self.tabs:
            for option_element in self.tabs[root_tab].childNodes:
                try:option_element.tagName
                except:pass
                else:
                    print option_element.tagName
                    #self.widgets_list.append(actions[option_element.tagName](option_element, options_used))
                #print ".."

    def create_element_optlist(self, name):
        element = self.xml_parse.createElementNS(None, 'option')
        element.setAttribute('name', name)
        return element

    def update_option_list(self, section, name, newoptionlist):
        '''
        to update the list of option_list 
        update all childs inside option_list


        steps of implementation : 
        - get element
        - remove childs 
        - create childs 
        - append childs
        '''

        element = self.search_option(section,name)
        for i in element.childNodes:
            try: i.tagName
            except:pass
            else:
                element.removeChild(i)
        for i in newoptionlist:
            new = self.create_element_optlist(i)
            element.appendChild(new)



    def rename_option(self, section, name, newname):
        '''
        rename label option inside a section
        '''

        element = self.search_option(section, name)
        element.setAttribute('label', newname)

    def rename_section(self, name, newname):
        '''
        rename section name, should be renamed at groups 
        and the <Name...>
        '''
        node = self.get_section_node(name)
        node.setAttribute('name', newname)

        element = self.xml_parse.createElement(newname)
        element.setAttribute('label', newname)
        for option in self.tabs[name].childNodes:
            try: option.tagName
            except:pass
            else:
                element.appendChild(option)

        self.xml.removeChild(self.tabs[name])
        self.xml.appendChild(element)

        self.groups = self.__parse_groups()
        self.section_names = self.__parse_section_names()
        self.tabs = self.__parse_tabs()


    def get_section_node(self, section):
        '''
        get section node
        '''

        element = self.xml.getElementsByTagName('groups')[0]
        element_group = element.getElementsByTagName(u'group')
        result = None 
        for i in element_group:
            result = i
            if i.getAttribute('name') == section:
                break


        return result
    def get_section(self, section):
        '''
        @param section: a section name
        @type section: str 
        @return: a list of options
        @rtype: a list of ProfileOption

        '''
        result = []
        for option in self.tabs[section].childNodes:
            try: option.tagName
            except:pass
            else:
                tagName = option.tagName
                if tagName == 'option_check':
                    tmp_po = ProfileOption(tagName, option.getAttribute(u'label'),
                                           option.getAttribute(u'option'),
                                           option.getAttribute(u'arg_type'),
                                           None)
                elif tagName == 'option_list':

                    option_list = []
                    for k in option.getElementsByTagName('option'):
                        option_list.append(k.getAttribute(u'name'))
                    tmp_po = ProfileOption(tagName, option.getAttribute(u'label'),
                                           None, None, option_list)

                result.append(tmp_po)
        return result


    def add_section(self, name):
        '''
        Add section inside groups and create a new tagName
        '''

        self.add_section_before(name, None)
        #Create a void tag of section: 
        element = self.xml_parse.createElementNS(None, name)
        element.setAttribute('label',name)
        self.xml.appendChild(element)
        self.groups = self.__parse_groups()
        self.section_names = self.__parse_section_names()
        self.tabs = self.__parse_tabs()

    def remove_opt(self, section, name):	
        if section == None or name == None:
            return False
        elem = self.search_option(section, name)
        root = self.xml_parse.getElementsByTagName(self.root_tag)[0]
        sec = root.getElementsByTagName(section)

        sec[0].removeChild(elem)
    def remove_section(self, section_name):
        '''
        Removes section of the DOM 
        @param section_name: name of the section that will be removed
        @type section_name: str 
        '''


        #root = self.xml_parse.getElementsByTagName(self.root_tag)[0]
        root = self.xml.getElementsByTagName('groups')[0]
        elem = self.search_in_groups(section_name)
        root.removeChild(elem)



    def search_in_groups(self, name):
        '''
        Search a element of group
        @param name: name of group to search
        @type name: str 

        @return : a Child None of DOM if found or None if not found 
        @rtype: ChildNode or None 
        '''

        element = self.xml.getElementsByTagName('groups')[0]
        element_group = element.getElementsByTagName(u'group')
        result = None 
        for i in element_group:
            if i.getAttribute('name') == name:
                result = i
        return result
    def add_section_after(self, section, section_after):
        pass

    def add_section_before(self, section, section_before):
        '''
        This function is to insert a new section at groups 
        with a new interface it is need insert and move sections

        '''
        #Fill element 
        element = self.xml_parse.createElementNS(None, "group")
        element.setAttributeNS(None, 'name',section) 
        #search Node to insert before it
        beforeChild = self.search_in_groups(section_before)
        #Add to xml doc
        self.xml.getElementsByTagName('groups')[0].insertBefore(element,
                                                                beforeChild )	

    def search_option(self, section_name, option_name):
        '''
        Search a option with a name and return this Node 
        @param section_name: A section name where is to looking for 
        @type section_name: str 
        @param option_name: A name of option for searching 
        @type option_name: str

        @return: A node with a element found or None if not found 
        @rtype: ChildNode element or None 
        '''

        grp = self.xml.getElementsByTagName(section_name)[0]
        result = None 
        for elem in grp.childNodes:
            try: elem.getAttribute(u'label')
            except: pass
            else: 
                if elem.getAttribute(u'label') == option_name:
                    result = elem
                    break 

        return result

    def add_option_before(self, section_name, option, before):

        result = self.xml.getElementsByTagName(section_name)[0].insertBefore(option, before)	   
    def add_from_profileoption(self, profileoption):
        '''
        use add_option
        '''
        po = profileoption
        section = po.get_section()
        tagname = po.get_type()
        label = po.get_label()
        option = po.get_option()
        arg_type = po.get_arg_type()
        option_list = po.get_option_list()
        option_name_next = po.get_next_opt()


        self.add_option(section, tagname, label, option, arg_type, 
                        option_list, option_name_next)


    def add_option(self, section_name, tagname, label, option=None, 
                   arg_type=None, options_list=None, option_name_before=None):
        '''
        Add a option in a section 
        - If is a optionlist it have a option_list and if the option 
        should be not inserted at the end of section have a option_name_before
        @param section_name: A section name where options should be added
        @type section_name: str 
        @param tagname: option_check, option_list or others used at 
        Profile Editor or Wizard
        @type tagname: str 
        @param label: Name of this option
        @type label: str 
        @param option: The option is used to link with file options.xml
        @type option:  str 
        @param arg_type: type of arg (#XXX I think that it's obsulete right now)
        @type arg_type:str 
        @param option_list: A list with a name options to option_list
        @type option_list: list 
        @param option_name_before: name of option after where is inserted 
        @type option_name_before: str 
        '''
        element = self.xml_parse.createElementNS(None, tagname)
        if arg_type != None: 
            element.setAttribute('arg_type', arg_type)
        element.setAttribute('label',label)
        if option != None:
            element.setAttribute('option', option)
        elements = [] 
        if options_list != None: 

            for i in options_list:
                element_in = self.xml_parse.createElementNS(None, 'option')
                element_in.setAttributeNS(None, 'name', i)
                elements.append(element_in)
        after = None 
        if option_name_before != None:
            after = self.search_option(section_name, option_name_before)

        el = self.xml.getElementsByTagName(section_name)[0]
        result = el.insertBefore(element, after)	    
        if elements != [] :
            for i in elements:
                result.appendChild(i)

    def _determine_prev(self,section, list):
        result = None 
        for i in list:
            if i.getAttribute('name') == section:
                break

            result = i
        return result

    def get_prev(self, section): 
        '''
        get prev section 
        '''

        element = self.get_group_element()
        element_group = element.getElementsByTagName(u'group')
        result = self._determine_prev(section, element_group)
        return result
    def get_next(self, section): 
        '''
        get next section 
        '''

        element = self.get_group_element()
        element_group = element.getElementsByTagName(u'group')
        element_group.reverse()
        result = self._determine_prev(section, element_group)
        return result


    def get_group_element(self):
        element = self.xml.getElementsByTagName('groups')[0]
        return element
    def move_section_left(self, section):
        node_prev = self.get_prev(section)
        node = self.get_section_node(section)
        element = self.get_group_element()
        element.removeChild(node)
        element.insertBefore(node, node_prev)


    def move_section_right(self, section):
        node_next = self.get_next(section)
        node = self.get_section_node(section)
        element = self.get_group_element()
        element.removeChild(node_next)
        element.insertBefore(node_next, node)

    def get_opt_check(self, section, label):
        elem = self.search_option(section,label)
        return elem.getAttribute('option')
    def get_list_opt(self, section, label):
        '''
        Based on label of OptionList
        return a List with a Options in. 
        '''
        elem = self.search_option(section, label)
        list = elem.getElementsByTagName(u'option')
        result = [] 
        for i in list:
            name = i.getAttribute(u'name')
            result.append(name)
        return result
    def get_prev_opt(section, option):
        #XXX <- May be lack in other side 
        elem = self.search_option(section, option)
        pass

    def move_option_up(self, section,option, option_up):
        option_prev =  self.search_option(section, option_up)
        if option_up == None : 
            pass
        else: 
            elem = self.search_option(section, option)
            self.remove_opt(section, option)
            self.add_option_before(section, elem, option_prev)



    def move_option_down(self, section, option, option_down):
        option_next =  self.search_option(section, option_down)
        if option_down == None : 
            pass
        else: 
            self.remove_opt(section, option_down)
            elem = self.search_option(section, option)
            self.add_option_before(section, option_next, elem)




    def print_screen(self):
        xml.dom.ext.PrettyPrint(self.xml)
    def write_file(self,filename):
        '''
        Write Option List to XML file
        @param filename: File name of xml
        @type filename: String
        '''
        #self.print_screen()
        #self.xml.unlink()
        file_object = open(filename, "w")
        #xml.dom.ext.PrettyPrint(self.xml, file_object)
        doc_str = self.xml.toprettyxml(indent='', newl='')
        #doc_str = self.xml.toxml()
        #print doc_str
        doc_str = doc_str.replace('\n','')
        doc_str = doc_str.replace('\t','')
        #print doc_str
        self.xml = minidom.parseString(doc_str)
        self.xml.writexml(file_object, indent='\t', newl='\n')
        file_object.close()



# This is only for test a implementation of ProfileCore 

def main():
    s = ProfileCore("/home/kop/.umit/profile_editor.xml")
    #for group in s.groups:
        #print group
    #for sections in s.section_names:
        #print sections
    #for tab in s.tabs:
        #print tab
    #s.get_group()
    s.get_section('Scan')
    #s.add_section_before('New label','Ping')
    #s.add_option('Scan', 'option_list', 'dasdas', 'dasda', 
    #		 'dasdas', ['sdas','dasda'], 'Timing: ')
    s.remove_opt('Scan', 'TCP scan: ')
    s.print_screen()



if __name__ == "__main__":
    main() 
