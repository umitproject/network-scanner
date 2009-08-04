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


from gettext import gettext as _

import gtk

#HIG

from higwidgets.higwindows import HIGWindow, HIGMainWindow 
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer,hig_box_space_holder
from higwidgets.higexpanders import HIGExpander
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog, HIGDialog
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higframe import HIGFrame
import gobject
from os.path import split, join

from umit.interfaceeditor.Profile import ProfileEdit
from umit.interfaceeditor.WizardEditor import WizardEdit

from umit.core.UmitLogging import log
from umit.core.I18N import _
from umit.interfaceeditor.OptionManager import OptionList, OptionDisplay, OptionDisplayMainFrame
from umit.core.Paths import Path

profile_editor =  Path.profile_editor
wizard =  Path.wizard

from umit.interfaceeditor.Tools import ToolDesign, Proprieties

from umit.interfaceeditor.Command import command_manager


class InterfaceEditor(HIGMainWindow):
    def __init__(self):
        HIGMainWindow.__init__(self)
        self._proprieties = None
        self.profile_box = None 
        self.wizard_box = None 
        self._current_edit_mode = None 
        self._tooldesign = None
        self.profile_box_b = None 
        self.wizard_box_b = None 
        self.edit_mode_opt = None
        self._show_bar = True
        self.set_title(_('Interface Editor'))
        self.set_size_request(800, 400)
        self.set_position(gtk.WIN_POS_CENTER)
        #self.maximize()
        self.list_options_box = OptionList()
        self.notebook = HIGNotebook()
        self._proprieties = Proprieties()
        self.create_profile_edit()
        self.create_wizard_edit()
        self.obj = self.profile_box
        #Create Widgets
        self.__create_widgets()
        #Packing - Group of widgets  
        self.__pack_widgets()    
        self.__option_display()
        self.edit_mode_opt = "Options"


        self.connect("delete_event", self._destroy)

        self.opt_display.set_profile(self.profile_box)
        self.opt_display.set_wizard(self.wizard_box)
        self.profile_box.notebook.connect_after('need-save', self._update_menu_s)
        self.wizard_box.notebook.connect_after('need-save', self._update_menu_s)
        self.profile_box.notebook.connect_after('changed', self._update_menu)
        self.wizard_box.notebook.connect_after('changed', self._update_menu)
        self.opt_display.connect_after('need-save', self._update_menu_s)

    def _update_menu(self, actions, others, page):
        obj = None 
        if self.edit_mode_opt == "Profile":
            obj = self.profile_box
        elif self.edit_mode_opt == "Wizard":
            obj = self.wizard_box
        if obj == None:
            return 
        #Check if there is something selected:
        current_page = obj.notebook.get_nth_page(obj.notebook.get_current_page())
        if obj.notebook._old_select != None:
            #Section is Selected
            log.debug('Section is selected << updating toolbar')

            pass
        elif current_page._old_selected != None:
            #Item Selected
            log.debug('Item is selected << updating toolbar')
            pass



    def _update_menu_s(self, action, others, page):
        log.debug('<<< Update Main menubar ')
        save = self.main_action_group.get_action('Save')
        save_all = False
        if self.edit_mode_opt == "Profile":
            log.debug('profile updating menubar save')
            value = self.profile_box.is_changed()
            save.set_sensitive(value)
        elif self.edit_mode_opt == "Wizard":
            log.debug('wizard updating menubar save')
            value = self.wizard_box.is_changed()
            save.set_sensitive(value)

        elif self.edit_mode_opt == 'Options': 
            log.debug('options updating menubar save')
            value = self.opt_display.is_changed()
            save.set_sensitive(value)

        save_all = self.opt_display.is_changed() or \
                 self.wizard_box.is_changed() or self.profile_box.is_changed()
        self.main_action_group.get_action('Save all').set_sensitive(save_all)


        #


    def _destroy(self, widget, event):
        self.destroy()
    def create_wizard_edit(self):
        '''
        create a profile area editing 
        and connect to Undo Redo Manager to update the buttons 
        '''
        if self.wizard_box != None:
            self.wizard_box.set_proprieties(self._proprieties)
            #return
        if self.wizard_box ==None :
            self.wizard_box = WizardEdit(self.list_options_box.get_list_option())
        #else:
        #    self.profile_box.show_all()
        #command_manager.connect_after('changed', self._update_undo_redo_cb)
        self.wizard_box.set_notebook(self.notebook)

    def create_profile_edit(self):
        '''
        create a profile area editing 
        and connect to Undo Redo Manager to update the buttons 
        '''
        if self.profile_box != None:
            self.profile_box.set_proprieties(self._proprieties)
            #return
        if self.profile_box ==None :
            self.profile_box = ProfileEdit(self.list_options_box.get_list_option())
        #else:
        #    self.profile_box.show_all()
        command_manager.connect_after('changed', self._update_undo_redo_cb)
        self.profile_box.set_notebook(self.notebook)
    def _update_undo_redo_cb(self, action, other):
        '''
        Verify if exists undo and redo
        and update the buttons on the toolbar/menubar
        #DO:
        - sensitive -> True/False
        - Ajust tips 
        ####
        '''

        can_undo = command_manager.can_undo() 
        can_redo = command_manager.can_redo()
        self.main_action_group.get_action('Undo').set_sensitive(can_undo)
        self.main_action_group.get_action('Redo').set_sensitive(can_redo)
        if can_undo:
            self.main_action_group.get_action('Undo').tooltip = 'sss'
            self.main_action_group.get_action('Undo').create_menu_item()
    def __create_widgets(self):
        """
        Create widgets 
        """
        self.main_vbox = gtk.VBox()
        self.widgets = {}

        #UI Manager
        self.__create_ui_manager()
        #Table - contains menubar and toolbar


        #Menubar
        self.__create_menubar()
        #Toolbar
        self.__create_toolbar()

        self.display_frame = HIGFrame()
        self.display_frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.display_frame.set_border_width(6)

        self.hbox_edit = gtk.HBox()
        self.hspacer = gtk.HPaned()
        self.hspacer.set_border_width(0)
        self.vbox_right = HIGVBox()
        self.vbox_left = HIGVBox()



        self.edit_mode_exp = gtk.Expander(_('Edit Modes'))
        self.edit_mode_box = self.create_edit_mode()




        self.notebook.set_scrollable(True)
        self.notebook.append_page(self.list_options_box, 
                                  HIGEntryLabel(_('Option List')))

        self.list_options_box.reload()

        self.__create_status_bar()
    def __option_display(self):

        self.display_frame.set_label('Options')
        self.opt_display = OptionDisplayMainFrame()
        self.opt_display.set_options_list(self.list_options_box)
        self.list_options_box.set_option_display(self.opt_display)
        self.display_frame.add_with_properties(self.opt_display)
        self.vbox_left.pack_start(self.display_frame, False, False)


    def __pack_widgets(self):
        """
        Packing widgets of mainly windows 
        """

        self.add(self.main_vbox)

        #Pack widgets to main_box

        self.main_vbox.pack_start(self.hbox_edit, True, True)

        #Paned
        self.hbox_edit.pack_start(self.hspacer)
        separator = gtk.VSeparator()
        self.hspacer.pack1(self.vbox_left, False, False)
        self.hspacer.set_position(580)
        self.hspacer.pack2(self.vbox_right, False, True)

        #Edit Mode
        self.edit_mode_exp.add(self.edit_mode_box)
        self.edit_mode_exp.set_expanded(True)

        #Frame right 
        self.vbox_right.pack_start(self.edit_mode_exp, False, False)
        self.vbox_right.pack_end(self.notebook, True, True)

        #Status bar 
        self.main_vbox.pack_start(self.statusbar,False, False)

    def create_edit_mode(self):
        """
        Create a treeview that contains a three edit modes 
        returns vbox contains a treeview

        @return: returns the treeview with list of edit modes 
        @rtype: vbox
        """

        model =  gtk.TreeStore(gtk.gdk.Pixbuf,gobject.TYPE_STRING)
        self.edit_mode_tv = gtk.TreeView(model)
        self.edit_mode_tv.set_headers_visible(False)
        renderer = gtk.CellRendererText()
        cell_renderer_pix = gtk.CellRendererPixbuf()
        column = gtk.TreeViewColumn()
        column.set_title(_('Name'))
        column.pack_start(cell_renderer_pix, False)
        column.add_attribute(cell_renderer_pix, 'pixbuf', 0)
        column.pack_start(renderer, True)
        column.add_attribute(renderer, 'text', 1)


        self.edit_mode_tv.append_column(column)
        myiter = model.insert_before(None, None)
        icon = gtk.Image()
        icon = icon.render_icon('gtk-edit',gtk.ICON_SIZE_MENU)
        model.set_value(myiter, 0, icon)
        model.set_value(myiter, 1, "Profile")
        myiter = model.insert_before(None, None)
        icon = gtk.Image()
        icon = icon.render_icon('gtk-convert',gtk.ICON_SIZE_MENU)
        model.set_value(myiter, 0, icon)
        model.set_value(myiter, 1, "Wizard")
        myiter = model.insert_before(None, None)
        icon = gtk.Image()

        icon = icon.render_icon(gtk.STOCK_DND_MULTIPLE, gtk.ICON_SIZE_MENU)
        model.set_value(myiter, 0, icon)
        model.set_value(myiter, 1, "Options")
        selection = self.edit_mode_tv.get_selection()
        selection.select_iter(myiter)
        self.edit_mode_tv.connect("cursor-changed", self.change_edit_mode)
        vbox = HIGVBox()
        vbox.pack_start(self.edit_mode_tv, False, False)
        return vbox


    def change_edit_mode(self, widget):
        """
        Change box of main screen and others changes at toolbar
        """
        selection  = self.edit_mode_tv.get_selection()
        (model,iter) = selection.get_selected()	
        edit = model.get_value(iter, 1)
        if edit == "Options" and not self.edit_mode_opt == "Options":
            #
            self._remove_previews()
            self.edit_mode_opt = "Options"
            #self.vbox_left.pack_start(self.display_frame, False, False )
            self.display_frame.show_all()
            if self.notebook.get_n_pages > 1 :
                self.notebook.remove_page(-1)
                self.notebook.remove_page(-1)
            self._set_menus_editor(False)


        elif edit == "Profile" and not self.edit_mode_opt == "Profile":
            #
            self._remove_previews()
            self.edit_mode_opt="Profile"
            bool = self.profile_box_b==None 
            self.create_profile_edit()
            if bool:
                self.vbox_left.pack_start(self.profile_box, True, True)
                self.profile_box_b= True
            log.debug('<<< show :: Profile Edit Mode :: ')
            self.profile_box.show_all()
            self.profile_box.notebook.put_on_page()
            self._create_tooldesign()
            self._set_menus_editor(True)
            self.profile_box.show()
            self.obj = self.profile_box
        elif edit == "Wizard" and not self.edit_mode_opt == "Wizard":
            log.debug('<<< show :: Wizard Edit Mode - basic mode ')
            self._remove_previews()
            self.edit_mode_opt="Wizard"
            self._set_menus_editor(True)
            bool = self.wizard_box_b==None 
            self.create_wizard_edit()
            if bool:
                self.vbox_left.pack_start(self.wizard_box, True, True)
                self.wizard_box_b = True

            self.wizard_box.show_all()
            self.wizard_box.notebook.put_on_page()
            self._create_tooldesign()
            self.wizard_box.show()
            self.obj = self.wizard_box	    


    def _remove_previews(self):
        '''
        Remove the previews Edit mode
        '''
        #XXX Lack the toolbars and some ajusts
        if self.edit_mode_opt == "Profile":
            #self.vbox_left.remove(self.profile_box)
            self.profile_box.hide_all()
        elif self.edit_mode_opt == "Options":
            #self.vbox_left.remove(self.display_frame)
            self.display_frame.hide_all()
        elif self.edit_mode_opt == "Wizard":
            self.wizard_box.hide_all()

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
        if self.edit_mode_opt == "Profile":
            obj = self.profile_box
        elif self.edit_mode_opt == "Wizard":
            obj = self.wizard_box
        obj.set_proprieties(self._proprieties)
        profilecore = obj.get_profilecore()
        self._proprieties.set_profilecore(profilecore)

    def __optinlist_from_group(self):
        """
        After Select a Option from a group this treeview refresh options lists
        that each group contains
        """
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

        self.toolbar = self.ui_manager.get_widget('/toolbar')
        self.toolbar.set_style(gtk.TOOLBAR_BOTH)

        self.main_vbox.pack_start(self.toolbar, False, True,0)
        self.toolbar.show_all()
    def save_all(self, widget):
        #if self.opt_display.is_changed(): 
            #XXX BUG (is_changed method is in OptionList)
        self.list_options_box.save()
        if self.profile_box.is_changed():
            self.profile_box.save()
        if self.wizard_box.is_changed():
            self.wizard_box.save()

    def _set_menus_editor(self, value):
        self.main_action_group.get_action('Items').set_sensitive(value)
        self.main_action_group.get_action('Section').set_sensitive(value)
        if self.edit_mode_opt!=None:
            self._update_menu_s(None, None, None)

    def save(self, widget):
        if self.edit_mode_opt == 'Options':
            obj = self.list_options_box
        elif self.edit_mode_opt  == 'Profile':
            obj = self.profile_box
        elif self.edit_mode_opt == 'Wizard':
            obj = self.wizard_box

        obj.save()
    def quit(self, widget):
        self.destroy()
    def np(self, widget):
        print "Don't work yet"
    def __create_ui_manager(self):
        """
        Create a UI Manager
        """
        self.ui_manager = gtk.UIManager()
        self.main_action_group = gtk.ActionGroup('MainActionGroup')
        self.main_actions = [ \
            ('File', None, _('_File'), None),
            ('Save', gtk.STOCK_SAVE, _('_Save'), None, _('Save'), self.save),
            ('Save all', gtk.STOCK_SAVE, _('_Save all'), None, _('Save all'),
             self.save_all),
            ('Quit', gtk.STOCK_QUIT, _('_Quit'), None, _('Quit'), self.quit),
            ('Edit', None, _('Edit'), None),
            ('Undo', gtk.STOCK_UNDO, _('_Undo'), '<Control>z', _('Undo'), self._undo_cb),
            ('Redo', gtk.STOCK_REDO, _('_Redo'), '<Control>r', _('Redo'), self._redo_cb),
            ('View', None, _('View'), None),
            ('Right Bar', None, _('_Right Bar'), None, 
             _('Right Bar'), self._hide_right),
            ('Tools', None, _('Tools'), None),
            ('Section', None, _('Section'), None),
            ('Items', None, _('Items'), None),
            ('Insert label', None, _('_Label'), None, 
             _('Insert label'), self.np),
            ('New Section', None, _('_New Section'), None, 
             _('New Section'), self._add_section),	    
            ('Remove Section Label', None, _('_Remove Section Label'), None, 
             _('Remove Section Label'), self._remove_section),
            ('Remove Section', None, _('_Remove Section'), None, 
             _('Remove Section'), self._remove_section),
            ('Add new voidplace', None, _('_Add new voidplace'), None, 
             _('Add new voidplace'), self._add_place),
            ('Remove option', None, _('_Remove Option'), None, 
             _('Remove option'), self._remove_option),
            ('Remove voidplace', None, _('_Remove voidplace'), None, 
             _('Remove voidplace'), self._remove_option),
            ('Add option selected', None, _('_Add option selected'), None, 
             _('Add option selected'), self.np),
            ('Move Section Left', None, _('_Move Section Left'), None, 
             _('Move Section Left'), self._move_section_left),
            ('Move Section Right', None, _('_Move Section Right'), None, 
             _('Move Section Right'), self._move_section_right),
            ('Move Item Down', None, _('_Move Item Down'), None, 
             _('Move Item Down'), self._move_item_down),
            ('Move Item Up', None, _('_Move Item Up'), None, 
             _('Move Item Up'), self._move_item_up),
            ('Help', None, _('Help'), None),
            ('About', gtk.STOCK_PASTE, _('_About'), None, _('About'), self.np),

        ]

        self.ui_info = """
            <menubar>
            <menu action='File'>
            <menuitem action='Save'/>
            <menuitem action='Save all'/>
            <separator/>
            <menuitem action='Quit'/>
            </menu>
            <menu action='Edit'>
            <menuitem action='Undo'/>
            <menuitem action='Redo'/>
            </menu>
            <menu action='View'>
            <menuitem action='Right Bar'/>
            </menu>
            <menu action='Section'>
            <menuitem action='Insert label'/>
            <menuitem action='New Section'/>
            <menuitem action='Remove Section Label'/>
            <menuitem action='Remove Section'/>
            <menuitem action='Move Section Left'/>
            <menuitem action='Move Section Right'/>
            </menu>
            <menu action='Items'>
            <menuitem action='Add new voidplace'/>
            <menuitem action='Remove option'/>
            <menuitem action='Remove voidplace'/>
            <menuitem action='Move Item Up'/>
            <menuitem action='Move Item Down'/>
            </menu>

            </menubar>
            <toolbar>
            <toolitem action='Save'/>
            <toolitem action='Save all'/>
            <separator/>
            <toolitem action='Undo'/>
            <toolitem action='Redo'/>

            <separator/>
            <toolitem action='Quit'/>
            </toolbar>
            """


        self.main_action_group.add_actions(self.main_actions)
        self.main_accel_group = gtk.AccelGroup()
        for action in self.main_action_group.list_actions():

            action.set_accel_group(self.main_accel_group)
            action.connect_accelerator()

        #ENABLE = FALSE
        self.main_action_group.get_action('Save all').set_sensitive(False)
        self.main_action_group.get_action('Save').set_sensitive(False)
        self.main_action_group.get_action('Undo').set_sensitive(False)
        self.main_action_group.get_action('Redo').set_sensitive(False)

        self._set_menus_editor(False)
        #END ENABLE 

        self.ui_manager.insert_action_group(self.main_action_group, 0)
        #try:
        self.ui_manager.add_ui_from_string(self.ui_info)
        self.add_accel_group(self.main_accel_group)     
        #except gobject.GError, msg:
        #    print "Fails %s" % msg


    # ACTIONS 
    def _add_section(self, widget):
        self.obj._toolbar._add_section(widget)
    def _remove_section(self, widget):
        self.obj._toolbar._remove_section(widget)  
    def _add_place(self,widget):
        self.obj._toolbar._add_place(widget)  
    def _move_item_up(self, widget):    
        self.obj._toolbar._move_item_down(widget)
    def _move_item_down(self, widget):    
        self.obj._toolbar._move_item_down(widget)
    def _move_section_left(self, widget):
        self.obj._toolbar._move_section_left(widget)
    def _move_section_right(self, widget):
        self.obj._toolbar._move_section_right(widget)
    def _remove_option(self, widget):
        self.obj._toolbar._remove_option(widget)

    def _hide_right(self, widget):
        if self._show_bar:
            self.vbox_right.hide_all()
        else: 
            self.vbox_right.show_all()
        self._show_bar = not self._show_bar

    def _undo_cb(self, widget):
        command_manager.do_undo()
    def _redo_cb(self, widget):
        command_manager.do_redo()

    def __create_menubar(self):
        """
        Create a menubar 
        """

        self.menubar = self.ui_manager.get_widget('/menubar')

        self.main_vbox.pack_start(self.menubar,False,True, 0)

        self.menubar.show_all()

    def __create_status_bar(self):
        '''
        create status bar 
        '''
        self.statusbar = gtk.Statusbar()

        context_id = self.statusbar.push(1," ")
        self.statusbar.show()


if __name__ == '__main__':
    p = umitInterfaceEditor()
    p.show_all()
    gtk.main()
