# Copyright (C) 2008 Adriano Monteiro Marques.
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA


"""
Widget to make semilar tabs to firefox

References:
http://www.moeraki.com/pygtktutorial/pygtk2reference/class-gtkiconview.html

Idea of implementation:

Create a Scroll Box with icons of tabs


"""
import gtk
import cairo
import gobject

from higwidgets.higboxes import HIGHBox
from higwidgets.higscrollers import HIGScrolledWindow

from umit.preferences.widgets.IconToggleWidget import IconToggleWidget

import os.path
from umit.core.Paths import Path
# Develpment step
Path.set_umit_conf("umit")


class TabStruct:
    """ Struct of tab """
    def __init__(self):
        """ Constructor """
        self.__list = {}
        self.__first_k = None
    ### Interface - Public Functions ###
    def add_item(self, name, image=None, image_bw=None, widget=None):
        """
        @param name name of item
        @param image image selected
        @param image_bw imae black and white - unselected
        @param widget widget associated
        """
        if self.__list == {}:
            self.__first_k = name
        self.__list[name] = image, image_bw, widget

    def del_item(self, name):
        if self.exists(name):
            del self.__list[name]
    def exists(self, name):
        self.__list.has_key(name)
    def get_first(self):
        """
        @return str
        """
        self.__first_k
    def is_empty(self):
        return self.__list=={}



class TabsIcon(HIGHBox):
    def __init__(self):
        """ Constructor """
        HIGHBox.__init__(self)
        self.scroll = HIGScrolledWindow()
        self._box = HIGHBox()
        self._icons_list = []
        self._tabstruct = TabStruct()
        self.__current = [0]
        self.__model = gtk.ListStore(str, gtk.gdk.Pixbuf)
        #self.__model = gtk.ListStore(str, HIGHBox)
        self.__pixmap_d = Path.pixmaps_dir

        self.__icon = gtk.IconView()
        self.__icon.set_model(self.__model)
        self.__icon.set_text_column(0)
        self.__icon.set_pixbuf_column(1)


        self.__icon.set_orientation(gtk.ORIENTATION_VERTICAL)
        self.__icon.set_selection_mode(gtk.SELECTION_SINGLE)

        # Change background color -- FIXME
        #self.__icon.set_name("icon tabs")
        #gtk.rc_parse_string(
#"""
#style "iconview"
#{
  #bg[PRELIGHT] = { 0.75, 3, 1 }
#}
#class 'GtkIconView' style 'iconview'

#""")
        map = self.__icon.get_colormap()

        colour = map.alloc_color("#FFF9E9") # light red

        style = self.__icon.get_style().copy()
        style.base[gtk.STATE_NORMAL] = colour
        self.__icon.set_style(style)


        #self.cellpb = gtk.CellRendererPixbuf()
        #self.cellpb.set_property('cell-background', 'yellow')

        #self.__icon.pack_start(self.cellpb, False)
        #self.__icon.set_attributes(self.cellpb, pixbuf=0)
        self.pack_start(self.scroll, True, True)
        self.scroll.add(self.__icon)
    ### Interface - Public Functions ###

    def set_callback(self, func):

        self.on_select = func
        self.__icon.connect('selection-changed', self.on_select, self.__model, self.__current)
        self.__icon.connect('selection-changed', self.on_select, self.__model, self.__current)


    def add_item(self, name, image, iter=None):
        """
        @param name: str with name of option
        @param image: str with name of image (e.g. sample.svg)
        """

        pixmap_file = os.path.join(self.__pixmap_d, "Preferences" ,image)


        # FIXME: only put the color when is selected
        pixbuf = gtk.gdk.pixbuf_new_from_file (pixmap_file)
        pixbuf2 = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB,0,8,40,40)
        pixbuf2.fill(0xAAEEEEFF)
        pixbuf2.composite(pixbuf,0,0,35,35,0,0,1,1,gtk.gdk.INTERP_NEAREST,50)


        self.__model.insert_before(iter,[name, pixbuf])

        #self.__icon.modify_bg(gtk.STATE_PRELIGHT, gtk.gdk.color_parse("blue"))
    def remove_item(self, name):
        self.__model.remove(name)
    ### Private Functions ####

    def __create_icon_list(self):

        iconView = gtk.IconView ()
        self._icons_list.append(iconView)







"""

TabWidget is a widget similar like tabs of firefox

Depends: cairo

"""
class TabWidget(gtk.HBox):
    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
                     (gobject.TYPE_STRING,))
    }
    def __init__(self):
        """ Construct widget """
        gtk.HBox.__init__(self)
        # Data Struct
        self.__list = TabStruct()


        self.__selected = None

    # Public Interface
    def add_item(self, text, image, image_bw=None):

        """
        Add Item to list
        @param text: its a message of item
        @param image:
        @param image_bw:
        """


        tmpw = IconToggleWidget(text, image, image_bw)
        if self.__list.is_empty():

            tmpw.toggle()
            self.__selected = tmpw
            tmpw.set_enable(True)
        else:
            tmpw.toggle_blackwhite()
        self.__list.add_item(text, image,image_bw,tmpw)
        self.pack_start(tmpw)
        tmpw.connect('toggle', self.__toggle_items)
    def do_realize(self):
        gtk.HBox.do_realize(self)

    def __toggle_items(self, widget, text):
        if self.__selected != widget:
            widget.set_enable(True)
            self.__selected.toggle()
            self.__selected.set_enable(False)
            self.__selected = widget
            self.emit('changed', text)
    def remove_item(self, text):
        """
        Remove Item
        @param text: message of item
        """
        self.__list.del_item(text)

gobject.type_register(TabWidget)
if __name__ == "__main__":
    w = gtk.Window()
    ti = ['Network','../share/pixmaps/umit/Preferences/network.svg',\
          '../share/pixmaps/umit/Preferences/network-bw.svg']
    ti2 = ['General Settings','../share/pixmaps/umit/Preferences/general.svg',\
          '../share/pixmaps/umit/Preferences/genral-bw.svg']

    ti3 = ['Interface','../share/pixmaps/umit/Preferences/expose.svg',\
          '../share/pixmaps/umit/Preferences/expose-bw.svg']

    tw = TabWidget()
    tw.add_item(*ti)
    tw.add_item(*ti2)
    #tw.add_item(*ti3)
    w.add(tw)
    w.show_all()
    gtk.main()
