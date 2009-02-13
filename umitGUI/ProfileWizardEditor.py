#!/usr/bin/env python
# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Luis Bastiao Silva <luis.kop@gmail.com>
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


from gettext import gettext as _

import gtk

#HIG

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer, hig_box_space_holder
from higwidgets.higexpanders import HIGExpander
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog, HIGDialog
from higwidgets.hignotebooks import HIGNotebook
import gobject
from os.path import split, join

from umitCore.PWOptions import PWOptions

from umitCore.Paths import Path
Path.set_umit_conf(join(split(__file__)[0], 'config', 'umit.conf'))

profile_editor =  Path.profile_editor

# This is my first tests with higwidgets

class ProfileWizardEditor(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self)
        self.set_title(_('Profile and Wizard Editor'))
        #self.set_default_size(700, 500)

        self.set_position(gtk.WIN_POS_CENTER)
        
        #Create Widgets
        self.__create_widgets()
        #Packing - Group of widgets  
        self.__pack_widgets()    
        


    def __create_widgets(self):
        """
        Create widgets 
        """
        
        
        self.main_vbox = HIGVBox()
        self.widgets = {}
        
        #UI Manager
        self.__create_ui_manager()
        #Menubar
        self.__create_menubar()
        
        
        
        #Toolbar
        self.__create_toolbar()

        #Mainly frame - contains a toolbar, and notebook 
        #(tabs with Wizard, Profile and Options)
        self.hbox_edit = HIGHBox()
        

        """
        Notebook
        """

        self.notebook = HIGNotebook()
        
        self.list_combo = gtk.combo_box_entry_new_text()
        self.list_combo.append_text("New Style")


        """
        Profile Tab 
        """
        # Contains the combo and a HBox
        self.profile_vbox = HIGVBox() 
        # HBox - three columns 
        self.profile_hbox = HIGHBox()    
        self.profile_vbox_group = HIGVBox()
        self.profile_vbox_option = HIGVBox()
        self.profile_group_sw = HIGScrolledWindow()
        self.profile_group_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.profile_group_sw.set_policy(gtk.POLICY_AUTOMATIC, 
                                         gtk.POLICY_AUTOMATIC)
        
        self.profile_group_sw.set_size_request(150,250)
        self.profile_vbox_proprieties = HIGVBox()

        self.__grouplist()
        self.profile_separator = gtk.VSeparator()    
        self.__optinlist_from_group()
        
    
        self.profile_separator2 = gtk.VSeparator()    
        # Buttons << and >>
        # BBOX buttons move right move left
        self.profile_bbox_rl = gtk.VButtonBox()
 
        
        self.profile_bbox_rl.set_layout(gtk.BUTTONBOX_SPREAD)
        self.profile_bbox_rl.set_spacing(12)
        #Buttons 
        self.profile_left_but = HIGButton()
        self.profile_left_but.set_label('<<')
        self.profile_right_but = HIGButton()
        self.profile_right_but.set_label('>>')
        #Add Buttons to ButtonBox
        self.profile_bbox_rl.add(self.profile_right_but)
        self.profile_bbox_rl.add(self.profile_left_but)


        self.profile_separator3 = gtk.VSeparator()    

        self.__proprieties()    
        
        """
        Wizard Tab
        """

        self.wizard_vbox = HIGVBox()
        self.wizard_group_label = HIGSectionLabel(_('Group List'))
        

        """
        Down of notebook 
        """

        self.main_buttons_down = gtk.HButtonBox()
        self.main_buttons_down.set_layout(gtk.BUTTONBOX_END)
        self.main_buttons_down.set_spacing(12)
        #Buttons 
        self.main_down_ok_but = HIGButton(stock='gtk-ok')
        self.main_down_cancel_but = HIGButton(stock='gtk-cancel')
        self.main_down_help_but = HIGButton(stock='gtk-help')
        #Add Buttons to ButtonBox
        self.main_buttons_down.add(self.main_down_ok_but)
        self.main_buttons_down.add(self.main_down_cancel_but)
        self.main_buttons_down.add(self.main_down_help_but)



    def __pack_widgets(self):
        """
        Packing widgets of mainly windows 
        """
        
        self.add(self.main_vbox)

        #Pack widgets to main_box
        self.main_vbox.pack_start(self.hbox_edit)
        
        #HBox_Edit
        self.hbox_edit._pack_expand_fill(self.notebook)
            
        #Profile:
        
        self.profile_vbox._pack_noexpand_nofill(self.list_combo)
        self.profile_vbox._pack_expand_fill(self.profile_hbox)
        
        """
        Group
        """
        
        self.profile_hbox._pack_expand_fill(self.profile_vbox_group)
        self.profile_vbox_group._pack_noexpand_nofill(self.profile_group_label)
        
        self.profile_vbox_group._pack_expand_fill(self.profile_group_sw)
        box = HIGHBox()
        box._pack_expand_fill(self.treeview)
        self.profile_group_sw.add(box)
        
        
        self.profile_hbox.pack_start(self.profile_separator)
       
        """
        Option
        """
        
        self.profile_hbox.pack_start(self.profile_vbox_option)
        self.profile_vbox_option._pack_noexpand_nofill(self.profile_option_list_lbl)
        self.profile_vbox_option._pack_noexpand_nofill(self.profile_optionlist_tvw)
        
        
        self.profile_hbox._pack_noexpand_nofill(
            self.profile_separator2)
        
        """
        Buttons move left and move right 
        """

        self.profile_hbox.pack_start(
            self.profile_bbox_rl)
        
        
        #self.profile_hbox._pack_noexpand_nofill(self.profile_separator3)
        """
        Proprieties
        """
        
        self.profile_hbox.pack_start(self.profile_vbox_proprieties)
        self.profile_vbox_proprieties.pack_start(self.prop_frame_option)        
        self.profile_vbox_proprieties.pack_start(self.prop_frame)


        #Wizard: 

        self.wizard_vbox._pack_noexpand_nofill(self.wizard_group_label)
        
        self.notebook.append_page(self.profile_vbox, 
                                  gtk.Label(_('Profile')))
        self.notebook.append_page(self.wizard_vbox, 
                                  gtk.Label(_('Wizard')))

        """
        Down --- 
        after notebook 
        Apply changes, quit or cancel

        """
        

        self.main_vbox._pack_noexpand_nofill(self.main_buttons_down)



    def __optinlist_from_group(self):
        """
        After Select a Option from a group this treeview refresh options lists that 
        each group contains
        """
        self.profile_option_list_lbl = HIGSectionLabel(_('Option of List'))

        model =  gtk.TreeStore(gobject.TYPE_STRING)
        self.profile_optionlist_tvw = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", renderer, text=0)
        self.profile_optionlist_tvw.append_column(column)
        
        self.wizard_file = PWOptions(profile_editor)
        group_list = self.wizard_file.read("group", "name", "group")
        for i,v in group_list:
            myiter = model.insert_after(None, None)
            model.set_value(myiter, 0, i)


    def __proprieties(self):
        """

        Create a editable options - Proprieties of Options
        """
    

        #Create a listview with options
        self.prop_frame_option = gtk.Frame()
        self.prop_frame_option.set_label("List Options")
        self.prop_frame_option.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        prop_sw = HIGScrolledWindow()
        prop_sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        prop_sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        prop_sw.set_size_request(150,250)
        model =  gtk.TreeStore(gobject.TYPE_STRING)
        treeview = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", renderer, text=0)
        treeview.append_column(column)
        self.prop_frame_option.add(treeview)
        self.prop_frame_option.add(prop_sw)
        
        

        """
        Box Edit 
        """

        #Frame
        self.prop_frame = gtk.Frame()
        self.prop_frame.set_label("Edit Option")
        self.prop_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)
        
        self.prop_exp = HIGExpander("Proprieties")

        label = gtk.Label('s')
        self.prop_exp.add(label)
        self.prop_frame.add(self.prop_exp)    
        


    def __grouplist(self):
        """
        Group List, Tree view 
        """
        self.profile_group_label = HIGSectionLabel(_('Group List'))
        model =  gtk.TreeStore(gobject.TYPE_STRING)
        self.treeview = gtk.TreeView(model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Name", renderer, text=0)
        self.treeview.append_column(column)
        
        self.wizard_file = PWOptions(profile_editor)
        group_list = self.wizard_file.read("group", "name", "group")
        for i,v in group_list:
            myiter = model.insert_after(None, None)
            model.set_value(myiter, 0, i)



    def __create_toolbar(self):
        """
        Create a Main Toolbar of Profile Wizard Editor
        """
        
        self.toolbar = gtk.Toolbar()
    
    
    def np(self):
        print "np"
    def __create_ui_manager(self):
        """
        Create a UI Manager
        """
        
        self.ui_manager = gtk.UIManager()
        self.main_action_group = gtk.ActionGroup('MainActionGroup')
        self.main_actions = [ \
            ('Manage', None, _('_Manage'), None),
            ('Open', gtk.STOCK_OPEN, _('_Open'), None, _('Open'), self.np),
            ('Quit', gtk.STOCK_OPEN, _('_Quit'), None, _('Quit'), self.np),
            ('Edit', None, _('Edit'), None),
            ('Undo', gtk.STOCK_OPEN, _('Undo'), None, _('Edit'), self.np),
        ]

        self.ui_info = """<menubar>
            <menu action='Manage'>
                  <menuitem action='Open'/>
            <menuitem action='Quit'/>
            </menu>
            <menu action='Edit'>
                <menuitem action='Edit'/>
             </menu>
          </menubar>
        """


        self.main_action_group.add_actions(self.main_actions)
        self.main_accel_group = gtk.AccelGroup()
        for action in self.main_action_group.list_actions():
            action.set_accel_group(self.main_accel_group)
            action.connect_accelerator()

        self.ui_manager.insert_action_group(self.main_action_group, 0)
        #try:
        self.ui_manager.add_ui_from_string(self.ui_info)
        #except gobject.GError, msg:
        #    print "Fails %s" % msg

    
    def __create_menubar(self):
        """
        Create a menubar 
        """
        
        self.menubar = self.ui_manager.get_widget('/menubar')
        self.main_vbox._pack_noexpand_nofill(self.menubar)
    
    
if __name__ == '__main__':
    p = ProfileWizardEditor()
    p.show_all()
    gtk.main()
