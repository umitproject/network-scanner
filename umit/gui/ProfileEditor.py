#!/usr/bin/env python
# Copyright (C) 2005 Insecure.Com LLC.
# Authors: 
#  Adriano Monteiro Marques <py.adriano@gmail.com>
#  Luis Antonio Bastiao Silva <luis.kop@gmail.com>
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

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higboxes import HIGSpacer, hig_box_space_holder
from higwidgets.higexpanders import HIGExpander
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog, HIGDialog

from umit.gui.OptionBuilder import *
from umit.gui.Help import show_help

from umit.core.ProfileEditorConf import profile_editor_file
from umit.core.NmapCommand import CommandConstructor
from umit.core.UmitConf import Profile, CommandProfile
from umit.core.UmitLogging import log
from umit.core.I18N import _


class ProfileEditor(HIGWindow):

    def __init__(self, profile_name=None, delete=False):
        HIGWindow.__init__(self)
        self.set_title(_('Profile Editor'))
        self.set_position(gtk.WIN_POS_CENTER)
        self.profile_name=profile_name
        self.__create_widgets()
        self.__pack_widgets()

        self.scan_notebook = None
        self.profilemanager = None

        self.profile = CommandProfile()

        self.deleted = False
        options_used = {}

        if profile_name:
            log.debug("Showing profile %s" % profile_name)
            prof = self.profile.get_profile(profile_name)
            options_used = prof['options']

            # Interface settings
            self.profile_name_entry.set_text(profile_name)
            self.profile_hint_entry.set_text(prof['hint'])
            self.profile_description_text.get_buffer().set_text(prof['description'])
            self.profile_annotation_text.get_buffer().set_text(prof['annotation'])

            if delete:
                # Removing profile. It must be saved again
                self.remove_profile()

        self.constructor = CommandConstructor(options_used)
        self.options = OptionBuilder(profile_editor_file, self.constructor, self.update_command)
        log.debug("Option groups: %s" % str(self.options.groups))
        log.debug("Option section names: %s" % str(self.options.section_names))
        #log.debug("Option tabs: %s" % str(self.options.tabs))

        for tab in self.options.groups:
            self.__create_tab(tab, self.options.section_names[tab], self.options.tabs[tab])

        self.update_command()

    def update_command(self):
        """Regenerate command with target '<target>' and set the value for the command entry"""
        self.command_entry.set_text(self.constructor.get_command('<target>'))

    def help(self, widget):
        """
        Show help documentation of Profile Editor
        """
        show_help(self,"profile_editor.html#introduction")

    def __create_widgets(self):
        self.main_vbox = HIGVBox()



        self.command_expander = HIGExpander('<b>'+_('Command')+'</b>')
        self.command_expander.set_expanded(True)
        self.command_entry = gtk.Entry()

        self.notebook = gtk.Notebook()

        # Profile info page
        self.profile_info_vbox = HIGVBox()
        self.profile_info_label = HIGSectionLabel(_('Profile Information'))
        self.profile_name_label = HIGEntryLabel(_('Profile name'))
        self.profile_name_entry = gtk.Entry()
        self.profile_hint_label = HIGEntryLabel(_('Hint'))
        self.profile_hint_entry = gtk.Entry()
        self.profile_description_label = HIGEntryLabel(_('Description'))
        #self.profile_description_label = HIGHBox() 
        self.profile_description_scroll = HIGScrolledWindow()
        self.profile_description_text = HIGTextView()
        self.profile_annotation_label = HIGEntryLabel(_('Annotation'))
        #self.profile_annotation_label = HIGHBox() 
        self.profile_annotation_scroll = HIGScrolledWindow()
        self.profile_annotation_text = HIGTextView()

        # Buttons
        self.buttons_hbox = HIGHBox()

        self.help_button = HIGButton(stock=gtk.STOCK_HELP)
        self.help_button.connect('clicked', self.help)

        #self.delete_button = HIGButton(stock=gtk.STOCK_DELETE)
        #self.delete_button.connect('clicked', self.delete_profile)

        self.cancel_button = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel_button.connect('clicked', self.quit_without_saving)

        self.ok_button = HIGButton(stock=gtk.STOCK_OK)
        self.ok_button.connect('clicked', self.save_profile)

    def __pack_widgets(self):
        self.add(self.main_vbox)

        # Packing widgets to main_vbox

        self.main_vbox._pack_noexpand_nofill(self.command_expander)
        self.main_vbox._pack_expand_fill(self.notebook)
        self.main_vbox._pack_noexpand_nofill(self.buttons_hbox)

        # Packing command_entry on command_expander
        self.command_expander.hbox.pack_start(self.command_entry)

        # Packing profile information tab on notebook
        self.notebook.append_page(self.profile_info_vbox, gtk.Label(_('Profile')))
        self.profile_info_vbox.set_border_width(5)
        table = HIGTable()
        self.profile_info_vbox._pack_noexpand_nofill(self.profile_info_label)
        self.profile_info_vbox._pack_noexpand_nofill(HIGSpacer(table))

        self.profile_annotation_scroll.add(self.profile_annotation_text)
        self.profile_description_scroll.add(self.profile_description_text)

        vbox_desc = HIGVBox()
        vbox_desc._pack_noexpand_nofill(self.profile_description_label)
        vbox_desc._pack_expand_fill(hig_box_space_holder())

        vbox_ann = HIGVBox()
        vbox_ann._pack_noexpand_nofill(self.profile_annotation_label)
        vbox_ann._pack_expand_fill(hig_box_space_holder())
        table.attach(self.profile_name_label,0,1,0,1)
        table.attach(self.profile_name_entry,1,2,0,1)
        #table.attach(self.profile_hint_label,0,1,1,2,xoptions=0)
        table.attach(self.profile_hint_label,0,1,1,2)
        table.attach(self.profile_hint_entry,1,2,1,2)
        table.attach(vbox_desc,0,1,2,3)
        table.attach(self.profile_description_scroll,1,2,2,3)
        table.attach(vbox_ann,0,1,3,4)
        table.attach(self.profile_annotation_scroll,1,2,3,4)

        # Packing buttons on button_hbox
        self.buttons_hbox.pack_start(self.help_button)
        #self.buttons_hbox.pack_start(self.delete_button)
        self.buttons_hbox.pack_start(self.cancel_button)
        self.buttons_hbox.pack_start(self.ok_button)

        self.buttons_hbox.set_border_width(5)
        self.buttons_hbox.set_spacing(6)

    def __create_tab(self, tab_name, section_name, tab):
        log.debug(">>> Tab name: %s" % tab_name)
        log.debug(">>>Creating profile editor section: %s" % section_name)

        vbox = HIGVBox()
        table = HIGTable()
        section = HIGSectionLabel(section_name)

        vbox._pack_noexpand_nofill(section)
        vbox._pack_noexpand_nofill(HIGSpacer(table))
        vbox.set_border_width(6)

        tab.fill_table(table, True)
        self.scrollwindow = HIGScrolledWindow()
        self.scrollwindow.set_size_request(600,300)
        vp = gtk.Viewport()
        vp.add(vbox)
        vp.set_shadow_type(gtk.SHADOW_NONE)
        self.scrollwindow.add(vp)

        vbox_tmp = HIGVBox()
        vbox_tmp.set_border_width(6)
        vbox_tmp.set_spacing(12)
        vbox_tmp.pack_start(self.scrollwindow)


        self.notebook.append_page(vbox_tmp, gtk.Label(tab_name))
    def set_profilemanager(self, model):
        """
        give a model of treeview to update profile manager
        after run wizard
        """
        assert model != None

        self.model = model 
        self.profilemanager = True 

    def update_profilemanager(self):
        """
        Update treeview of ProfileManager"
        """
        assert self.profilemanager;

        profiles = self.profile.sections()
        profiles.sort()
        self.model.clear()


        for command in profiles:
            myiter = self.model.insert_before(None, None)
            self.model.set_value(myiter, 0, command)
            self.model.set_value(myiter,1, self.profile.get_hint(command))


    def save_profile(self, widget):
        profile_name = self.profile_name_entry.get_text()
        if profile_name == '':
            alert = HIGAlertDialog(message_format=_('Unnamed profile'),\
                                   secondary_text=_('You must provide a name \
for this profile.'))
            alert.run()
            alert.destroy()

            self.notebook.set_current_page(0)
            self.profile_name_entry.grab_focus()

            return None

        if not self.deleted:
            self.remove_profile()

        command = self.constructor.get_command('%s')
        hint = self.profile_hint_entry.get_text()

        buf = self.profile_description_text.get_buffer()
        description = buf.get_text(buf.get_start_iter(),\
                                   buf.get_end_iter())

        buf = self.profile_annotation_text.get_buffer()
        annotation = buf.get_text(buf.get_start_iter(),\
                                  buf.get_end_iter())
        self.profile.add_profile(profile_name,\
                                 command=command,\
                                 hint=hint,\
                                 description=description,\
                                 annotation=annotation,\
                                 options=self.constructor.get_options())
        self.deleted = False
        if self.profilemanager:
            self.update_profilemanager()

        self.quit()


    def clean_profile_info(self):
        self.profile_name_entry.set_text('')
        self.profile_hint_entry.set_text('')
        self.profile_description_text.get_buffer().set_text('')
        self.profile_annotation_text.get_buffer().set_text('')

    def set_notebook(self, notebook):
        self.scan_notebook = notebook

    def quit(self, widget=None, extra=None):
        if self.deleted:
            dialog = HIGDialog(buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            alert = HIGEntryLabel('<b>'+_("Deleting Profile")+'</b>')
            text = HIGEntryLabel(_('Your profile is going to be deleted! Click\
                                   Ok to continue, or Cancel to go back to Profile Editor.'))
            hbox = HIGHBox()
            hbox.set_border_width(5)
            hbox.set_spacing(12)

            vbox = HIGVBox()
            vbox.set_border_width(5)
            vbox.set_spacing(12)

            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)

            vbox.pack_start(alert)
            vbox.pack_start(text)
            hbox.pack_start(image)
            hbox.pack_start(vbox)

            dialog.vbox.pack_start(hbox)
            dialog.vbox.show_all()

            response = dialog.run()
            dialog.destroy()

            if response == gtk.RESPONSE_CANCEL:
                return None
        self.destroy()       
        if self.scan_notebook != None:

            for i in xrange(self.scan_notebook.get_n_pages()):
                page = self.scan_notebook.get_nth_page(i)
                page.toolbar.profile_entry.update()

        #page.toolbar.scan_profile.profile_entry.child.\
        #    set_text(self.profile_name_entry.get_text())
    def quit_without_saving(self, widget=None):
        self.deleted=False
        self.quit()

    def on_delete(self, widget=None):
        if not self.profile_name:
            return self.on_cancel()

        dialog = HIGDialog(buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                                    gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
        alert = HIGEntryLabel('<b>'+_("Deleting Profile")+'</b>')
        text = HIGEntryLabel(_('Your profile is going to be deleted! Click \
Ok to continue, or Cancel to go back to Profile Editor.'))
        hbox = HIGHBox()
        hbox.set_border_width(5)
        hbox.set_spacing(12)

        vbox = HIGVBox()
        vbox.set_border_width(5)
        vbox.set_spacing(12)

        image = gtk.Image()
        image.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)

        vbox.pack_start(alert)
        vbox.pack_start(text)
        hbox.pack_start(image)
        hbox.pack_start(vbox)

        dialog.vbox.pack_start(hbox)
        dialog.vbox.show_all()

        response = dialog.run()
        dialog.destroy()

        if response == gtk.RESPONSE_CANCEL:
            return None

        self.deleted = True
        self.profile.remove_profile(self.profile_name)
        self.on_cancel()


    def on_cancel(self, widget=None):
        self.destroy()
        self.update_profile_entry()

    def update_profile_entry(self):
        page = None
        for i in xrange(self.scan_notebook.get_n_pages()):
            page = self.scan_notebook.get_nth_page(i)

            page.toolbar.profile_entry.update(\
                self.profile_name_entry.get_text())

            list = page.toolbar.profile_entry.get_model()
            length = len(list)
            if self.deleted and length > 0 :
                page.toolbar.profile_entry.set_active(0)
            elif self.deleted and length == 0:
                page.toolbar.profile_entry.child.set_text("")

        if page is not None:
            page.toolbar.profile_entry.update()



    def remove_profile(self,profile_name=None):
        '''
        Remove current profile 
        '''
        if not profile_name:
            profile_name = self.profile_name
        self.profile.remove_profile(profile_name)
        self.deleted = True        

    def delete_profile(self, widget=None):
        """
        delete profile
        """
        self.remove_profile()
        self.deleted=False        
        self.quit()



if __name__ == '__main__':
    p = ProfileEditor()
    p.show_all()

    gtk.main()

