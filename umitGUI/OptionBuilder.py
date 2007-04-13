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


class OptionBuilder(object):
    def __init__(self, xml_file):
        xml_desc = open(xml_file)
        self.xml = minidom.parse(xml_desc)

        # Closing file to avoid problems with file descriptors
        xml_desc.close()
        
        self.root_tag = "interface"
        self.actions = {'option_list':self.__parse_option_list,\
                        'option_check':self.__parse_option_check}
        
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
            tab = self.xml.getElementsByTagName(tab_name)[0]
            widgets_list = []
            # Cannot use list comprehhension because text nodes raise exception
            # when tagName is called
            for option in tab.childNodes:
                try:option.tagName
                except:pass
                else:
                    if option.tagName in self.actions.keys():
                        widgets_list.append\
                            (self.actions[option.tagName](option))
            
            dic[tab_name] = widgets_list
        
        return dic
    
    def __parse_option_list(self, option_list):
        options = option_list.getElementsByTagName(u'option')
        
        label = HIGEntryLabel(option_list.getAttribute(u'label'))
        opt_list = OptionList()
        
        for opt in options:
            opt_list.append(self.options.get_option\
                            (opt.getAttribute(u'name')))
        
        return label, opt_list
    
    def __parse_option_check(self, option_check):
        arg_type = option_check.getAttribute(u'arg_type')
        option = option_check.getAttribute(u'option')
        label = option_check.getAttribute(u'label')
        
        check = OptionCheck(label, self.options.get_option\
                            (option_check.getAttribute(u'option')))
        additional = None
        
        if arg_type == "str":
            additional = OptionEntry()
        elif arg_type == "int":
            additional = OptionIntSpin()
        elif arg_type == "float":
            additional = OptionFloatSpin()
        elif arg_type == "level":
            additional = OptionLevelSpin()
        elif arg_type == "path":
            additional = OptionFile()
        elif arg_type == "interface":
            additional = OptionInterface()
        
        return check, additional

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
    def __init__(self):
        gtk.Entry.__init__(self)

class OptionLevelSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=0):
        gtk.SpinButton.__init__(self,gtk.Adjustment(initial,0,10,1),0.0,0)

class OptionIntSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,gtk.Adjustment(initial,0,10**100,1),0.0,0)

class OptionFloatSpin(gtk.SpinButton, OptionWidget):
    def __init__(self, initial=1):
        gtk.SpinButton.__init__(self,gtk.Adjustment(initial,0,10**100,1),0.1,2)

class OptionFile(HIGHBox, OptionWidget, object):
    def __init__(self):
        HIGHBox.__init__(self)
        
        self.entry = OptionEntry()
        self.button = HIGButton(stock=gtk.STOCK_OPEN)
        
        self._pack_expand_fill(self.entry)
        self._pack_noexpand_nofill(self.button)
        
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
