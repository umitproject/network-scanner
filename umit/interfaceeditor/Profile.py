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


import gtk 

import sys
from os.path import split, join

from umit.core.Paths import Path
options = Path.options
profile_editor = Path.profile_editor


from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel

from umit.core.NmapCommand import CommandConstructor
from umit.core.UmitConf import Profile, CommandProfile
from umit.gui.OptionBuilder import *
from higwidgets.higboxes import HIGVBox
from umit.core.UmitLogging import log
from umit.core.I18N import _
from higwidgets.higtables import HIGTable
import gobject

from umit.interfaceeditor.selectborder.WrapperWidgets import NotebookLabel, SpecialHBox

from umit.interfaceeditor.ProfileCore import ProfileCore, ProfileOption
from umit.interfaceeditor.Command import Command, TwiceCommand, command_manager
from umit.interfaceeditor.Tools import ToolBarInterface

from umit.interfaceeditor.PageNotebook import *

#TODO :
'''
The list and dictionarie with the widgets of NotebookEditable with numbers
of the pages should be a class to manage better the pages
'''


class CommandAddRemoveLabel(TwiceCommand, Command):
    ''' 
    Add or Remove Label from Title pages of NotebookEditable 
    ###
    trik : state is a inicial value if it is remove or add.
    '''
    def __init__(self, widget, text,profilecore,  state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Add Label'))
        self._widget = widget
        self._text = text 
        self._profilecore = profilecore
        self._new = False 


    def _add_label(self):
        if self._widget.is_voidplace():
            self._widget.unload_voidplace()
        self._widget.set_text(self._text) 

        #ProfileCore

        elem = self._profilecore.search_in_groups(self._widget.get_name())
        if elem == None and not self._new: 
            self._new = True
            #XXX lack profilecore add
            #self._profilecore.add_section(self._text)
            self._widget.set_name(self._text)


        log.debug('Adding label')
    _execute_1 = _add_label
    def _remove_label(self):

        self._widget.voidplace()

        #ProfileCore
        if self._new : 
            pass



        log.debug('Removing label, Adding Void Place')
    _execute_2 = _remove_label



class CommandMovePage(TwiceCommand, Command):
    '''
    move page
    '''
    def __init__(self, notebook, number,profilecore, state):
        '''
        @param number: number of num pages to move ; default should be 1
        @type number: Integer
        '''

        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Move Page'))
        self._notebook = notebook
        self._page = self._notebook.get_nth_page(self._notebook.get_current_page())
        self._number = number
        self._profilecore = profilecore
    def _move_left(self):
        log.debug("move left")
        current = self._notebook.get_current_page()
        self._notebook.reorder_child(self._page,current-self._number )
        name = self._page.get_name()
        if name != None :
            self._profilecore.move_section_left(name)

        #Ajust sections childs (NotebookLabel)

        dic = self._notebook.sections_widgets
        list = self._notebook.sections_widgets_list

        list_tmp = []
        for i in range(len(list)):
            widget = list.pop()
            list_tmp.append(widget)
            if widget.get_name()==name :
                break 
        w_tmp = list.pop()
        w_tmp2 = list_tmp.pop()
        num = dic[w_tmp] 
        dic[w_tmp] = dic[w_tmp2]
        dic[w_tmp2] = num
        list.append(w_tmp2)
        list.append(w_tmp)
        for i in range(len(list_tmp)):
            list.append(list_tmp.pop())

    _execute_1 = _move_left
    def _move_right(self):
        log.debug("move right")
        current = self._notebook.get_current_page()
        self._notebook.reorder_child(self._page,current+self._number )
        name = self._page.get_name()
        if name != None :
            self._profilecore.move_section_right(name)

        #Ajust sections childs (NotebookLabel)

        dic = self._notebook.sections_widgets
        list = self._notebook.sections_widgets_list

        list_tmp = []
        for i in range(len(list)):
            widget = list.pop()
            list_tmp.append(widget)
            if widget.get_name()==name :
                break 
        w_tmp = list_tmp.pop()
        w_tmp2 = list_tmp.pop()
        num = dic[w_tmp] 
        dic[w_tmp] = dic[w_tmp2]
        dic[w_tmp2] = num
        list.append(w_tmp2)
        list.append(w_tmp)
        for i in range(len(list_tmp)):
            list.append(list_tmp.pop())
    _execute_2 = _move_right



class NotebookEditable(HIGNotebook):
    '''
    Editable Notebook to Edit Profile Editor
    '''
    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                     (gobject.TYPE_STRING,object)),
        'need-save': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                      (gobject.TYPE_STRING,object)),
    }
    def __init__(self, listoption, profilecore):
        self._listoption = listoption
        HIGNotebook.__init__(self)
        self._inc = 0
        self.sections_widgets = {}
        self.sections_widgets_list = []
        self.connect('key-press-event', self.on_key_press)
        self.connect_after('switch-page', self.on_switch_page)
        self._old_select = None 
        self._profilecore = profilecore

        self._page_in = 0



    def save(self):
        self._profilecore.write_file(profile_editor)
    def reset(self):
        pass

    def load_data(self):
        self.profile = CommandProfile()
        options_used = {}

        self.constructor = CommandConstructor(options_used)
        self.options = self._profilecore
        i = 0
        for tab in self.options.groups:
            self.create_tab(tab, self.options.section_names[tab], 
                            self.options.tabs[tab], i)
            i = i+1 
    def create_label(self, name):
        label = NotebookLabel(name)
        label.set_name(name)
        label.set_flags( label.flags() |  gtk.CAN_FOCUS) 
        label.connect('key-press-event', self.on_key_press)
        label.connect('button-press-event', self.on_button_press)  


        label.connect('drag_data_received', self.label_drag_data_received)
        label.drag_dest_set(gtk.DEST_DEFAULT_ALL, target[:-1],
                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

        return label
    def create_tab(self, tab_name, section_name, tab, number):
        box = BoxEditable(tab_name, self.options, self._listoption, self)
        box.set_profile_core(self._profilecore)
        label = NotebookLabel(tab_name)
        label.set_name(tab_name)
        #eventbox = gtk.EventBox()

        #eventbox.add(label)
        label.set_flags( label.flags() |  gtk.CAN_FOCUS) 
        label.connect('key-press-event', self.on_key_press)
        label.connect('button-press-event', self.on_button_press)  


        label.connect('drag_data_received', self.label_drag_data_received)
        label.drag_dest_set(gtk.DEST_DEFAULT_ALL, target[:-1],
                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        #eventbox.show_all()
        label.show_all()
        self.sections_widgets[label] = number
        self.sections_widgets_list.append(label)
        box._fill_table()
        self.append_page(box, label)
        #self.set_tab_reorderable(label, True)

    def select(self, value):
        if self._old_select!=None:
            self._old_select.set_select(value)
            self._old_select=None

    def get_new_name(self):
        self._inc = self._inc +1 
        return str('New_section_%s' % self._inc )
    def get_page_name(self, name):
        result = None 
        for i in self.sections_widgets_list:
            if i.get_name() == name : 
                result = self.sections_widgets[i] 
                break 
        if result==None:
            return 
        return self.get_nth_page(result)

    def on_button_press(self, widget, event):
        log.debug('Button press on Notebook')
        if self._old_select != None:
            self._old_select.set_select(False)
        widget.set_select(True)
        self._old_select = widget
        widget.do_draw()
        self.set_current_page(self.sections_widgets[widget])
        #XXX - this focus owns drag-n-drop received :( 
        #widget.grab_focus()
        self._page_in = self.get_current_page()
        log.debug('<<< Setting page %s'%self._page_in)
        return True
    def put_on_page(self):
        log.debug('<<< Put on page %s'%self._page_in)
        self.set_current_page(self._page_in)
    def on_switch_page(self, widget, event, page):
        self.grab_focus()
        self.emit('changed','Sections', page)
    def delete_section(self):
        if self._old_select.is_voidplace():

            log.debug('Key press event on NotebookEditable \
                      -- unload voidplace')
            #self._old_select.unload_voidplace()
            #label_tmp =self.get_tab_label(self.get_nth_page(
                #self.get_current_page()))
            #num = self.sections_widgets[label_tmp]
            #del self.sections_widgets[label_tmp]
            #for i in range(num, len(self.sections_widgets)):
                #print i
                #widget_tmp = self.sections_widgets_list[i+1]
                #self.sections_widgets[widget_tmp] = self.sections_widgets[widget_tmp] - 1 

            #self.sections_widgets_list.pop(num)
            #self.remove_page(self.get_current_page())
            num = self.get_current_page()
            cmd = CommandPageNotebook(self,
                                      self.get_nth_page(num),num, 
                                      self._profilecore,
                                      False)
            command_manager.add_command(cmd)

            self._old_select=None
        else: 
            log.debug('Key press event on NotebookEditable -- \
                      CommandAddRemoveLabel')
            cmd = CommandAddRemoveLabel(self._old_select, 
                                        self._old_select.get_text(), self._profilecore,False)
            command_manager.add_command(cmd)
        self.emit('need-save', 'Sections', None)
    def on_key_press(self, widget, event):
        _keyval = gtk.gdk.keyval_name(event.keyval)
        log.debug('Key press event on NotebookEditable')
        if self._old_select==None:
            log.debug('Key press event on NotebookEditable -- Return')
            return

        if _keyval == "Delete" :
            self.delete_section()

        #else: 
            #self._old_select.unload_voidplace()
    def label_drag_data_received(self, w, context, x, y, data, info, time):

        if data and data.format == 8:
            context.finish(True, False, time)
            cmd = CommandAddRemoveLabel(self._old_select, self._old_select.get_name(), self._profilecore, True)
            command_manager.add_command(cmd)
            self.emit('need-save', 'Sections', None)

        #else:
        #    context.finish(False, False, time)

    def can_move_right(self):
        n = self.get_n_pages()
        current = self.get_current_page()
        return (n-1) != (current)
    def can_move_left(self):	
        current = self.get_current_page()
        return current!= 0
    def move_right(self):
        cmd = CommandMovePage(self, 1, self._profilecore, False)
        command_manager.add_command(cmd)
        self.emit('changed','Sections', None)
        self.emit('need-save', 'Sections', None)
    def move_left(self):
        cmd = CommandMovePage(self, 1, self._profilecore, True)
        command_manager.add_command(cmd)
        self.emit('changed','Sections', None)
        self.emit('need-save', 'Sections', None)



class ProfileEdit(gtk.HBox):

    def __init__(self, listoption, profile_editor_file=profile_editor):
        gtk.HBox.__init__(self)
        self._toolbar = ToolBarInterface()
        self._toolbar.set_optionlist(listoption)
        self.profile_editor_file = profile_editor_file
        self._proprieties = None 
        self._notebook_tools = None 
        self._changed = False
        #MAIN SCROLLED
        self._scroolledmain = HIGScrolledWindow()
        #NOTEBOOKEDITABLE :
        self._profilecore = ProfileCore(profile_editor_file)
        self._toolbar.set_profilecore(self._profilecore)

        self.notebook = NotebookEditable(listoption, self._profilecore)
        self._toolbar.set_notebook(self.notebook)
        self.notebook.connect_after('changed', self.update_toolbar)
        self.notebook.connect_after('need-save',self._need_save)
        self.notebook.load_data()
        self.pack_start(self._toolbar.get_toolbar(), False, True,0)
        self.pack_start(self._scroolledmain, True, True)
        self._scroolledmain.add_with_viewport(self.notebook)
        self.show_all()
    def _need_save(self, action, others, page):
        self._changed = True
    def get_profilecore(self):
        return self._profilecore
    def set_notebook(self, notebook):
        self._notebook_tools = notebook
    def set_proprieties(self, proprieties):
        self._proprieties = proprieties
        proprieties.disable_all()
    def is_changed(self):
        return self._changed
    def update_toolbar(self, action, others, page):
        #print action
        #print others
        #print page
        boxeditable = self.get_box_editable()
        self._toolbar.set_box_editable(boxeditable)
        self._toolbar.update_toolbar()

        #Update Proprieties box
        if self._notebook_tools != None: 
            self._notebook_tools.set_current_page(2)

        if boxeditable._old_selected!= None :
            #SpecialHBox - Item
            self._proprieties.set_boxeditable(boxeditable)
            self._proprieties.set_item(boxeditable._old_selected)

            log.debug('<<< SpecialHBox Item update')
        elif self.notebook._old_select!= None:
            #Notebook_Label
            self._proprieties.set_notebooklabel(self.notebook._old_select)
            self._proprieties.set_boxeditable(boxeditable)
            log.debug('<<< NotebookLabel update')

    def get_box_editable(self):
        current_page = self.notebook.get_current_page()
        current_box = self.notebook.get_nth_page(current_page)
        return current_box

    def save(self):
        self._profilecore.write_file(self.profile_editor_file)
        log.debug('<<< Saving to file %s ' % self.profile_editor_file)

    def create_events(self):
        #....
        pass

