#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2007 Adriano Monteiro Marques
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gtk

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higbuttons import HIGButton
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel, HIGDialogLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higframe import HIGFrame
from higwidgets.higdialogs import HIGDialog

from umit.gui.Wizard import Wizard
from umit.core.NmapCommand import CommandConstructor

from ProfileEditor import ProfileEditor
from umit.core.UmitConf import CommandProfile
from umit.core.I18N import _

from umit.core.Paths import Path

import gobject

profile_editor = Path.profile_editor

class ProfileManager(HIGWindow):
    """
    Create a Profile Manager 
    """
    def __init__(self):
        HIGWindow.__init__(self, type=gtk.WINDOW_TOPLEVEL)
        self.set_title('Profile Manager')
        self.set_position(gtk.WIN_POS_CENTER)
        self.__create_widgets()
        self.add(self.vbox_main)
        self.__fill_widgets()
        self.__pack_widgets()
        self.__scan_notebook = None


    def __create_widgets(self):

        self.vbox_main = HIGVBox()

        self.main_frame = HIGFrame("Profiles")
        #self.main_frame.set_shadow_type(gtk.SHADOW_ETCHED_OUT)

        self.align = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
        self.align.set_padding(0,0,12,0)

        self.vbox = HIGVBox()
        self.profiles_sw = HIGScrolledWindow()
        #TreeView
        self.model = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
        #self.modelfilter = self.model.filter_new()
        self.profiles_tv = gtk.TreeView(self.model)
        renderer = gtk.CellRendererText()
        column = gtk.TreeViewColumn(_("Name"), renderer, text=0)
        self.profiles_tv.append_column(column)
        renderer_hint = gtk.CellRendererText()
        column_hint = gtk.TreeViewColumn(_("Hint"), renderer_hint, text=1)
        self.profiles_tv.append_column(column_hint)
        #self.profiles_tv.set_model(self.modelfilter)
        #Info 
        self.hbox_info = HIGHBox()
        self.command_label = HIGEntryLabel('Command: ')
        self.command_entry = HIGTextEntry()
        self.command_entry.set_editable(False)

        #Buttons
        self.hbox_buttons = HIGHBox()

        self.wiz_button = HIGButton(title='Wizard', stock='gtk-convert')
        self.wiz_button.connect("clicked", self.new_wiz)

        self.edit_button = HIGButton(stock='gtk-edit')
        self.edit_button.connect("clicked", self.open_peditor)
        self.new_button = HIGButton(stock='gtk-new')
        self.new_button.connect("clicked", self.open_peditor)
        self.copy_button = HIGButton(stock='gtk-copy')
        self.copy_button.connect("clicked", self.copy_profiles)
        self.delete_button = HIGButton(stock=gtk.STOCK_DELETE)
        self.delete_button.connect('clicked', self.delete_profile)	
        #Apply Buttons
        self.cancel_button = HIGButton(stock='gtk-close')
        self.cancel_button.connect("clicked", self.quit)

    def __fill_widgets(self):


        self.profiles = CommandProfile()
        self._reload_profile_list()

        #selection = self.profiles_tv.get_selection()
        #selection.connect("changed", self.change_nmap_command)
        self.profiles_tv.connect("cursor-changed", self.change_nmap_command)

    def __pack_widgets(self):
        """
        Pack all widgets of windows 
        """
        self.vbox_main.pack_start(self.main_frame, True, True)
        self.main_frame.add(self.align)
        self.align.add(self.vbox)
        self.vbox.set_border_width(6)

        self.vbox.pack_start(self.profiles_sw, True, True, 0)

        self.hbox_info.pack_start(self.command_label, False,False,0)
        self.hbox_info.pack_start(self.command_entry, True, True, 0)
        self.vbox.pack_start(self.hbox_info, False,False,0)



        self.hbox_buttons.pack_end(self.cancel_button)    
        self.hbox_buttons.pack_end(self.copy_button, True, True)
        self.hbox_buttons.pack_end(self.edit_button, True, True)
        self.hbox_buttons.pack_end(self.delete_button, True, True)
        self.hbox_buttons.pack_end(self.new_button, True, True)
        self.hbox_buttons.pack_end(self.wiz_button, True, True)
        self.hbox_buttons.set_spacing(6)
        self.vbox_main.pack_start(self.hbox_buttons, False, False)

        self.profiles_sw.set_size_request(400,170)
        self.profiles_sw.add(self.profiles_tv) 


    def get_selected_profile(self):
        """
        Returns the string with name of selected profile 
        """
        try:
            treeselection = self.profiles_tv.get_selection()
            (model,iter) = treeselection.get_selected()	
            return model.get_value(iter,0)
        except:
            return None

    def change_nmap_command(self,widget_tv):
        """
        Change a nmap command at command entry
        """
        assert widget_tv is not None
        # it call __init__ because when wizard or profile are open,  
        # need update profiles
        self.profiles.__init__()
        # update text entry of command
        self.command_entry.set_text(self.profiles.get_command(
            self.get_selected_profile()))	

    def new_wiz(self,widget):
        w = Wizard()
        w.set_notebook(None)
        w.set_profilemanager(self.model)
        w.show_all()

    def open_peditor(self, widget):
        """
        Open Profile Editor with a Selected or Non-Selected(New) Item
        """
        assert widget is not None

        if widget.get_label() == "gtk-edit":
            # Edit profile selected    
            if self.get_selected_profile() is not None:
                pe = ProfileEditor(self.get_selected_profile())
                pe.set_notebook(self.__scan_notebook)
                pe.set_profilemanager(self.model)
                pe.show_all()
        else:
            # New Profile
            pe = ProfileEditor()
            pe.set_notebook(self.__scan_notebook)
            pe.set_profilemanager(self.model)
            pe.show_all()
            self._reload_profile_list()

    def copy_profiles(self, widget):
        """
        Copy selected Profile
        """
        if self.get_selected_profile() is None:
            return None
        d = ProfileName(_("Insert a profile name"))
        profile_name = d.run()
        if profile_name is None or profile_name=="":
            return None
        #get commands of selected profile
        profile_selected = self.get_selected_profile()
        command = self.profiles.get_command(profile_selected)
        hint = self.profiles.get_hint(profile_selected)
        description = self.profiles.get_description(profile_selected)
        annotation = self.profiles.get_annotation(profile_selected)
        #Options
        prof = self.profiles.get_profile(profile_selected)
        options_used = prof['options']
        options = CommandConstructor(options_used)

        self.profiles.add_profile(profile_name,\
                                  command=command,\
                                  hint=hint,\
                                  description=description,\
                                  annotation=annotation,\
                                  options=options.get_options())



        myiter = self.model.insert_before(None, None)
        self.model.set_value(myiter, 0, profile_name)
        self.model.set_value(myiter,1, self.profiles.get_hint(profile_name))
        treeselection = self.profiles_tv.get_selection()
        treeselection.select_iter(myiter)
        #(model,iter) = treeselection.get_selected()	
        #model.get_value(iter,0)


    def delete_profile(self, widget=None):
        """
        delete profile 
        """
        if self.get_selected_profile() is None:
            return None
        self.profiles.remove_profile(self.get_selected_profile())
        #Update treeview
        treeselection = self.profiles_tv.get_selection()
        (model,iter) = treeselection.get_selected()
        model.remove(iter)
        # update text entry of command
        self.command_entry.set_text('')	



    def _reload_profile_list(self):
        """
        Reload a list of profiles
        """
        profiles = self.profiles.sections()
        profiles.sort()
        self.model.clear()


        for command in profiles:
            myiter = self.model.insert_before(None, None)
            self.model.set_value(myiter, 0, command)
            self.model.set_value(myiter,1, self.profiles.get_hint(command))
            #self.model.append([command,self.profiles.get_hint(command)])

    def set_notebook(self, notebook):
        self.__scan_notebook = notebook
    def quit(self, widget):
        self.destroy()


class ProfileName(HIGDialog):
    def __init__(self, text):
        HIGDialog.__init__(self, _('Profile\'s Name'))

        dialog_label = HIGDialogLabel(text)
        dialog_label.show()
        self.vbox.pack_start(dialog_label)
        self.entry_text = HIGTextEntry()
        self.entry_text.show()
        self.vbox.pack_start(self.entry_text)
        self.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        self.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)

    def run(self):
        """
        Returns text of entry
        and None if someone clicked Cancel.
        """
        text = None
        response = HIGDialog.run(self)
        text = self.entry_text.get_text()
        if response==gtk.RESPONSE_CANCEL:
            text = None
        self.destroy()
        return text




class ProfileChosse(HIGHBox):
    def __init__(self):
        HIGHBox.__init__(self)        
        self._create_profile()

    #def _create_profile(self):
    def __init__(self):
        HIGHBox.__init__(self)

        self._create_profile()

        self.change_button = gtk.Button(_("Change"))

        self._pack_noexpand_nofill(self.profile_label)
        self._pack_expand_fill(self.profile_entry)

        self._pack_noexpand_nofill(self.change_button)

        self.profile_entry.set_focus_child(self.profile_entry.child)

        # Events
        self.profile_entry.child.connect('activate',
                                         lambda x: self.change_button.clicked())

    def _create_profile(self):
        self.profile_label = HIGEntryLabel(_('Profile:'))
        self.profile_entry = ProfileCombo()
        self.update()
    def update(self):
        self.update_profile()
    def update_profile(self):
        self.profile_entry.update()




if __name__=="__main__":
    pm = ProfileManager()
    pm.show_all()
    gtk.main()

