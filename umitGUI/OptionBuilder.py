#!/usr/bin/env python
# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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

from xml.dom import minidom

from higwidgets.higboxes import HIGHBox
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higbuttons import HIGButton

from umitGUI.FileChoosers import AllFilesFileChooserDialog

from umitCore.NmapOptions import NmapOptions
from umitCore.I18N import _
from umitCore.Paths import Path

options = Path.options


class OptionTab(object):
    def __init__(self, root_tab, options, constructor, update_func):
        actions = {'option_list':self.__parse_option_list,\
                   'option_check':self.__parse_option_check}

        self.options = options
        self.constructor = constructor
        self.update_func = update_func
        self.widgets_list = []

        options_used = self.constructor.get_options()
        
        # Cannot use list comprehhension because text nodes raise exception
        # when tagName is called
        for option_element in root_tab.childNodes:
            try:option_element.tagName
            except:pass
            else:
                if option_element.tagName in actions.keys():
                    self.widgets_list.append(actions[option_element.tagName](option_element, options_used))

    def __parse_option_list(self, option_list, options_used):
        options = option_list.getElementsByTagName(u'option')
        
        label = HIGEntryLabel(option_list.getAttribute(u'label'))
        opt_list = OptionList()
        
        for opt in options:
            opt_list.append(self.options.get_option(opt.getAttribute(u'name')))
        
        for i, row in enumerate(opt_list.list):
            if row[0] in options_used:
                opt_list.set_active(i)
                
        return label, opt_list
    
    def __parse_option_check(self, option_check, options_used):
        arg_type = option_check.getAttribute(u'arg_type')
        option = option_check.getAttribute(u'option')
        label = option_check.getAttribute(u'label')
        
        check = OptionCheck(label, self.options.get_option(option))
        check.set_active(option in options_used)
            
        type_mapping = { 
            "str": OptionEntry,
            "int": OptionIntSpin,
            "float": OptionFloatSpin,
            "level": OptionLevelSpin, 
            "path": OptionFile,
            "interface": OptionInterface
            }

        additional = None
        if type_mapping.has_key(arg_type):
            value = options_used.get(option, None)
            if value:
                additional = type_mapping[arg_type](value)
            else:
                additional = type_mapping[arg_type]()

        check.connect('toggled', self.update_check, additional)
        
        return check, additional

    def fill_table(self, table, expand_fill = True):
        yopt = (0, gtk.EXPAND | gtk.FILL)[expand_fill]
        for y, widget in enumerate(self.widgets_list):
            if widget[1] == None:
                table.attach(widget[0], 0, 2, y, y+1, yoptions=yopt)
            else:
                table.attach(widget[0], 0, 1, y, y+1, yoptions=yopt)
                table.attach(widget[1], 1, 2, y, y+1, yoptions=yopt)

        for widget in self.widgets_list:
            te = type(widget[1])
            if te == type(OptionList()):
                widget[1].connect('changed',self.update_list_option)
            elif te == type(OptionIntSpin()) or\
                 te == type(OptionFloatSpin()) or\
                 te == type(OptionEntry()):
                widget[1].connect('changed', self.update_entry, widget[0])
            elif te == type(OptionLevelSpin()):
                widget[1].connect('changed', self.update_level, widget[0])
            elif te == type(OptionFile()):
                widget[1].entry.connect('changed', self.update_entry, widget[0])
            elif te == type(OptionInterface()):
                widget[1].child.connect('changed', self.update_entry, widget[0])
            
    def update_check(self, check, extra):
        if check.get_active():
            te = type(extra)
            if te == type(OptionEntry()) or\
               te == type(OptionIntSpin()) or\
               te == type(OptionFloatSpin()):
                self.update_entry(extra, check)
            elif te == type(OptionLevelSpin()):
                self.update_level(extra, check)
            elif te == type(OptionFile()):
                self.update_entry(extra.entry, check)
            elif te == type(OptionInterface()):
                self.update_entry(extra.child, check)
            else:
                self.constructor.add_option(check.option['name'])
        else:
            self.constructor.remove_option(check.option['name'])

        self.update_command()
        
    def update_entry(self, widget, check):
        if not check.get_active():
            check.set_active(True)

        self.constructor.remove_option(check.option['name'])
        self.constructor.add_option(check.option['name'], widget.get_text())
        
        self.update_command()
    
    def update_level(self, widget, check):
        if not check.get_active():
            check.set_active(True)
        
        try:
            self.constructor.remove_option(check.option['name'])
            if int(widget.get_text()) == 0:
                check.set_active(False)
            else:
                self.constructor.add_option(check.option['name'],\
                                        level=int(widget.get_text()))
        except:pass
        
        self.update_command()

    def update_list_option(self, widget):
        try:widget.last_selected
        except:pass
        else:
            self.constructor.remove_option(widget.last_selected)
        
        option_name = widget.options[widget.get_active()]['name']
      
        self.constructor.add_option(option_name)
        widget.last_selected = option_name
        
        self.update_command()

    def update_command(self):
        if self.update_func:
            self.update_func()
    
                 
class OptionBuilder(object):
    def __init__(self, xml_file, constructor, update_func):
        """ OptionBuilder(xml_file, constructor)

        xml_file is a UI description xml-file
        constructor is a CommandConstructor instance
        """
        xml_desc = open(xml_file)
        self.xml = minidom.parse(xml_desc)
        # Closing file to avoid problems with file descriptors
        xml_desc.close()

        self.constructor = constructor
        self.update_func = update_func
        
        self.root_tag = "interface"
        
        self.xml = self.xml.getElementsByTagName(self.root_tag)[0]
        self.options = NmapOptions(options)
        
        self.groups = self.__parse_groups()
        self.section_names = self.__parse_section_names()
        self.tabs = self.__parse_tabs()
    
    def __parse_section_names(self):
        dic = {}
        for group in self.groups:
            grp = self.xml.getElementsByTagName(group)[0]
            dic[group] = grp.getAttribute(u'label')
        return dic
    
    def __parse_groups(self):
        return [g_name.getAttribute(u'name') for g_name in \
                  self.xml.getElementsByTagName(u'groups')[0].\
                  getElementsByTagName(u'group')]

    def __parse_tabs(self):
        dic = {}
        for tab_name in self.groups:
            dic[tab_name] = OptionTab(self.xml.getElementsByTagName(tab_name)[0],
                                      self.options, self.constructor, self.update_func)
        return dic

    
class OptionWidget:
    def enable_widget(self):
        self.set_sensitive(True)
    
    def disable_widget(self):
        self.set_sensitive(False)

class OptionInterface(gtk.ComboBoxEntry, OptionWidget):
    def __init__(self):
        self.list = gtk.ListStore(str)
        gtk.ComboBoxEntry.__init__(self, self.list)
        
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)

class OptionList(gtk.ComboBox, OptionWidget):
    def __init__(self):
        self.list = gtk.ListStore(str)
        gtk.ComboBox.__init__(self, self.list)
        
        cell = gtk.CellRendererText()
        self.pack_start(cell, True)
        self.add_attribute(cell, 'text', 0)
        
        self.options = []
    
    def append(self, option):
        self.list.append([option[u'name']])
        self.options.append(option)

class OptionCheck(gtk.CheckButton, OptionWidget):
    def __init__(self, label=None, option=None):
        gtk.CheckButton.__init__(self, label)
        
        self.option = option
    
    def get_option(self):
        return self.option


class OptionEntry(gtk.Entry, OptionWidget):
    def __init__(self, param = ""):
        gtk.Entry.__init__(self)
        self.set_text(param)

class OptionLevelSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=0):
        gtk.SpinButton.__init__(self,gtk.Adjustment(int(initial),0,10,1),0.0,0)

class OptionIntSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,gtk.Adjustment(int(initial),0,10**100,1),0.0,0)

class OptionFloatSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,gtk.Adjustment(float(initial),0,10**100,1),0.1,2)

class OptionFile(HIGHBox, OptionWidget, object):
    def __init__(self, param=""):
        HIGHBox.__init__(self)
        
        self.entry = OptionEntry()
        self.button = HIGButton(stock=gtk.STOCK_OPEN)
        
        self._pack_expand_fill(self.entry)
        self._pack_noexpand_nofill(self.button)

        self.entry.set_text(param)
        self.button.connect('clicked', self.open_dialog_cb)
    
    def open_dialog_cb(self, widget):
        dialog = AllFilesFileChooserDialog(_("Choose file"))
        if dialog.run() == gtk.RESPONSE_OK:
            self.entry.set_text(dialog.get_filename())
        dialog.destroy()

    def get_filename(self):
        return "\ ".join(self.entry.get_text().split(" "))

    def set_filename(self, filename):
        self.entry.set_text(" ".join(filename.split("\ ")))

    filename = property(get_filename, set_filename)

if __name__ == '__main__':
    o = OptionBuilder('profile_editor.xml')
    
    ol = OptionFile()
    w = gtk.Window()
    w.add(ol)
    w.show_all()
    w.connect('delete-event', lambda x,y,z=None: gtk.main_quit())
    gtk.main()
