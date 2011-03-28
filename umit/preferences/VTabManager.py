# Copyright (C) 2008-2010 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
#         Diogo Ricardo Marques Pinheiro <diogormpinheiro@gmail.com>
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

import os
import gtk
import gobject


from umit.core.UmitLogging import log
from umit.core.I18N import _

############
# Get Class
from umit.preferences.GeneralSettings import *
from umit.preferences.Inventory import InventoryTab
from umit.preferences.Interfaces import InterfaceDetails
from umit.preferences.Expose import ExposeGeneral
from umit.preferences.NSE import NSEGeneral
from umit.preferences.MapperSettings import MapperSettings

import umit.preferences.Interfaces
import umit.preferences.Expose
import umit.preferences.NSE
import umit.preferences.InterfaceEditor
##############
from umit.preferences.widgets.VTab import IconScroller

from umit.core.Paths import Path
pixmap = Path.pixmaps_dir

class VTabManager(gtk.VBox):
    def __init__(self):
        gtk.VBox.__init__(self)
        self.set_spacing(10)
        self.set_border_width(0)
        self.grab_focus()
        self.fields = []



        # General:
        self.fields.append({'name':_('General'),
                            'image':'general-m.png',
                            'class': GeneralSettings,
                            'cb':self._change_page_general})

        # Expose :

        items = []
        factory = umit.preferences.Expose.Factory()

        items.append({'name':_('Customize'),
                      'box': factory.create("settings")})

        items.append({'name':_('Profiles'),
                      'box': factory.create("profiles")})


        items.append({'name':_('Layout'),
                      'box': factory.create("window")})


        self.fields.append({'name':_('User Interface'),
                            'image':'expose-m.png',
                            'class': ExposeGeneral,
                            'cb':self._change_page_expose,
                            'items':items})

        # Interface / Details :

        items = []
        factory = umit.preferences.Interfaces.Factory()

        items.append({'name':_('Diff Colours'),
                      'box': factory.create("diff")})

        items.append({'name':_('Nmap Results'),
                      'box': factory.create("nmap")})


        items.append({'name':_('Search'),
                      'box': factory.create("search")})


        self.fields.append({'name':_('Nmap/Interface'),
                            'image':'fonts-m.png',
                            'items':items,
                            'class': InterfaceDetails,
                            'cb':self._change_page_interface})


        self.fields.append({'name':_('Inventory'),
                            'image':'fonts-m.png',
                            'class': InventoryTab(_('Inventory Settings')),
                            'cb':self._change_page_inventory,
                            'save': True})


        self.fields.append({'name':_('Mapper'),
                            'image':'fonts-m.png',
                            'class': MapperSettings,
                            'cb':self._change_page_mapper})
        
        # Interface Editor

        items = []
        factory = umit.preferences.InterfaceEditor.Factory()
        
        items.append({'name':_('Profile'),
                      'box': factory.create("profile"),
                      'save': True})
        
        items.append({'name':_('Wizard'),
                      'box': factory.create("wizard"),
                      'save': True})
        
        items.append({'name':_('Options'),
                      'box': factory.create("options"),
                      'save': True})

        self.fields.append({'name':_('Interface Editor'),
                            'image':'fonts-m.png',
                            'items': items,
                            'class': InterfaceDetails,
                            'cb':self._change_page_interface_editor})
        
        # NSE Facilitator :

        items = []
        factory = umit.preferences.NSE.Factory()

        items.append({'name':_('Sources'),
                      'box': factory.create("sources")})

        items.append({'name':_('Editor'),
                      'box': factory.create("editor")})

        items.append({'name':_('Columns'),
                      'box': factory.create("columns")})
        
        items.append({'name':_('Network'),
                      'box': factory.create("network")})


        self.fields.append({'name':_('NSE Facilitator'),
                            'image':'fonts-m.png',
                            'items':items,
                            'class': NSEGeneral,
                            'cb':self._change_page_nse})        

        self.pages_to_save = []
        
        for i in self.fields:
            if i.has_key('items'):
                item = i['items']
            else:
                item = None
            icont = IconScroller(i['name'],\
                                 os.path.join(pixmap, \
                                              "Preferences" , i['image']),
                                 item)
            i['icont'] = icont
            icont.set_size_request(-1,33)
            self.pack_start(icont, False, False)
            icont.connect("changed", i['cb'])
            icont.connect("close", self.close_all_tabs)
            
            # if item have key 'save' set to True, add page to save list
            if i.has_key('save') and i['save']:
                self.pages_to_save.append(i['class'])
            if item!=None:
                for it in item:
                    if it.has_key('save') and it['save']:
                        self.pages_to_save.append(it['box'])
            
            
    def _change_page_interface(self, widget, num):
        if num == 0:
            return False
        menu = self.fields[2]
        page = menu['items'][num-1]
        self.change_page(page['box'])

    def _change_page_expose(self, widget, num):

        if num == 0:
            return False
        menu = self.fields[1]
        page = menu['items'][num-1]
        self.change_page(page['box'])
        
    def _change_page_interface_editor(self, widget, num):
        if num == 0:
            return False
        menu = self.fields[5]
        page = menu['items'][num-1]
        self.change_page(page['box'])
        
    def _change_page_nse(self, widget, num):
        if num == 0:
            return False
        menu = self.fields[6]
        page = menu['items'][num-1]
        self.change_page(page['box'])

    def _change_page_general(self, widget, num):
        self.change_page(GeneralSettings(_('General Settings')))
        
    def _change_page_mapper(self, widget, num):
        self.change_page(MapperSettings(_('Mapper Settings')))
        
    def _change_page_inventory(self, widget, num):
        self.change_page(self.fields[3]['class'])

    def change_page(self, page):
        """
        Change page on main window
        """

        # Get main window
        pw = self.get_main_window()
        pw.change_page(page)
        
    def close_all_tabs(self, widget):
        """
        Close all other tabs
        """
        for tab in self.fields:
            if tab['icont'] != widget:
                tab['icont'].close()

    def get_main_window(self):
        return self.get_parent().get_parent()
    
    def save_changes(self):
        for page in self.pages_to_save:
            page.save()
