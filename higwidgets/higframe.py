# Copyright (C) 2007 TO BE DEFINED
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 
# USA

"""
higwidgets/higframe.py

    hig frame
"""

__all__ = ['HIGFrame']

import gtk

class HIGFrame(gtk.Frame):
    """
    Frame without border with bold label.
    """
    def __init__(self, label=None):
        gtk.Frame.__init__(self)
        
        self.set_shadow_type(gtk.SHADOW_NONE)
        self._flabel = gtk.Label()
        self._set_label(label)
        self.set_label_widget(self._flabel)

    def _set_label(self, label):
        self._flabel.set_markup("<b>%s</b>" % label)

# Demo
if __name__ == "__main__":
    w = gtk.Window()
    box = gtk.VBox()
    box.set_border_width(12)
    f = HIGFrame()
    f._set_label("Nice")
    box1 = gtk.VBox()
    box2 = gtk.HBox()
    box2.pack_start(gtk.Label("cool"), False, False, 0)
    box3 = gtk.HBox()
    box3.pack_start(gtk.Label("!!!!"), False, False, 0)
    box1.add(box2)
    box1.add(box3)
    box.pack_start(box1, False, False, 0)
    f.add(box)
    w.connect('destroy', lambda d: gtk.main_quit())
    w.add(f)
    w.show_all()
    gtk.main()
