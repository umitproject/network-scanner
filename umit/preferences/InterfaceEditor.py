# Copyright (C) 2010 Adriano Monteiro Marques.
#
# Author: Diogo Ricardo Marques Pinheiro <diogormpinheiro@gmail.com>
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

import gtk
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higboxes import  hig_box_space_holder
from umit.preferences.FramesHIG import *

from umit.interfaceeditor.Profile import ProfileEdit
from umit.interfaceeditor.WizardEditor import WizardEdit
from umit.interfaceeditor.OptionManager import OptionList, OptionDisplay, OptionDisplayMainFrame
from umit.interfaceeditor.Main import InterfaceEditor
from umit.interfaceeditor.Tools import Proprieties, ToolDesign
from umit.core.I18N import _



class InterfaceOptions(TabBox):

    def __init__(self, name):
        self.notebook = HIGNotebook()
        self.list_options_box = OptionList()
        self._proprieties = Proprieties()
        TabBox.__init__(self, name)
        self.__pack_widgets()
        self.__option_display()
        
    def _create_widgets(self):
        """
        Create widgets 
        """
        self.main_vbox = gtk.VBox()

        self.display_frame = HIGFrame()
        self.display_frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.display_frame.set_border_width(6)

        self.hbox_edit = gtk.HBox()
        self.hspacer = gtk.HPaned()
        self.hspacer.set_border_width(0)
        self.vbox_right = HIGVBox()
        self.vbox_left = HIGVBox()

        self.notebook.set_scrollable(True)
        self.notebook.append_page(self.list_options_box, 
                                  HIGEntryLabel(_('Option List')))

        self.list_options_box.reload()
                
    def __pack_widgets(self):
        """
        Packing widgets of mainly windows 
        """
        #Pack widgets to main_box
        self.main_vbox.pack_start(self.hbox_edit, True, True)

        #Paned
        self.hbox_edit.pack_start(self.hspacer)
        self.hspacer.pack1(self.vbox_left, False, False)
        self.hspacer.set_position(480)
        self.hspacer.pack2(self.vbox_right, True, True)

        #Frame right 
        self.vbox_right.pack_start(self.notebook, True, True)

        self.pack_start(self.main_vbox, True, True)
        
    def __option_display(self):
        self.display_frame.set_label('Options')
        self.opt_display = OptionDisplayMainFrame()
        self.opt_display.set_options_list(self.list_options_box)
        self.list_options_box.set_option_display(self.opt_display)
        self.display_frame.add_with_properties(self.opt_display)
        self.vbox_left.pack_start(self.display_frame, False, False)
        
    def save(self):
        self.list_options_box.save()
        
        
class InterfaceWizard(TabBox):

    def __init__(self, name):
        self.wizard_box = None
        self._tooldesign = None
        self.notebook = HIGNotebook()
        self.list_options_box = OptionList()
        self._proprieties = Proprieties()
        self.create_wizard_edit()
        TabBox.__init__(self, name)
        self.__pack_widgets()
        self.vbox_left.pack_start(self.wizard_box, True, True)
        self._create_tooldesign()
        
    def create_wizard_edit(self):
        if self.wizard_box != None:
            self.wizard_box.set_proprieties(self._proprieties)
        if self.wizard_box ==None :
            self.wizard_box = WizardEdit(self.list_options_box.get_list_option())
            
        self.wizard_box.set_notebook(self.notebook)
        
    def _create_widgets(self):
        """
        Create widgets 
        """
        self.main_vbox = gtk.VBox()

        self.display_frame = HIGFrame()
        self.display_frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.display_frame.set_border_width(6)

        self.hbox_edit = gtk.HBox()
        self.hspacer = gtk.HPaned()
        self.hspacer.set_border_width(0)
        self.vbox_right = HIGVBox()
        self.vbox_left = HIGVBox()

        self.notebook.set_scrollable(True)

        self.list_options_box.reload()
                
    def __pack_widgets(self):
        """
        Packing widgets of mainly windows 
        """
        #Pack widgets to main_box
        self.main_vbox.pack_start(self.hbox_edit, True, True)

        #Paned
        self.hbox_edit.pack_start(self.hspacer)
        self.hspacer.pack1(self.vbox_left, False, False)
        self.hspacer.set_position(480)
        self.hspacer.pack2(self.vbox_right, True, True)

        #Frame right 
        self.vbox_right.pack_start(self.notebook, True, True)

        self.pack_start(self.main_vbox, True, True)
                
    def _create_tooldesign(self):
        '''
        create tooldesign that contains widgets to put 
        in work area of edit profile
        '''
        if self._tooldesign == None :     
            self._tooldesign = ToolDesign()

        if self._proprieties == None :
            self._proprieties = Proprieties()
        if self.notebook.get_n_pages() < 2:
            self.notebook.append_page(self._tooldesign, 
                                      HIGEntryLabel(_('Design')))
            self.notebook.append_page(self._proprieties, 
                                      HIGEntryLabel(_('Proprieties')))
        self.notebook.show_all()
        obj = self.wizard_box
        obj.set_proprieties(self._proprieties)
        profilecore = obj.get_profilecore()
        self._proprieties.set_profilecore(profilecore)
        
    def save(self):
        self.wizard_box.save()
        
        
class InterfaceProfile(TabBox):

    def __init__(self, name):
        self.profile_box = None
        self._tooldesign = None
        self.notebook = HIGNotebook()
        self.list_options_box = OptionList()
        self._proprieties = Proprieties()
        self.create_profile_edit()
        TabBox.__init__(self, name)
        self.__pack_widgets()
        self.vbox_left.pack_start(self.profile_box, True, True)
        self._create_tooldesign()
        
    def create_profile_edit(self):
        if self.profile_box != None:
            self.profile_box.set_proprieties(self._proprieties)
            
        if self.profile_box ==None :
            self.profile_box = ProfileEdit(self.list_options_box.get_list_option())
            
        self.profile_box.set_notebook(self.notebook)
        
    def _create_widgets(self):
        """
        Create widgets 
        """
        self.main_vbox = gtk.VBox()

        self.display_frame = HIGFrame()
        self.display_frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.display_frame.set_border_width(6)

        self.hbox_edit = gtk.HBox()
        self.hspacer = gtk.HPaned()
        self.hspacer.set_border_width(0)
        self.vbox_right = HIGVBox()
        self.vbox_left = HIGVBox()

        self.notebook.set_scrollable(True)

        self.list_options_box.reload()
                
    def __pack_widgets(self):
        """
        Packing widgets of mainly windows 
        """
        #Pack widgets to main_box
        self.main_vbox.pack_start(self.hbox_edit, True, True)

        #Paned
        self.hbox_edit.pack_start(self.hspacer)
        self.hspacer.pack1(self.vbox_left, False, False)
        self.hspacer.set_position(480)
        self.hspacer.pack2(self.vbox_right, True, True)

        #Frame right 
        self.vbox_right.pack_start(self.notebook, True, True)

        self.pack_start(self.main_vbox, True, True)
        
    def _create_tooldesign(self):
        '''
        create tooldesign that contains widgets to put 
        in work area of edit profile
        '''
        if self._tooldesign == None :     
            self._tooldesign = ToolDesign()

        if self._proprieties == None :
            self._proprieties = Proprieties()
        if self.notebook.get_n_pages() < 2:
            self.notebook.append_page(self._tooldesign, 
                                      HIGEntryLabel(_('Design')))
            self.notebook.append_page(self._proprieties, 
                                      HIGEntryLabel(_('Proprieties')))
        self.notebook.show_all()
        obj = self.profile_box
        obj.set_proprieties(self._proprieties)
        profilecore = obj.get_profilecore()
        self._proprieties.set_profilecore(profilecore)
        
    def save(self):
        self.profile_box.save()
        
        
class Factory:
    
    def create(self, name):
        if name == "profile":
            return InterfaceProfile(_('InterfaceEditor Profile'))
        elif name == "wizard":
            return InterfaceWizard(_('InterfaceEditor Wizard'))
        elif name == "options":
            return InterfaceOptions(_('InterfaceEditor Options'))