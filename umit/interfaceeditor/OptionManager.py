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
import os

from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higscrollers import HIGScrolledWindow 
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higbuttons import HIGButton
from higwidgets.higdialogs import HIGDialog, HIGAlertDialog
from umit.core.UmitLogging import log
from umit.core.I18N import _
## Testing at devel 
from os.path import split, join

from umit.core.Paths import Path
#Path.set_umit_conf(join(split(__file__)[0], 'config', 'umit.conf'))
##END DEV TEST
options = Path.options
pixmaps_dir = Path.pixmaps_dir

import gobject
from umit.interfaceeditor.ProfileCore import ProfileOption
from umit.gui.OptionBuilder import OptionBuilder
from umit.core.NmapOptions import  NmapOptions
from umit.interfaceeditor.OptionsCore import ListOptions, Option, ARG_TYPES

from umit.interfaceeditor.Command import Command, TwiceCommand, CommandContainer, command_manager
from umit.interfaceeditor.RestructFiles import RestructFiles
from umit.interfaceeditor.DependencesOption import DependenceOption

from umit.interfaceeditor.PageNotebook import CommandAddRemoveOption, CommandAddRemoveVoidplace

'''
Contains a Display, and the List of Options 
to use in the GUI UIE
It's a sub-file of UIE
'''

class CommandAddRemoveOptionMode(TwiceCommand, Command):
    def __init__(self, option, optioncore,modeltreeview,optiondisplay, state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, 'Add / Remove a Option')
        self._option = option
        self.options = optioncore
        self.__model = modeltreeview
        self.optionlist = optiondisplay.optionlist
        self.optiondisplay = optiondisplay


    def _add_option(self):
        option = self._option 
        opt = option.get_option_dic()
        self.options.add_option_from_dic(opt)

        myiter = self.__model.insert_before(None, None)
        arg = option.get_arg_type()
        icon = gtk.Image()
        s = self.optionlist._arg_img(arg)
        img_dir =  os.path.join(pixmaps_dir, 'uie', '%s.png' % s)
        icon.set_from_file(img_dir)
        icon = icon.get_pixbuf()
        self.__model.set_value(myiter, 0, icon)
        self.__model.set_value(myiter, 1, option.get_name())
        self.options.reload_opt()

    _execute_1 = _add_option
    def _remove_option(self):
        name = self._option.get_name()

        self.options.remove_option(name)

        #Update treeview
        m =  self.optionlist.get_model()
        iter = m.get_iter_first()
        result = None 
        while True:
            if iter==None:
                break
            if m.get_value(iter,1) == name:
                result = iter
                break
            iter = m.iter_next(iter)


        #(model,iter) = self.optionlist.get_selected_option()
        if result==None:
            log.debug('Something happen!! ERROR')
            return
        m.remove(iter)	
        self.optiondisplay.clear()

    _execute_2 = _remove_option



class OptionDisplay(HIGTable):
    def __init__(self, option=None):
        HIGTable.__init__(self)
        self.create_and_attach_widgets()
        self.set_border_width(5)
        self.arg_type=None

    def create_and_attach_widgets(self):
        self.option_label = HIGSectionLabel('New Option')
        self.attach(self.option_label, 0, 3, 0, 1)

        self.name_label = HIGEntryLabel(_('Name:'))
        self.name_entry = HIGTextEntry()
        self.attach(self.name_label, 0,1,1,2)
        self.attach(self.name_entry, 1,3,1,2)

        self.hint_label = HIGEntryLabel(_('Hint:'))
        self.hint_entry = HIGTextEntry()
        self.attach(self.hint_label, 0,1,2,3)
        self.attach(self.hint_entry,1,3,2,3)

        self.need_root = gtk.CheckButton(_('Need root'))
        self.attach(self.need_root, 0,1,3,4)	



        self.options_label = HIGEntryLabel(_('Options:'))
        hbox = HIGHBox()
        self.options_entry = HIGTextEntry()
        self.insert_arg_button = HIGButton(title='Args', stock='gtk-add')
        self.insert_arg_button.connect('clicked', self.update_args)
        self.attach(self.options_label,0,1,4,5)
        self.attach(self.options_entry, 1,2,4,5)
        self.attach(self.insert_arg_button, 2,3, 4, 5)

        self.aguments_label = HIGEntryLabel(_('Arguments:'))
        self.arguments_entry = HIGTextEntry()
        self.arguments_entry.set_editable(False)
        self.attach(self.aguments_label, 0,1, 5,6)
        self.attach(self.arguments_entry, 1,3,5,6)	


    def update_args(self, widget):
        '''
        Update aguments entry and option entry
        '''

        cursor_index = self.options_entry.get_position()
        text_entry = self.options_entry.get_text()
        arg_description, arg_key = self.dialog_args()
        if arg_key != None :
            #Update arguments

            self.arg_type = arg_key
            if text_entry.find('%s') == -1: 
                left = text_entry[0:cursor_index]
                right = text_entry[cursor_index:len(text_entry)]
                final = left + "%s" + right
                self.options_entry.set_text(final)
            self.arguments_entry.set_text(arg_description)	


    def dialog_args(self):
        '''
        Create a dialog
        '''

        d = HIGDialog(_('Arguments'))
        description_label = HIGEntryLabel(
            _('Insert the description to argument:'))
        description_label.show()
        description_entry = HIGTextEntry()
        text = self.arguments_entry.get_text()
        description_entry.set_text(text)
        description_entry.show()

        combo_box = gtk.combo_box_new_text()
        combo_box.set_wrap_width(1)
        index = -1 
        j = 0 
        for i in ARG_TYPES:
            combo_box.append_text(ARG_TYPES[i])
            if i == self.arg_type:
                index = j 
            j = j + 1
        if index > -1 : 
            combo_box.set_active(index)
        combo_box.show()
        d.vbox.pack_start(description_label, False, False)
        d.vbox.pack_start(description_entry, False, False)
        d.vbox.pack_start(combo_box, False, False)
        d.add_button(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL)
        d.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        resp = d.run()
        result  = None, None 
        if resp == gtk.RESPONSE_OK:
            model = combo_box.get_model()
            active = combo_box.get_active()
            if active < 0:
                return None, None 
            combo_selected =  model[active][0]

            for i in ARG_TYPES:
                if combo_selected == ARG_TYPES[i]:
                    combo_selected = i

            result = description_entry.get_text(), combo_selected
            #self.insert_arg_button.set_label('Edit args')
            #self.insert_arg_button.
        d.destroy()
        return result 

    def clear(self):
        """ 
        Clear Option Display
        """
        self.option_label.set_new_text('New Option')
        self.name_entry.set_text('')
        self.hint_entry.set_text('')
        self.arguments_entry.set_text('')
        self.need_root.set_active(False)
        self.options_entry.set_text('')


    def set_option_list(self, list):
        """
        set option list from a dictionarie 

        @param list: Elements of a option
        @type list: Dictionarie with elements
        """
        self.clear()
        self.option_label.set_new_text(list['name'])
        self.name_entry.set_text(list['name'])
        self.hint_entry.set_text(list['hint'])

        for i in list['arguments']:
            i = self.arguments_entry.get_text() + i
            self.arguments_entry.set_text(i)

        self.options_entry.set_text(list['option'])
        self.need_root.set_active(list['need_root'])
        self.arg_type = list['arg_type']


    def set_option(self,name, hint,
                   arguments, need_root, 
                   options, arg_type):        
        """
        fill fields
        buggy arguments.
        """
        self.clear()
        self.options_entry.set_label(name)
        self.name_entry.set_text(name)
        self.hint_entry.set_text(hint)
        self.arguments_entry.set_text(arguments)
        self.need_root.set_active(need_root)
        self.arg_type = arg_type

class OptionDisplayMainFrame(OptionDisplay):
    __gsignals__ = {
        'need-save': (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, 
                      (gobject.TYPE_STRING,object)),
    }
    def __init__(self, option=None):
        OptionDisplay.__init__(self)
        #Profile and Wizard core
        self._profilecore = None 
        self._wizardcore = None 
        self._notebook= None
        self._profile = None 
        self._wizard = None 
        self._changed = False

        hbox = HIGHBox()
        hbox.set_border_width(12)
        self.delete_button = HIGButton(stock='gtk-delete')
        self.delete_button.connect('clicked', self.delete_option)
        self.new_button = HIGButton(stock='gtk-new')
        self.new_button.connect('clicked', self.new_option)
        self.update_button = HIGButton(stock='gtk-refresh')
        self.update_button.connect('clicked', self.update_option)
        self.add_button = HIGButton(stock='gtk-add')
        self.add_button.connect('clicked', self.add_option)
        hbox.pack_end(self.delete_button,False,False)
        hbox.pack_end(self.update_button, False, False)
        hbox.pack_end(self.add_button, False, False)
        hbox.pack_end(self.new_button, False,False)
        self.attach(hbox, 1,2,6,7)

        self.optionlist = option
    def set_wizard(self, wizard):
        self._wizard = wizard
        self._wizardcore = wizard.get_profilecore()
    def set_profile(self, profile):
        self._profile = profile 
        self._profilecore = profile.get_profilecore()
    def set_options_list(self, options):
        '''
        set a OptionList to manipulate when add remove and edit 
        @param options: Options List 
        @type options: class OptionList
        '''

        self.optionlist = options


    def get_option(self):
        '''
        Get a option filled
        @return: a option 
        @rtype: class Option
        '''

        name = self.name_entry.get_text()
        hint = self.hint_entry.get_text()
        #Args is only to one yet
        arguments = [self.arguments_entry.get_text()]
        need_root = self.need_root.get_active()
        arg_type = self.arg_type
        options = self.options_entry.get_text()
        opt = Option(name, options, hint, arguments, need_root, arg_type)
        return opt


    def delete_option(self, widget):
        """
        Delete option
        @param widget: widget from connect
        @type widget: HIGButton
        """
        name = self.name_entry.get_text()
        if name == '':
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                               message_format=_('Invalid option '), 
                               secondary_text='Fill fields of option')
            d.run()
            d.destroy()
        else:	    
            if self.optionlist.options.exists(name): 
                #Verify if exists 
                self.rf = RestructFiles(self.optionlist.options, 
                                        self._wizardcore,
                                        self._profilecore)
                profile, wizard =  self.rf.get_places(name)
                used = []
                for i in profile:
                    used.append(i)
                for i in wizard:
                    used.append(i)
                if used == []:
                    cmd = CommandAddRemoveOptionMode(self.get_option(),
                                                     self.optionlist.options,
                                                     self.optionlist.get_model(),
                                                     self,
                                                     False)
                    command_manager.add_command(cmd)
                    self.emit('need-save', None, None)
                else:
                    #Show Dialog Dependences etc!!!
                    dep = DependenceOption(name, self.rf, profile, wizard)
                    resp = dep.run()
                    dep.destroy()

                    if resp == gtk.RESPONSE_YES:
                        commands = []
                        for i in profile:
                            boxedit = self._profile.notebook.get_page_name(i[0])
                            widget = boxedit.search_option(i[1])
                            cmd = CommandAddRemoveOption(widget,
                                                         boxedit,
                                                         self._profilecore,
                                                         boxedit, 
                                                         False)

                            cmd2 = CommandAddRemoveVoidplace(boxedit,
                                                             widget,
                                                             boxedit._coords,
                                                             False)
                            commands.append(cmd)
                            commands.append(cmd2)
                            boxedit.send_signal_save()
                        for i in wizard:
                            boxedit = self._wizard.notebook.get_page_name(i[0])
                            widget = boxedit.search_option(i[1])
                            cmd = CommandAddRemoveOption(widget,
                                                         boxedit,
                                                         self._wizardcore,
                                                         boxedit,
                                                         False)

                            cmd2 = CommandAddRemoveVoidplace(boxedit,
                                                             widget,
                                                             boxedit._coords,
                                                             False)
                            commands.append(cmd)
                            commands.append(cmd2)
                            boxedit.send_signal_save()
                        cmd3 = CommandAddRemoveOptionMode(self.get_option(),
                                                          self.optionlist.options,
                                                          self.optionlist.get_model(),
                                                          self,
                                                          False)
                        commands.append(cmd3)
                        cmd = CommandContainer('Remove option and deps',
                                               True,
                                               commands)
                        command_manager.add_command(cmd)
                        self.emit('need-save', None, None)


                    else: 
                        return



                #self.optionlist.options.remove_option(name)

                ##Update treeview
                #(model,iter) = self.optionlist.get_selected_option()
                #model.remove(iter)	
                #self.clear()

            else: 
                d = HIGAlertDialog(type= gtk.MESSAGE_ERROR, 
                                   message_format=_('ERROR'),
                                   secondary_text=_('Option do not exists')
                                   )
                d.run()
                d.destroy()
    def is_changed(self):
        return self._changed

    def do_need_save(self,action, event):
        self._changed = True 
        log.debug('<<< do_need_save')
    def set_notebook(self, notebook):
        self._notebook = notebook

    def update_option(self, widget):
        """
        Update option
        @param widget: widget from connect
        @type widget: HIGButton
        """
        name = self.name_entry.get_text()
        if name == '':
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                               message_format=_('Invalid name option '), 
                               secondary_text='Fill fields of option')
            d.run()
            d.destroy()
        else:	
            if self.optionlist.options.exists(name): 
                opt = self.get_option()
                self.optionlist.options.remove_option(name)
                self.optionlist.add(opt)



    def new_option(self, widget):
        """
        Clean Option Display
        @param widget: widget from connect
        @type widget: HIGButton
        """   
        self.clear()
        self.add_button.set_sensitive(True)
        self.update_button.set_sensitive(False)
        self.delete_button.set_sensitive(False)

    def add_option(self, widget):
        """
        Add option
        @param widget: widget from connect
        @type widget: HIGButton
        """

        if self.name_entry.get_text()=="":
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                               message_format=_('No fields entered'), 
                               secondary_text=_('Blank options is not allowed!'))
            d.run()
            d.destroy()
        else:
            opt = self.get_option()
            self.optionlist.add(opt)
            self.add_button.set_sensitive(False)
            self.emit('need-save', None, None)

TARGET_STRING = 0
TARGET_ROOTWIN = 1

target = [
    ('STRING', 0, TARGET_STRING),
    ('text/plain', 0, TARGET_STRING),
    ('application/x-rootwin-drop', 0, TARGET_ROOTWIN)
]

class OptionList(HIGVBox):
    """
    A treeview with a list of actual options
    """

    def __init__(self, optiondisplay=None):
        HIGVBox.__init__(self)
        self.__model =  gtk.TreeStore(gtk.gdk.Pixbuf,gobject.TYPE_STRING)
        self.__treeview = gtk.TreeView(self.__model)
        self.__treeview.set_headers_visible(True)
        self.__treeview.drag_source_set(gtk.gdk.BUTTON1_MASK | 
                                        gtk.gdk.BUTTON3_MASK,
                                        target, gtk.gdk.ACTION_COPY | 
                                        gtk.gdk.ACTION_MOVE)
        self.__treeview.connect('drag_data_get', self.source_drag_data_get)
        column = gtk.TreeViewColumn()
        column.set_title('Name')
        render_pixbuf = gtk.CellRendererPixbuf()
        column.pack_start(render_pixbuf, expand=False)
        column.add_attribute(render_pixbuf, 'pixbuf', 0)
        render_text = gtk.CellRendererText()
        column.pack_start(render_text, expand=True)
        column.add_attribute(render_text, 'text', 1)
        self.__treeview.append_column(column)
        self.options = ListOptions(options)
        self.__scrolledwindow = HIGScrolledWindow()
        self.__scrolledwindow.set_policy(gtk.POLICY_AUTOMATIC,
                                         gtk.POLICY_AUTOMATIC)
        self.pack_start(self.__scrolledwindow, True, True )
        self.__scrolledwindow.add(self.__treeview)
        self.optiondisplay = optiondisplay

        self.exists_display = (self.optiondisplay != None ) #True or False
        self.set_option_display(optiondisplay)
    def get_model(self):
        return self.__model
    def get_list_option(self):
        return self.options 
    def source_drag_data_get(self, btn, context, selection_data, info, time):

        param_send = self.get_selected()
        #param_send = opt
        selection_data.set(selection_data.target, 8, param_send)
    def get_selected_option(self):
        '''
        @return: iter and model of option treeview selected
        '''
        treeselection = self.__treeview.get_selection()
        (model,iter) = treeselection.get_selected()
        return model, iter

    def set_option_display(self, optiondisplay):
        """
        Set a option display to change fields when cursor change
        @param optiondisplay: it's a mainframe that contains fields to set 
        @type optiondisplay: OptionDisplay
        """

        self.optiondisplay = optiondisplay
        self.exists_display = (self.optiondisplay != None ) #True or False
        if self.exists_display:
            log.debug('<<< Cursor changed')
            self.__treeview.connect("cursor-changed",self.update_option_display)


    def get_selected(self):
        """
        Returns the string with name of selected option
        """
        try:
            treeselection = self.__treeview.get_selection()
            (model,iter) = treeselection.get_selected()	
            return model.get_value(iter,1)
        except:
            return None            

    def update_option_display(self, widget):
        """
        Update option display contents 
        """
        if self.get_selected()==None :
            return
        option = self.options.get_option(self.get_selected())
        self.optiondisplay.set_option_list(option)
        self.optiondisplay.add_button.set_sensitive(False)
        self.optiondisplay.update_button.set_sensitive(True)   
        self.optiondisplay.delete_button.set_sensitive(True)

    def _arg_img(self, arg):
        if arg == 'str':
            return 'entry'
        elif arg == 'int':
            return 'spinbutton'
        elif arg == '' :
            return 'checkbutton'
        return 'label'
    def reload(self):
        """
        Reload items of treeview
        """

        list = self.options.get_options_list()
        for i in list:
            arg = self.options.get_arg_type(i)
            myiter = self.__model.insert_before(None, None)
            icon = gtk.Image()
            s = self._arg_img(arg)
            img_dir =  os.path.join(pixmaps_dir,'uie' ,'%s.png' % s)
            icon.set_from_file(img_dir)
            icon = icon.get_pixbuf()
            self.__model.set_value(myiter, 0, icon)
            self.__model.set_value(myiter, 1, i)


    def add(self, option):
        """
        Add a new option
        """
        cmd = CommandAddRemoveOptionMode(option, 
                                         self.options, 
                                         self.__model,
                                         self.optiondisplay,
                                         True)
        command_manager.add_command(cmd)


        #opt = option.get_option_dic()
        #self.options.add_option_from_dic(opt)

        #myiter = self.__model.insert_before(None, None)
        #arg = option.get_arg_type()
        #icon = gtk.Image()
        #s = self._arg_img(arg)
        #img_dir =  os.path.join(pixmaps_dir, '%s.png' % s)
        #icon.set_from_file(img_dir)
        #icon = icon.get_pixbuf()
        #self.__model.set_value(myiter, 0, icon)
        #self.__model.set_value(myiter, 1, option.get_name())
        #self.options.reload_opt()



    def save(self):
        """
        Save from option treeview to xml file 
        """
        self.options.write_file(options)


if __name__ == "__main__":
    o = OptionList()

