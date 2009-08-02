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
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higbuttons import HIGMixButton, HIGButton
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higdialogs import HIGAlertDialog

from umit.core.UmitLogging import log
from umit.core.I18N import _


from umit.core.Paths import Path
pixmaps_dir = Path.pixmaps_dir
import sys

from umit.interfaceeditor.selectborder.WrapperWidgets import NotebookLabel, SpecialHBox
from umit.interfaceeditor.PageNotebook import BoxEditable, CommandPageNotebook
from umit.interfaceeditor.Command import Command, TwiceCommand, command_manager


''' 
This is a tool of the left frame of UIE
It do a part of the interface, and this tools is packed on the UIE Right frame
The toolbar is embeed on Profile Edit Mode and Wizard Edit Mode.


Have too others class to right frame of UIE like Design and Proprieties of 
NotebookLabels, and Items.
'''


TARGET_STRING = 0
TARGET_ROOTWIN = 1


target = [
    ('STRING', 0, TARGET_STRING),
    ('text/plain', 0, TARGET_STRING),
    ('application/x-rootwin-drop', 0, TARGET_ROOTWIN)
]


class ToolDesign(HIGScrolledWindow):
    ''' 
    ToolDesign contains widgets that you can add to Notebook to edit Profile
    and Wizard
    '''
    def __init__(self, only_text=True):
        HIGScrolledWindow.__init__(self)

        self._box = HIGVBox()
        vp = gtk.Viewport()

        self._box.set_border_width(6)
        if only_text:
            self._draw_buttons()
            self._pack()
        #ELSE == Algo com icons; ETC! 

        vp.add(self._box)
        vp.set_shadow_type(gtk.SHADOW_NONE)
        self.add(vp)
    def update_toolbar(self):
        pass

    def _draw_buttons(self):
        self.button_list = HIGButton('Option List')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'combo.png')
        img.set_from_file(img_dir)
        self.button_list.set_image(img)	


        self.button_list.drag_source_set(gtk.gdk.BUTTON1_MASK ,
                                         target, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.button_list.connect('drag_data_get', self._drag_option_list)	


        self.button_label = HIGButton('Label')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir,'uie',  'label.png')
        img.set_from_file(img_dir)
        self.button_label.set_image(img)

        self.button_label.drag_source_set(gtk.gdk.BUTTON1_MASK ,
                                          target, gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        self.button_label.connect('drag_data_get', self.source_drag_data_get)

        self.button_check = HIGButton('Option Check')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'checkbutton.png')
        img.set_from_file(img_dir)
        self.button_check.set_image(img)
        self.button_path = HIGButton('Choose Path')
        self.button_text_entry = HIGButton('String')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir,'uie', 'entry.png')
        img.set_from_file(img_dir)
        self.button_text_entry.set_image(img)
        self.button_float = HIGButton('Float Spin')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'spinbutton.png')
        img.set_from_file(img_dir)
        self.button_float.set_image(img)	

        self.button_level = HIGButton('Level Spin')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'spinbutton.png')
        img.set_from_file(img_dir)
        self.button_level.set_image(img)	
        self.button_interface = HIGButton('Interface')
        self.button_integer = HIGButton('Integer Spin ')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'spinbutton.png')
        img.set_from_file(img_dir)
        self.button_integer.set_image(img)	
    def source_drag_data_get(self, btn, context, selection_data, info, time):
        selection_data.set(selection_data.target, 8, "Label")
    def _drag_option_list(self, btn, context, selection_data, info, time):
        selection_data.set(selection_data.target, 8, "_widget_option_list")


    def _pack(self):
        box = self._box 
        box.pack_start(self.button_list, False, False)
        box.pack_start(self.button_label, False, False)
        #box.pack_start(self.button_check, False, False)
        #box.pack_start(self.button_path, False, False)
        #box.pack_start(self.button_float, False, False)
        #box.pack_start(self.button_integer, False, False)
        #box.pack_start(self.button_level, False, False)



class ToolBarInterface(gtk.EventBox):
    '''
    ToolBarInterface is embeed on the Profile and Wizard Edit Mode 
    '''
    def __init__(self):
        gtk.EventBox.__init__(self)
        self._profilecore = None 
        self.box_editable = None 
        self._optionlist = None 
        self.notebook = None
        self.ui_manager = gtk.UIManager()
        self.main_action_group = gtk.ActionGroup('MainActionGroup')
        self.main_actions = [ \

            ('Move up', gtk.STOCK_GO_UP, _('_Move up'), None, _('Move up'),
             self._move_item_up),
            ('Move down', gtk.STOCK_GO_DOWN, _('_Move down'), None,
             _('Move down'),
             self._move_item_down),
            ('Move Section Left', gtk.STOCK_GO_BACK, _('_Move Section Left'), 
             None, _('Move Section Left'), self._move_section_left),
            ('Move Section Right',gtk.STOCK_GO_FORWARD, _('_Move Section Right'), 
             None, _('Move Section Right'), self._move_section_right),
            ('Add Section', gtk.STOCK_ADD, _('_Add Section'), None,
             _('Add Section'), self._add_section),
            ('Remove Section', gtk.STOCK_REMOVE, _('_Remove Section'), 
             None, _('Remove Section'), self._remove_section),
            ('Add Place', gtk.STOCK_ADD, _('Add Place'), 
             None, _('Add Place'), self._add_place),
            ('Remove Option', gtk.STOCK_DELETE, _('Remove Option'), 
             None, _('Remove Option'), self._remove_option),

        ]
        self.ui_info = """
            <toolbar>
            <toolitem action='Move up'/>
            <toolitem action='Move down'/>
            <toolitem action='Add Place'/>
            <toolitem action='Remove Option'/>    
            <separator/>
            <toolitem action='Move Section Left'/>
            <toolitem action='Move Section Right'/>
            <toolitem action='Add Section'/>
            <toolitem action='Remove Section'/>
            <separator/>

            </toolbar>
            """



        self.main_action_group.add_actions(self.main_actions)
        self.main_accel_group = gtk.AccelGroup()
        for action in self.main_action_group.list_actions():

            action.set_accel_group(self.main_accel_group)
            action.connect_accelerator()

        #ENABLE = FALSE
        self.main_action_group.get_action('Move up').set_sensitive(False)
        self.main_action_group.get_action('Move down').set_sensitive(False)

        #END ENABLE 
        self.ui_manager.insert_action_group(self.main_action_group, 0)
        #try:
        self.ui_manager.add_ui_from_string(self.ui_info)
        self.toolbar = self.ui_manager.get_widget('/toolbar')
        self.toolbar.set_style(gtk.TOOLBAR_ICONS)
        self.toolbar.set_orientation(gtk.ORIENTATION_VERTICAL)

        #self.add(self.toolbar)
    def set_profilecore(self, profilecore):
        self._profilecore = profilecore
    def get_toolbar(self):
        return self.toolbar
    def set_optionlist(self, optionlist):
        self._optionlist = optionlist
    def enable(self,item, value):
        self.main_action_group.get_action(item).set_sensitive(value)
    def _remove_option(self, widget):
        if self.box_editable._old_selected ==None :
            d = HIGAlertDialog(type=gtk.MESSAGE_ERROR, 
                               message_format=_('Select a Option '), 
                               secondary_text=_('You do not select any option'))
            d.run()
            d.destroy()
        else:
            self.box_editable.delete_on_item(self.box_editable._old_selected)
    def _add_section(self, widget):
        '''
	Add a new section 
	'''
        new_name = self.notebook.get_new_name()
        page =  BoxEditable(new_name, self._profilecore, self._optionlist,
                            self.notebook, True)
        page.set_profile_core(self._profilecore)
        cmd = CommandPageNotebook(self.notebook,page, -1, self._profilecore, True)
        command_manager.add_command(cmd)

        page.send_signal_save()
    def _remove_section(self, widget):
        '''
        Remove section 
        '''
        self.notebook.delete_section()
    def _add_place(self,widget):
        self.box_editable.add_voidplace(-1)
    def _move_item_up(self, widget):    

        self.box_editable.move_item_up()
    def _move_item_down(self, widget):    
        self.box_editable.move_item_down()   
    def _move_section_left(self, widget):
        self.notebook.move_left()
    def _move_section_right(self, widget):
        self.notebook.move_right()
    def set_box_editable(self, boxeditable):
        self.box_editable = boxeditable
    def set_notebook(self, notebook):
        self.notebook = notebook

    def update_toolbar(self):
        boxeditable = self.box_editable
        self.enable('Move up', boxeditable.can_move_up())
        self.enable('Move down', boxeditable.can_move_down())
        self.enable('Move Section Left', self.notebook.can_move_left())
        self.enable('Move Section Right', self.notebook.can_move_right())


    def np(self, widget):
        pass


class CommandChangeLabel(TwiceCommand,Command):
    def __init__(self, widget, text, profilecore, page, state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Change Label'))
        self._profilecore = profilecore
        self._widget = widget
        self._text = text
        self._old_text = None
        self._is_section = False
        self._page = page

    def _identify(self, text):
        selected = self._widget
        if isinstance(selected, NotebookLabel):
            log.debug('update NotebookLabel')
            selected.set_text(text)
            self._is_section = True


            return 
        childs = selected.get_children()
        child_label = childs[0]
        if isinstance(child_label, gtk.HBox):
            log.debug('update OptionCheckIcon')
            #self._button_list.hide()
            child_label.cbutton.set_label(text)
        elif isinstance(child_label, gtk.EventBox):
            log.debug('update OptionList ')
            #self._button_list.show()
            other = child_label.get_children()[0]
            other.set_label(text)
    def _renama_profilecore(self, text1, text2):
        if self._is_section :
            self._profilecore.rename_section(text1, text2)
            self._page.set_name(text2)
        else: 
            section = self._widget.get_profileoption().get_section()
            self._profilecore.rename_option(section, text1, text2)
            self._widget.set_name(text2)
    def _rename(self):

        self._identify(self._text)
        self._old_text = self._widget.get_name()
        #Update ProfileCore: (section name)
        self._renama_profilecore(self._old_text, self._text)

    _execute_1 = _rename

    def _unrename(self):
        self._identify(self._old_text)
        #Update ProfileCore: (section name)
        self._renama_profilecore(self._text, self._old_text)


    _execute_2 = _unrename
import gobject
from OptionManager import OptionList
## Testing at devel 
#from os.path import split, join

#from umit.core.Paths import Path
#Path.set_umit_conf(join(split(__file__)[0], 'config', 'umit.conf'))
##END DEV TEST
#options = Path.options

class CommandUpdateOptionList(TwiceCommand, Command):
    def __init__(self, widget, list_new, list_old, profilecore,state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Update OptionList'))
        self._widget = widget
        self._new_list = list_new
        self._old_list = list_old
        self._profilecore = profilecore

    def _update_list(self, list):
        #Refresh Widget
        combo = self._widget.get_children()[1]
        combo.list.clear()
        for i in list :
            d= {}
            d['name'] = i  
            combo.append(d)

        #Update ProfileOption
        po = self._widget.get_profileoption()
        po.set_option_list(self._new_list)

        #Update ProfileCore
        self._profilecore.update_option_list(po.get_section(),
                                             po.get_label(),
                                             list)


    def _update_new(self):
        self._update_list(self._new_list)
    _execute_1 = _update_new
    def _update_old(self):
        self._update_list(self._old_list)
    _execute_2 = _update_old




class ListManager(gtk.Dialog):
    '''
    ListManager - manage the OptionList
    Tricks: 
     - To works with the Command Manager it save at __init__ the list 
       of options. After that. Add to CommandManager when clicked 'Ok Button'
       with the new and old list.
    '''
    def __init__(self, name, section, profilecore, widget, title):
        gtk.Dialog.__init__(self,title)
        self.set_size_request(450, 300)
        self._name = name
        self._section = section
        self._profilecore = profilecore
        self._widget = widget
        self._list = self._profilecore.get_list_opt(self._section, self._name)
        self._new_list = self._profilecore.get_list_opt(self._section, 
                                                        self._name)
        self._create_widgets()
        self.show()
        self._load_option_list()
        self._create_action_area()

    def _create_widgets(self):
        self._optionlist = OptionList()
        label = gtk.Label('Items at the %s ' % self._name)
        self._box = gtk.HPaned()
        ol = self._optionlist
        ol.reload()
        self.vbox.pack_start(label, False, False, 0)
        self._box.add(ol)
        self.vbox.pack_start(self._box)
        self._box.show_all()
        self._move_box = HIGVBox()
        self._add_bt = HIGButton(stock='gtk-add')
        self._add_bt.connect('clicked', self._on_add_press)
        self._remove_bt = HIGButton(stock='gtk-remove')
        self._remove_bt.connect('clicked', self._on_remove_press)
        #XXX - moves don't work yet: lack the connect
        self._move_up_bt = HIGButton(stock='gtk-go-up')
        self._move_down_bt = HIGButton(stock='gtk-go-down')
        self._move_box.pack_start(self._add_bt, False, False)
        self._move_box.pack_start(self._remove_bt, False, False)
        self._move_box.pack_start(self._move_up_bt, False, False)
        self._move_box.pack_start(self._move_down_bt, False, False)
        self._create_option_tv()

        self._box.set_position(200)
        self._box_other = gtk.HPaned()
        self._box.add(self._box_other)
        self._box_other.add(self._move_box)
        self._box_other.add(self._sw)
        self._move_box.show_all()
        self.vbox.show_all()

        label.show()

    def _create_option_tv(self):
        self._sw = HIGScrolledWindow()


        self._model = gtk.TreeStore(gobject.TYPE_STRING)
        self._tv = gtk.TreeView(self._model)
        column = gtk.TreeViewColumn()
        column.set_title('Name')
        render = gtk.CellRendererText()
        column.pack_start(render, expand=True)
        column.add_attribute(render, 'text', 0)
        self._tv.append_column(column)
        self._sw.add(self._tv)
        self._sw.show_all()
    def _load_option_list(self):
        list = self._list

        for i in list : 
            iter = self._model.insert_before(None, None)
            self._model.set_value(iter, 0, i)
    def _create_action_area(self):
        self._button_ok = HIGButton(stock='gtk-ok')
        self._button_cancel = HIGButton(stock='gtk-cancel')
        self._button_cancel.connect('clicked', self._on_cancel_press)
        self._button_ok.connect('clicked', self._on_ok_press)
        self.action_area.pack_start(self._button_cancel)
        self.action_area.pack_start(self._button_ok)
        self.action_area.show_all()

    def _on_add_press(self, widget):
        log.debug('<<< Add Option to OptionList')
        option_selected = self._optionlist.get_selected()
        iter = self._model.insert_before(None, None)
        self._model.set_value(iter, 0, option_selected)
        self._new_list.append(option_selected)

    def get_selected(self):
        """
        Returns the string with name of selected option
        """
        try:
            treeselection = self._tv.get_selection()
            (model,iter) = treeselection.get_selected()	
            return model.get_value(iter,0)
        except:
            return None            

    def get_selected_option(self):
        '''
        @return: iter and model of option treeview selected
        '''
        treeselection = self._tv.get_selection()

        (model,iter) = treeselection.get_selected()
        return model, iter    

    def _on_remove_press(self, widget):
        log.debug('<<< Remove Option from OptionList')
        selected = self.get_selected()
        (model, iter) = self.get_selected_option()
        if selected!=None:
            self._new_list.remove(selected)
            self._model.remove(iter)





    def _on_ok_press(self, widget):
        # Lists:
        list2 = self._list
        list1 = self._new_list

        cmd = CommandUpdateOptionList(self._widget, list1, list2, self._profilecore, True)
        command_manager.add_command(cmd)
        self.destroy()

    def _on_cancel_press(self, widget):
        self.destroy()



class Proprieties(HIGScrolledWindow):
    '''

    This box should be configurable 
    if widget is of a type all configuration should be change to this type

    #tricks: option_list have a icon to fill with options
    and option_check have a list of options in combo to change

    '''

    def __init__(self):
        HIGScrolledWindow.__init__(self)
        self._boxeditable = None 
        vp = gtk.Viewport()
        self._create_widgets()
        vp.add(self._box)
        vp.set_shadow_type(gtk.SHADOW_NONE)
        self.add(vp)
        self._profilecore = None 
        self._selected = None 

    def set_profilecore(self, profilecore):
        self._profilecore = profilecore


    def _create_widgets(self):
        '''
        Create the main entrys of the option 
        '''
        self._box = HIGVBox()


        self._table = HIGTable()


        #Name
        self._label_name  = HIGEntryLabel(_('Name'))
        self._entry_name = HIGTextEntry()

        self._entry_name.connect('activate', self._update_label)

        #Type 
        self._label_type = HIGEntryLabel(_('Type'))	
        self._combo_type = gtk.combo_box_new_text()
        self._combo_type.append_text('')
        self._combo_type.append_text('Option List')
        self._combo_type.append_text('Option Check')
        self._combo_type.set_active(0)
        self._combo_type.connect('changed', self.change_combo)

        self._label_opt = HIGEntryLabel(_('Option'))
        self._entry_opt = HIGTextEntry()
        self._entry_opt.set_sensitive(False)

        #For option list open a dialog to add/remove options
        self._button_list = HIGButton('Edit Option List')
        img = gtk.Image()
        img_dir =  os.path.join(pixmaps_dir, 'uie', 'combo.png')
        img.set_from_file(img_dir)
        self._button_list.set_image(img)
        self._button_list.connect('button-press-event', self._button_list_clicked)


        self._table.attach(self._label_name, 0,1,0, 1)
        self._table.attach(self._entry_name, 1,2,0,1)
        self._table.attach(self._label_type, 0,1,1,2)
        self._table.attach(self._combo_type, 1,2,1, 2)

        self._table.attach(self._button_list, 0,2, 3,4)
        self._table.attach(self._label_opt, 0,1, 4,5)
        self._table.attach(self._entry_opt, 1,2,4,5)

        self._box.pack_start(self._table, False, False)
    def _button_list_clicked(self, widget, event):
        section_name = self._boxeditable.get_name()
        lm = ListManager(self._entry_name.get_text(),section_name, 
                         self._profilecore, self._selected, _('List of items'))
    def _update_label(self, widget):
        #XXX Replace by Command
        print "Update Label"
        selected = self._selected
        cmd = CommandChangeLabel(selected, self._entry_name.get_text(), 
                                 self._profilecore,self._boxeditable, True)
        command_manager.add_command(cmd)
        #if isinstance(selected, NotebookLabel):
            #log.debug('update NotebookLabel')
            #selected.set_text(self._entry_name.get_text())
            #return 
        #childs = selected.get_children()
        #child_label = childs[0]
        #if isinstance(child_label, gtk.HBox):
            #self._button_list.hide()
            #child_label.cbutton.set_label(self._entry_name.get_text())
        #elif isinstance(child_label, gtk.EventBox):
            #self._button_list.show()
            #other = child_label.get_children()[0]
            #other.set_label(self._entry_name.get_text())

    def change_combo(self,combo):
        model = combo.get_model()
        index = combo.get_active()
        if index:
            if model[index][0]=='Option List':

                log.debug('Show Button List ')
                self._button_list.show()

            else:

                log.debug('Hide Button List ')
                self._button_list.hide()
        return
    def show_notebook_label(self):
        '''
        show proprieties of notebook label and hide others
        '''
        pass


    def show_item(self):
        pass
    def hide_item(self):
        self._label_opt.hide()
        self._entry_opt.hide()
        self._button_list.hide()
        self._combo_type.hide()
        self._label_type.hide()
        self._entry_name.hide()
        self._label_name.hide()
    def set_notebooklabel(self, selected):
        self._entry_name.show()
        self._label_name.show()
        self._entry_name.set_text(selected.get_text())
        self._button_list.hide()
        self._combo_type.hide()
        self._label_type.hide()
        self._label_opt.hide()
        self._entry_opt.hide()
        self._selected = selected
    def set_item(self, selected):
        self._entry_name.show()
        self._label_name.show()

        self._selected = selected
        if selected.get_name()!=None:
            self._entry_name.set_text(selected.get_name())
        else: 
            self.hide_item()
            return
        childs = selected.get_children()
        self._combo_type.show()
        self._label_type.show()
        child_label = childs[0]
        if isinstance(child_label, gtk.HBox):
            #OptionCheck
            self._label_opt.show()
            self._entry_opt.show()
            opt_ = self._profilecore.get_opt_check(self._boxeditable.get_name(),
                                                   selected.get_name())
            self._entry_opt.set_text(opt_)
            self._button_list.hide()
            child_label.cbutton.set_label(self._entry_name.get_text())
            self._combo_type.set_active(2)
            #XXX: Put other widget that sensitible = False with option name


        elif isinstance(child_label, gtk.EventBox):
            #OptionList
            self._button_list.show()
            other = child_label.get_children()[0]
            other.set_label(self._entry_name.get_text())
            self._combo_type.set_active(1)
        #Disable Combo to change OptionList/OptionChange
        self._combo_type.set_sensitive(False)

    def set_boxeditable(self, boxeditable):
        self._boxeditable = boxeditable
    def update(self):
        pass

    def disable_all(self):
        self._label_opt.hide()
        self._entry_opt.hide()
        self._button_list.hide()
        self._combo_type.hide()
        self._label_type.hide()
        self._entry_name.hide()
        self._label_name.hide()
    def load_data(self, option):
        pass 
    def unload(self,option):
        pass 
