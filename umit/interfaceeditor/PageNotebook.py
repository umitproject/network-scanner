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
from umit.gui.OptionBuilder import *
from umit.interfaceeditor.Command import Command, TwiceCommand, command_manager
from higwidgets.higboxes import HIGVBox
from umit.interfaceeditor.selectborder.WrapperWidgets import NotebookLabel, SpecialHBox
from umit.core.UmitLogging import log
from umit.core.I18N import _
from higwidgets.higtables import HIGTable
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel

from umit.interfaceeditor.ProfileCore import ProfileOption, option_to_profileoption

TARGET_STRING = 0
TARGET_ROOTWIN = 1

target = [
    ('STRING', 0, TARGET_STRING),
    ('text/plain', 0, TARGET_STRING),
    ('application/x-rootwin-drop', 0, TARGET_ROOTWIN)
]


#Global variables 
SPACE_TABLE = 6



# XXX : Should be put in other file to using by OptionBuilder too 
type_mapping = { 
    "str": OptionEntry,
    "int": OptionIntSpin,
    "float": OptionFloatSpin,
    "level": OptionLevelSpin, 
    "path": OptionFile,
    "interface": OptionInterface, 
    "scriptlist": OptionScriptList
}

class CommandAddRemoveVoidplace(TwiceCommand, Command):
    '''
    Add or Remove A voidplace on the Editor-Mode 

    '''
    def __init__(self, table, widget, coords, state): 
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Add/Remove Voidplace'))
        self._box = table
        self._table = table.get_table()

        self._widget = widget
        self._coords = coords
        self._x,self._y = coords[widget]  
        #self._spacing = self._table.get_row_spacing(self._x)
        self._spacing = SPACE_TABLE
    def _add(self):


        #self._widget.do_draw()
        label = self._widget.get_children()[0]
        label = gtk.Label()

        label.show()

        self._widget.set_size_request(-1, 23)
        self._widget.show()
        self._widget.set_view(True)

        if self._widget.is_voidplace():
            self._widget.show_voidplace()

        self._widget.set_view(True)
        #self._table.attach(self._widget, 0,2,self._x,self._y)

        #self._widget.do_voidplace()

        self._table.set_row_spacing(self._x,self._spacing)
        from umit.interfaceeditor.BugDiff import BugDiff
        BugDiff.pdic(self._coords)
        log.debug('CommandVoidplace: add voidplace')

    _execute_1 = _add 
    def _remove(self):
        log.debug('CommandVoidplace: remove voidplace')


        if self._widget != None and self._widget.is_voidplace():

            self._widget.hide_voidplace()
            self._widget.set_select(False)
            self._widget.hide()
            self._widget.set_view(False)
            self._table.set_row_spacing(self._x,0)
            self._widget.set_size_request(-1, 0)
            pass
            #self._widget.unload_voidplace()
            #self._table.remove(self._widget)
        if self._widget!= None :
            self._widget.hide()
            self._widget.set_view(False)
            self._table.set_row_spacing(self._x,0)
            self._widget.set_size_request(-1, 0)
        from umit.interfaceeditor.BugDiff import BugDiff
        BugDiff.pdic(self._coords)
    _execute_2 = _remove



class CommandVoidPlaceAttach(TwiceCommand, Command):
    '''
    Add a new widget (voidplace) at the last position 

    '''
    def __init__(self,table, widget, coords, state):
        self._last = table.get_last()
        self._box = table
        self._old_last = self._last
        if self._last != None :
            x, y = coords[self._last] 
        else: 
            x, y = -1,0
        coords[widget] = [x  +1 , y+1]
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Add/Remove Voidplace'))
        self._table = table.get_table()
        self._box.set_last(widget)
        self._widget = widget
        self._x,self._y = coords[widget]  
        self._coords = coords
        #self._spacing = self._table.get_row_spacing(x-1)
        self._spacing = SPACE_TABLE
    def _attach(self):
        self._table.resize(self._y, 2)
        log.debug('<<< Attach Add Voidplace')
        self._table.set_row_spacing(self._x,self._spacing)

        self._table.attach(self._widget, 0, 2, self._x, self._y)
        self._widget.show_all()
        self._widget.do_voidplace()
        self._widget.set_view(True)
        self._box._last = self._widget
        try: 
            self._coords[self._widget]
        except:
            self._coords[self._widget] = [self._x, self._y]


        #try:
            #x,y =self._coords[self._widget]
        #except:
            #self._coords[self._widget] = [self._x, self._y]
    _execute_1 = _attach
    def _unattach(self):
        #if self._widget != None and self._widget.is_voidplace():
            #log.debug('<<< remove voidplace unattach')
            #self._widget.hide_voidplace()
            #self._widget.set_select(False)
            #self._widget.hide()
            #self._table.set_row_spacing(self._x,0)
        self._widget.unload_voidplace()
        self._table.remove(self._widget)
        #from umit.interfaceeditor.BugDiff import BugDiff
        #BugDiff.pdic(self._coords)
        #BugDiff.pref(self._widget)
        del self._coords[self._widget]
        self._box._last = self._old_last
    _execute_2 = _unattach

class CommandMove(TwiceCommand, Command):
    '''
    Move items to down or up
    #Trick: 
    - Add other colums to save row and do a swap. Use a temporary widget. 
    '''
    def __init__(self, widget_container, widget, coords , profilecore,  state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Move item'))
        self._parent = widget_container
        self._section_name = widget_container.get_name()
        self._table = widget_container.get_table()
        self._move = widget
        self._coords = coords
        self._profilecore = profilecore
        self._x, self._y = self._coords[widget]
        self._name = widget.get_name()
        if self._name == None:
            self._voidplace = True 
        else :
            self._voidplace = False



    def _determine_child(self, list, num): 
        result = None 
        x, y = self._coords[self._move]
        x = x + num 
        y = y + num 
        for i in list : 
            x_tmp, y_tmp = self._coords[i]
            if x_tmp == x and y_tmp == y  :
                result= i
                break 
        return result
    def _get_next(self):

        childs = self._table.get_children()
        num = 1
        while True:	    
            child = self._determine_child(childs, num)
            if child.is_hide():
                num = num+1
            else:
                break 
        return child  
    def _get_prev(self): 

        childs = self._table.get_children()
        childs.reverse()
        num = -1 
        while True:
            child = self._determine_child(childs,num) 
            if child.is_hide():
                num = num -1 
            else:
                break
        return child
    def _swap(self, widget1, widget2):
        x1, y1 = self._coords[widget1]
        x2, y2 = self._coords[widget2]
        list_vp = []
        if widget1.is_voidplace():
            widget1.unload_voidplace()
            list_vp.append(widget1)

        if widget2.is_voidplace():
            list_vp.append(widget2)
            widget2.unload_voidplace()



        widget1.set_select(False)
        widget2.set_select(False)
        w_tmp = gtk.Label('tmp')
        self._table.attach(w_tmp, 1,2, x1, y1)
        self._table.remove(widget1)
        self._table.attach(widget1, 0,2, x2, y2)
        self._table.remove(widget2)
        self._table.attach(widget2, 0,2, x1, y1)
        self._table.remove(w_tmp)

        self._coords[widget1] = [x2, y2]
        self._coords[widget2] = [x1,y1]
        #self._move = widget2
        for i in list_vp:
            i.do_voidplace()
            #i.do_resize_voidplace()

        #Ajust the next opt to write in ProfileCore

        po_1 = widget1.get_profileoption()
        po_2 = widget2.get_profileoption()
        tmp_1 = None 
        tmp_2 = None
        if po_2 != None:
            tmp_2 = po_2.get_next_opt()
        if po_1 != None:
            tmp_1 = po_1.get_next_opt()
            po_1.set_next_opt(tmp_2)
        if po_2 != None:
            po_2.set_next_opt(tmp_1)

        if widget1 == self._parent._last :
            self._parent._last = widget2
        elif widget2 == self._parent._last :
            self._parent._last = widget1

    def _move_up(self):

        widget_swap = self._get_prev()
        if not self._voidplace : 
            self._profilecore.move_option_up(self._section_name, 
                                             self._name,
                                             widget_swap.get_name())
        self._swap(self._move, widget_swap)
        #widget_swap.do_resize_voidplace()
        self._parent.send_signal()
        self._move.do_draw()
        log.debug('<<< Moving item up')
    _execute_1 = _move_up

    def _move_down(self):

        widget_swap = self._get_next()
        if not self._voidplace : 
            self._profilecore.move_option_down(self._section_name, 
                                               self._name, 
                                               widget_swap.get_name())
        self._swap( widget_swap, self._move)
        #x, y = self._coords[widget_swap]
        #self._move.set_select(False)
        #widget_swap.set_select(False)

        #w_tmp = gtk.Label('tmp')
        #self._table.attach(w_tmp, 1,2, x, y)
        #self._table.remove(widget_swap)
        #self._table.attach(widget_swap, 0,2, self._x, self._x+1)
        #self._table.remove(self._move)

        #self._table.attach(self._move, 0,2, x, y)
        #self._table.remove(w_tmp)

        #self._coords[widget_swap] = [self._x, self._y]
        #self._coords[self._move] = [x,y]
        self._parent.send_signal()
        self._move.do_draw()
        log.debug('<<< Moving item down')

    _execute_2 = _move_down


class CommandAddRemoveOption(TwiceCommand, Command):
    ''' 
    Add or Remove Option from BoxEditable 
    ###
    trik : state is a inicial value if it is remove or add.
    '''
    def __init__(self, widget_container, widget_option,profilecore, page, state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Add/Remove Option'))
        self._widget = widget_container
        self._widget_option = widget_option
        self._profilecore = profilecore
        self._saved = None 
        self._page = page


    def _add_option(self):
        widget_option = self._widget_option
        widget = self._widget
        childs = widget.get_children()
        widget.remove(childs[0])
        if widget.is_voidplace():
            widget.unload_voidplace()
        if self._saved==None:
            for k in widget_option:
                widget.pack_start(k)
                k.show_all()
        else: 
            for k in self._saved:
                widget.pack_start(k)
                k.show_all()
        #self._widget.show_all()
        #widget_option.show() # XXX - may be need 

        #Profile Core modifications: 
        po = self._widget.get_profileoption()
        #print po.get_next_opt()
        widget_prev = self._page.get_prev_widget(self._widget)
        #widget_next = self._page.get_next_widget(self._widget)
        #print widget_prev
        #print widget_next
        if widget_prev !=None:
            po.set_next_opt(widget_prev.get_profileoption().get_next_opt())
            widget_prev.get_profileoption().set_next_opt(po.get_label())
        self._profilecore.add_from_profileoption(po)



        log.debug('Adding option')
    _execute_1 = _add_option
    def _remove_option(self):

        widget = self._widget
        childs = widget.get_children()
        self._saved = [] 
        for i in childs:
            widget.remove(i)
            self._saved.append(i)
        t = gtk.Label('-')
        t.set_size_request(-1, 23)
        t.show()

        widget.pack_start(t)
        widget.do_voidplace()


        #Profile Core modifications: 
        po = self._widget.get_profileoption()

        widget_prev = self._page.get_prev_widget(self._widget)
        #widget_next = self._page.get_next_widget(self._widget)
        #print widget_prev
        #print widget_next
        #po.set_next_opt(None)

        #XXX <--- this protection should be wrong, too defencive 
        if widget_prev!=None:

            widget_prev.get_profileoption().set_next_opt(po.get_next_opt())

        self._profilecore.remove_opt(po.get_section(), po.get_label())


        log.debug('Removing option, Adding Void Place')
    _execute_2 = _remove_option


class CommandPageNotebook(TwiceCommand, Command):
    '''
    Add Page at Notebook or Remove
    '''
    def __init__(self, notebook, page, number, profilecore, state):
        TwiceCommand.__init__(self, state)
        Command.__init__(self, _('Add/Remove Page'))
        self._notebook = notebook
        self._page = page
        self._number = number
        self._profilecore = profilecore
        self._name = self._page.get_name()

        self.label = None

        self._new = False



    def _add_page(self):
        log.debug('<<< Add new page')
        if self.label == None :
            label = self._notebook.create_label(self._name)
        else : 
            label = self.label

        if self._number == -1:
            self._notebook.sections_widgets_list.append(label)
            self._notebook.sections_widgets[label] = self._notebook.get_n_pages()
        else:
            num = self._number
            self._notebook.sections_widgets_list.insert(num,label)
            self._notebook.sections_widgets[label] = self._number-1
            for i in range(num-1, len(self._notebook.sections_widgets)-1):
                widget_tmp = self._notebook.sections_widgets_list[i+1]
                self._notebook.sections_widgets[widget_tmp] = self._notebook.sections_widgets[widget_tmp] + 1 

        self._notebook.insert_page(self._page, label, self._number)
        #self._notebook.append_page(self._page, label)
        self._page.show_all()
        label.voidplace()
        label.show_all()

        #profilecore
        #print self._name
        elem = self._profilecore.search_in_groups(self._name)
        if elem == None:

            self._profilecore.add_section(self._name)
            label.set_name(self._name)

    _execute_1 = _add_page
    def _remove_page(self):
        #self._notebook._old_select.unload_voidplace()
        label_tmp =self._notebook.get_tab_label(
            self._notebook.get_nth_page(self._number))
        name = label_tmp.get_name()
        if label_tmp.is_voidplace():
            label_tmp.unload_voidplace()
        self.label = label_tmp
        num = self._notebook.sections_widgets[label_tmp]
        del self._notebook.sections_widgets[label_tmp]
        #print range(num,len(self._notebook.sections_widgets))
        #from pprint import pprint
        #pprint(self._notebook.sections_widgets)
        #print "----\n"
        #pprint(self._notebook.sections_widgets_list)
        #from umit.interfaceeditor.BugDiff import BugDiff
        #BugDiff.plist(self._notebook.sections_widgets_list)
        #BugDiff.pdic(self._notebook.sections_widgets)
        for i in range(num, len(self._notebook.sections_widgets)):
            widget_tmp = self._notebook.sections_widgets_list[i+1]

            #BugDiff.pref(widget_tmp)
            #pprint(self._notebook.sections_widgets)
            self._notebook.sections_widgets[widget_tmp] = self._notebook.sections_widgets[widget_tmp] - 1 

        self._notebook.sections_widgets_list.pop(num)
        self._notebook.remove_page(self._number)
        self._profilecore.remove_section(name)


    _execute_2 = _remove_page


class BoxEditable(HIGVBox):
    def __init__(self, section_name, profile, listoptions, notebook_parent, new=False):
        """
        A Box Editable contains a options of each tab
        @param section_name: section name <tab>
        @type section_name: str 
        @param profile: A class that view and modify xml file 
        @type profile: ProfileCore
        @param listoptions: The List of Options to update XML (I guess to confirm)
        @type listoptions: ListOptions
        @param notebook_parent: Notebook
        @type notebook_parent: Notebook or Subclass
        @param new: It's a new tab or not 
        @type new: bool
        """

        HIGVBox.__init__(self)
        self._coords = {}
        self._parent = notebook_parent
        self._last = None 
        #Profile Core do a manage at profile_editor.xml file 
        self._profilecore = None 

        self._profile = profile
        self._listoptions = listoptions
        self._table = HIGTable()
        self._section_name = section_name
        if not new :
            self._options = self._profile.get_section(section_name)
        self._table.set_border_width(3)
        c = self.get_colormap()
        color = c.alloc_color(0,0,0)   
        self._table.modify_fg(gtk.STATE_NORMAL,color )
        #self._fill_table()

        box_tmp = HIGVBox()
        box_tmp.pack_start(self._table, False, False)
        self._sw = HIGScrolledWindow()
        #self._sw.set_size_request(400,200)
        vp = gtk.Viewport()
        vp.add(box_tmp)
        vp.set_shadow_type(gtk.SHADOW_NONE)
        self._sw.add(vp)
        self.pack_start(self._sw, True, True)
        self._old_selected = None 
        self._x = 0
        self._y = 0 


        self.connect('button-press-event', self._bp)
    #Private API 
    def _bp(self, widget,event):
        pass

    def _fill_table(self):
        k = 0
        self._old_po = None
        for i in self._options:
            t = SpecialHBox()
            type = i.get_type()
            if type== 'option_check':

                name_option = i.get_option()
                hint = self._listoptions.get_hint(name_option)
                tmp_widget = OptionCheckIcon(i.get_label(),name_option,hint)
                t.pack_start(tmp_widget)
                arg_type = self._listoptions.get_arg_type(name_option)
                if arg_type!= '':
                    additional = type_mapping[arg_type]()
                    t.pack_start(additional)
                po = ProfileOption('option_check', i.get_label(),name_option, 
                                   arg_type,None)
                po.set_section(self.get_name())
                t.set_profileoption(po)


            elif type == 'option_list': 
                eventbox = gtk.EventBox()
                label = HIGEntryLabel(i.get_label())

                eventbox.add(label)
                tmp_widget = OptionList()
                list = []
                for j in i.get_option_list():
                    d = {}
                    d['name'] = j 
                    tmp_widget.append(d)
                    list.append(j)
                po = ProfileOption('option_list', i.get_label(),i.get_label(), 
                                   None,list)
                po.set_section(self.get_name())
                t.set_profileoption(po)
                t.pack_start(eventbox)		
                t.pack_start(tmp_widget)
                #t.drag_source_set(gtk.gdk.BUTTON1_MASK |
                                                    #gtk.gdk.BUTTON3_MASK,
                                                    #target, 
                                                    #gtk.gdk.ACTION_COPY |
                                                    #gtk.gdk.ACTION_MOVE)
                #t.connect('drag_data_get', self.source_drag_data_get)

            #XXX : I think that is very important ( I only comment to get focus)
            if self._old_po!=None:
                self._old_po.set_next_opt(i.get_label())
            self._old_po = po
            t.set_flags( t.flags() |  gtk.CAN_FOCUS)
            t.connect('button-press-event', self._button_press_event)
            t.connect('key-press-event', self._key_press_event)
            t.set_name(i.get_label())
            t.connect('drag_data_received', self.drag_received)
            t.drag_dest_set(gtk.DEST_DEFAULT_ALL, target[:-1],
                            gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)

            self._table.attach(t, 0,2, k,k+1)
            self._coords[t] = [k, k+1]
            self._x = k 
            self._y = k+1
            k =k +1
            self._last = t 


    def delete_on_item(self, widget):
        if not widget.is_voidplace(): 
            # remove widgets like checkbuttons or others and put voidplace
            childs = widget.get_children()
            cmd = CommandAddRemoveOption(widget,childs,
                                         self._profilecore,self, False)
            widget.set_select(False)
            command_manager.add_command(cmd)
            log.debug(' Remove Widgets like CheckButtons or others and put voidplace')

        else:
            # remove voidplace and delete the widget from table/box
            #XXX 
            cmd = CommandAddRemoveVoidplace(self, 
                                            widget, self._coords, False)
            #widget.unload_voidplace()
            command_manager.add_command(cmd)
            log.debug('Remove voidplace and delete the widget from table')


        self._parent.emit('need-save', 'Sent', None)

    def _key_press_event(self, widget, event):
        _keyval = gtk.gdk.keyval_name(event.keyval)
        if _keyval == "Delete" and self._old_selected!=None :
            self.delete_on_item(widget)


        #self._table.remove(widget)
        #childs = self._table.get_children()
        #for i in childs:
            #if i.is_voidplace():
                #i.do_resize_voidplace()
    def _button_press_event(self,widget, event):

        widget.set_select(True) 
        self._parent.select(False)
        if widget == self._old_selected :
            log.debug('Do nothing')
            if widget.is_voidplace():
                widget.do_draw()
            widget.grab_focus()
            return 
        widget.do_draw()
        if self._old_selected != None:
            self._old_selected.set_select(False)
        log.debug('drawing')
        self._old_selected = widget
        widget.grab_focus()
        self._parent.emit('changed', 'Options', self._parent.get_current_page())
    #Public API 
    def set_name(self, name):
        self._section_name = name 
    def get_name(self):
        return self._section_name

    def get_generic_widget(self, widget, num):
        '''
        Get widget - None Vodplace
        '''
        result = None 
        num  = num 
        x1,y1 = self._coords[widget]
        while True : 
            for i in self._coords:
                x,y = self._coords[i]
                if x == (x1-num) and y == (y1-num):
                    result = i
                    break 
            if result!=None and result.is_voidplace():
                num = num +1 
                result = None 
            else: 
                break 
        return result
    def get_next_widget(self, widget):
        '''
        Get the next widget - None Vodplace
        '''
        if widget == self._last:
            return None 
        return self.get_generic_widget(widget, -1)

    def get_prev_widget(self, widget):
        '''
        Get a Previews widget - None Voidplace 
        '''
        x, y = self._coords[widget]
        if x == 0 and y == 1: 
            return None 
        return self.get_generic_widget(widget, 1)



    def can_move_up(self):

        widget = self._old_selected
        x = 0 
        if widget!= None :
            try:
                x,y = self._coords[widget]
            except KeyError:
                return False
        return x != 0
    def can_move_down(self):

        widget = self._old_selected
        y = len(self._coords)
        if widget!= None :
            try:
                x,y = self._coords[widget]
            except KeyError:
                return 
        return y != (len(self._coords))
    def send_signal_save(self):
        self._parent.emit('need-save', 'Sent', None)
    def send_signal(self):
        self._parent.emit('changed', 'Options', self._parent.get_current_page())
    def create_item(self):
        t = SpecialHBox()
        e = gtk.EventBox()
        label = gtk.Label('-')
        label.set_size_request(-1, 23)
        #e.add(label)
        t.pack_start(label)
        t.set_flags( t.flags() |  gtk.CAN_FOCUS)
        t.connect('button-press-event', self._button_press_event)
        t.connect('key-press-event', self._key_press_event)
        t.connect('drag_data_received', self.drag_received)
        t.drag_dest_set(gtk.DEST_DEFAULT_ALL, target[:-1],
                        gtk.gdk.ACTION_COPY | gtk.gdk.ACTION_MOVE)
        return t 
    def add_voidplace(self, position):
        # Create SpecialHBox with Voidplace
        t = self.create_item()
        cmd = CommandVoidPlaceAttach(self, t, self._coords, True)
        command_manager.add_command(cmd)
        self._parent.emit('need-save', 'Sent', None)

        #if position == -1 : 
            #x, y = self._x,self._y 
            #self._table.attach()
        #else:
            ## Choose the position 
            #pass

    def move_item_down(self):
        '''
        Move selected item to down
        '''
        assert self.can_move_down()

        cmd = CommandMove(self, self._old_selected, self._coords, self._profilecore, False)
        command_manager.add_command(cmd)
        self.send_signal()
        self.send_signal_save()
    def move_item_up(self):
        '''
        Move selected item to up
        '''
        assert self.can_move_up()

        cmd = CommandMove(self, self._old_selected, self._coords, self._profilecore, True)
        command_manager.add_command(cmd)
        self.send_signal()
        self.send_signal_save()


    def search_option(self, name):
        '''
        returns widget 
        '''
        list = self._table.get_children()
        result = None 
        for i in list : 
            if i.get_name() == name : 
                result = i
                break
        return result

    def set_profile_core(self, profile_core):
        self._profilecore = profile_core

    def option_builder(self, option_name, type):
        '''
        construct a widget with the name of the option
        @return: A widget
        @rtype: Widget like OptionCheck or others 
        '''
        result = []
        hint = self._listoptions.get_hint(option_name)
        #label, option_name, hint
        tmp_widget = OptionCheckIcon(option_name,option_name,hint) 
        result.append(tmp_widget)
        arg_type = self._listoptions.get_arg_type(option_name)
        if arg_type!= '':
            additional = type_mapping[arg_type]()
            result.append(additional)
        return result




    def _is_widget(self, name):
        return name[0:4] == '_wid'
    def _create_option_list(self, widget):
        eventbox = gtk.EventBox()
        name = 'New Option List'
        label = HIGEntryLabel(name)

        eventbox.add(label)
        tmp_widget = OptionList()
        list = []
        void = {'name':''}
        j = 'None'
        d = {}
        d['name'] = j 
        tmp_widget.append(void)
        tmp_widget.append(d)
        list.append(j)
        po = ProfileOption('option_list',name ,None, 
                           None,list)
        po.set_section(self.get_name())
        widget.set_profileoption(po)
        widgets = [] 
        widgets.append(eventbox)
        widgets.append(tmp_widget)
        widget.set_name(name)
        return widgets

    def exec_option_list(self, w):
        widgets = self._create_option_list( w)
        cmd = CommandAddRemoveOption(w,widgets, self._profile,self,
                                     True)
        command_manager.add_command(cmd)

    def exec_checkopt(self, name, w):
        option_name = name
        opt = self._listoptions.get_option_class(name)
        profileoption = option_to_profileoption(opt)
        profileoption.set_section(self.get_name())
        arg_type = self._listoptions.get_arg_type(name)
        widgets = self.option_builder(option_name, arg_type)
        w.set_profileoption(profileoption)
        w.set_name(name)
        cmd = CommandAddRemoveOption(w, widgets, self._profilecore, self,True)
        command_manager.add_command(cmd)






    def drag_received(self,w, context, x, y, data, info, time):
        if not w.is_voidplace(): 
            return 
        option_name = data.data
        if self._is_widget(option_name) :
            if option_name == '_widget_option_list':
                self.exec_option_list(w)
                #widgets = self._create_option_list( w)
                #cmd = CommandAddRemoveOption(w,widgets, self._profile,
                                                #True)
                #command_manager.add_command(cmd)

            return
        name = data.data
        self.exec_checkopt(name, w)

        #Remove child 
        #childs = w.get_children()
        #w.remove(childs[0])
        #Add

        #for child in widgets:
            #t = gtk.Label('fsck')
            #tmp_w.pack_start(child)
            #child.show_all()

        #w.unload_voidplace()


    def get_table(self):
        return self._table
    def set_last(self, last):
        self._last = last
    def get_last(self):
        return self._last
    def source_drag_data_get(self, btn, context, selection_data, info, time):
        selection_data.set(selection_data.target, 8, "I'm Data!")    
