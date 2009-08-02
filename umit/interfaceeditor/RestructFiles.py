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

'''
This file solve the strutural problems between wizard or profile and options. 
If a option don't exists this class should be remove a option of profile or 
wizard or add option to options.xml with anything to change later. 

Other functionality of the class is search a option on the Profile and Wizard
and return a list of option that should be added or removed at option.xml

'''


class RestructFiles:
    def __init__(self, option_core, wizard_core, profile_core):
        self.optioncore = option_core
        self.wizardcore = wizard_core
        self.profilecore = profile_core

    def _search(self, option, core):
        group_list = core.groups 


        result = []
        for section_name in group_list:
            grp = core.xml.getElementsByTagName(section_name)[0]
            for elem in grp.childNodes:
                try: elem.getAttribute(u'label')
                except: pass
                else: 

                    if elem.tagName == 'option_check':
                        if elem.getAttribute(u'option') == option:
                            result.append([section_name, 
                                           elem.getAttribute(u'label')])
                    elif elem.tagName == 'option_list':
                        #search in option list: 		
                        for j in elem.childNodes:
                            try: j.tagName
                            except:pass
                            else:
                                if j.getAttribute(u'name')==option:
                                    result.append([section_name, 
                                                   elem.getAttribute(u'label'),
                                                   j.getAttribute(u'name')])

        return result


    def _search_profile(self, option):
        return self._search(option, self.profilecore)
    def _search_wizard(self, option):
        return self._search(option, self.wizardcore)

    def get_places(self,option):
        profile = self._search_profile(option)
        wizard = self._search_wizard(option)
        return profile, wizard
    def restruct_all_files(self):
        pass


