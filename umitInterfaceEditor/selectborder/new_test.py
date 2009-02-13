#
# Kiwi: a Framework and Enhanced Widgets for Python
#
# Copyright (C) 2005 Async Open Source
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307
# USA
#
# Author(s): Johan Dahlin <jdahlin@async.com.br>
#

"""
A box which you can select and will have a border around it when
you click on any widgets in it
"""
import gobject

MIN_WIDTH = 200
MIN_HEIGHT = 30
background_xpm = [
    # columns rows colors chars-per-pixel
    "8 8 2 1",
    "  c #bbbbbb",
    ". c #0000FF",
    # pixels
    " .  .   ",
    ".    .  ",
    "      ..",
    "      ..",
    ".    .  ",
    " .  .   ",
    "  ..    ",
    "  ..    ",
    ]

SELECTION_NODE_SIZE = 6
BORDER_WIDTH = 3
import gtk
from gtk import gdk

class SelectableBox(object):
    def __init__(self, width=6):
        self._selected = None
        self._draw_gc = None
        self._selection_width = width
        self.unset_flags(gtk.NO_WINDOW)
        self.set_redraw_on_allocate(True)
        self.set_spacing(width)
        self.set_border_width(width)

    # Public API

    def get_selected(self):
        """
        @returns: the currently selected widget
        """

        return self._selected

    def set_selected(self, widget):
        """
        @param widget: widget to select, must be a children of self
        """

        if not widget in self.get_children():
            raise ValueError("widget must be a child of %r" % self)

        old_selected = self._selected
        self._selected = widget
        if old_selected != widget:
            self.queue_draw()

    def pack_start(self, child, expand=True, fill=True, padding=0):
        """
        Identical to gtk.Box.pack_start
        """
        super(SelectableBox, self).pack_start(child, expand=expand,
                                              fill=fill, padding=padding)
        self._child_added(child)

    def pack_end(self, child, expand=True, fill=True, padding=0):
        """
        Identical to gtk.Box.pack_end
        """
        super(SelectableBox, self).pack_end(child, expand=expand,
                                            fill=fill, padding=padding)
        self._child_added(child)

    def add(self, child):
        """
        Identical to gtk.Container.add
        """
        super(SelectableBox, self).add(child)
        self._child_added(child)

    def update_selection(self):
        selected = self._selected
        if not selected:
            return

        border = 1
        x, y, w, h = selected.allocation
        #self.window.draw_rectangle(self._draw_gc, False,
        #                           x - (border / 2), y - (border / 2),
        #                           w + border, h + border)
        gc = self._draw_gc
        #if width > SELECTION_NODE_SIZE and height > SELECTION_NODE_SIZE:
        x = x - (border/2)
        y = y- (border/2)
        height = h 
        width = w 
        gc = self._draw_gc
        window = self.window
        window.draw_rectangle(gc, True, x, y,
                                SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x, y + height -SELECTION_NODE_SIZE,
                                SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE, y,
                                SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE,
                                y + height - SELECTION_NODE_SIZE,
                                SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            
        window.draw_rectangle(gc, False, x, y, width - 1, height - 1)

    # GtkWidget

    def do_realize(self):
        assert not (self.flags() & gtk.NO_WINDOW)
        self.set_flags(self.flags() | gtk.REALIZED)
        self.window = gdk.Window(self.get_parent_window(),
                                 width=self.allocation.width,
                                 height=self.allocation.height,
                                 window_type=gdk.WINDOW_CHILD,
                                 wclass=gdk.INPUT_OUTPUT,
                                 event_mask=(self.get_events() |
                                             gdk.EXPOSURE_MASK |
                                             gdk.BUTTON_PRESS_MASK))
        self.window.set_user_data(self)
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_NORMAL)

        self._draw_gc = gdk.GC(self.window,
                               line_width=self._selection_width,
                               line_style=gdk.SOLID,
                               foreground=self.style.bg[gtk.STATE_SELECTED])

    def do_button_press_event(self, event):
        selected = self._get_child_at_pos(int(event.x), int(event.y))
        if selected:
            self.set_selected(selected)

    # Private

    def _get_child_at_pos(self, x, y):
        """
        @param x: x coordinate
        @type x: integer
        @param y: y coordinate
        @type y: integer
        """
        toplevel = self.get_toplevel()
        for child in self.get_children():
            coords = toplevel.translate_coordinates(child, x, y)
            if not coords:
                continue

            child_x, child_y = coords
            if (0 <= child_x < child.allocation.width and
                0 <= child_y < child.allocation.height and
                child.flags() & (gtk.MAPPED | gtk.VISIBLE)):
                return child

    def _child_added(self, child):
        child.connect('button-press-event',
                      lambda child, e: self.set_selected(child))

class SelectableHBox(SelectableBox, gtk.HBox):
    __gtype_name__ = 'SelectableHBox'

    def __init__(self, width=6):
        gtk.HBox.__init__(self)
        SelectableBox.__init__(self, width=width)

    do_realize = SelectableBox.do_realize
    do_button_press_event = SelectableBox.do_button_press_event

    def do_size_allocate(self, allocation):
        gtk.HBox.do_size_allocate(self, allocation)
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_expose_event(self, event):
        gtk.HBox.do_expose_event(self, event)
        self.update_selection()

class SelectableVBox(SelectableBox, gtk.VBox):
    __gtype_name__ = 'SelectableVBox'

    def __init__(self, width=6):
        gtk.VBox.__init__(self)
        SelectableBox.__init__(self, width=width)

    do_realize = SelectableBox.do_realize
    do_button_press_event = SelectableBox.do_button_press_event

    def do_size_allocate(self, allocation):
        gtk.VBox.do_size_allocate(self, allocation)
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_expose_event(self, event):
        gtk.VBox.do_expose_event(self, event)
        self.update_selection()
        
class BackgroundWidget(gtk.Widget):
    ''' 
    This is a background for editor 
    
    Use a generic widget and it filled with gdk
    
    '''
    
    def __init__(self):
        gtk.Widget.__init__(self)
        #Attributes
        self._pixmap = None
        self._xmp = background_xpm
        #self.unset_flags(gtk.VISIBLE)
        #self.set_flags(self.flags() | gtk.COMPOSITE_CHILD)
        
        self.show()
    def do_realize(self):
        self.set_flags(self.flags() | gtk.REALIZED)
        
        events = (gtk.gdk.EXPOSURE_MASK |
                  gtk.gdk.BUTTON_PRESS_MASK |
                  gtk.gdk.POINTER_MOTION_MASK)
        self.window = gtk.gdk.Window(self.get_parent_window(), 
                                     x=self.allocation.x,
                                     y=self.allocation.y,
                                     width = self.allocation.width,
                                     height = self.allocation.height,
                                     window_type = gtk.gdk.WINDOW_CHILD, 
                                     wclass = gtk.gdk.INPUT_OUTPUT, 
                                     visual=self.get_visual(),
                                     colormap = self.get_colormap(),
                                     event_mask = self.get_events() | events)
        self.window.set_user_data(self)
        self.style.attach(self.window)
        c = self.get_colormap()
        color = c.alloc_color(65000,6500,655)
        self.style.set_background(self.window,3)

        if not self._pixmap:
            temp = gtk.gdk.pixmap_colormap_create_from_xpm_d(None, 
                                                           self.get_colormap(), 
                                                           None,
                                                           self._xmp)
            self._pixmap = temp[0]
        
        self.window.set_back_pixmap(self._pixmap, False)
        
    def do_size_allocate(self, allocation):
        x,y,w,h = allocation
        print w,y,w,h
        allocation = gtk.gdk.Rectangle(x,y,w,h)
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)

    def do_size_request(self, requisition):
        requisition.width = MIN_WIDTH
        requisition.height = MIN_HEIGHT

    def do_expose_event(self, event):
        light_gc = self.style.light_gc[gtk.STATE_NORMAL]
        dark_gc = self.style.dark_gc[gtk.STATE_NORMAL]
        w, h = event.window.get_size()

        # These lines make the Placeholder looks like a button
        event.window.draw_line(light_gc, 0, 0, w - 1, 0)
        event.window.draw_line(light_gc, 0, 0, 0, h - 1)
        event.window.draw_line(dark_gc, 0, h -1, w - 1, h - 1)
        event.window.draw_line(dark_gc, w - 1, 0, w - 1, h - 1)
        return False


    def do_motion_notify_event(self, event):
        
        return False

    def do_button_press_event(self, event):
        light_gc = self.style.light_gc[gtk.STATE_NORMAL]
        dark_gc = self.style.dark_gc[gtk.STATE_NORMAL]
        w, h = event.window.get_size()
        #


        # These lines make the Placeholder looks like a button
        event.window.draw_line(light_gc, 0, 0, w - 1, 0)
        event.window.draw_line(light_gc, 0, 0, 0, h - 1)
        event.window.draw_line(dark_gc, 0, h -1, w - 1, h - 1)
        event.window.draw_line(dark_gc, w - 1, 0, w - 1, h - 1)
        
        x,y,width, height = self.allocation
        border = 5
        gc = gdk.GC(self.window, line_width=3)
        
        window = self.window
        window.draw_rectangle(gc, True, x, y,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x, y + height -SELECTION_NODE_SIZE,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE, y,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
        window.draw_rectangle(gc, True, x + width - SELECTION_NODE_SIZE,
                              y + height - SELECTION_NODE_SIZE,
                              SELECTION_NODE_SIZE, SELECTION_NODE_SIZE)
            
        window.draw_rectangle(gc, False, x, y, width - 1, height - 1)

gobject.type_register(BackgroundWidget)

class WindowSelect:
    def __init__(self):
        
        window = gtk.Window()
        window.set_size_request(600, 300)
        box = gtk.VBox()
        
        window.add(box)

        label = gtk.Label('Label!!!')

        sbox = SelectableVBox()
        #sbox = SelectableVBox()
        button = gtk.CheckButton('Button')

        hbox = gtk.HBox()
        hbox.pack_start(label)
        hbox.pack_start(button)
        cb2=BackgroundWidget()
        ev2 = gtk.EventBox()
        ev2.add(cb2)
        cb3=BackgroundWidget()
        ev3 = gtk.EventBox()
        ev3.add(cb3)
        cb4=BackgroundWidget()
        ev4 = gtk.EventBox()
        ev4.add(cb4)
        button2 = gtk.CheckButton('Button')
        la2= gtk.Label('tres')

        sbox.pack_start(ev2, False, False)
        sbox.pack_start(ev3, False, False)
        sbox.pack_start(ev4, False, False)
        sbox.pack_start(la2)
        sbox.pack_start(button2)
        sbox.pack_start(hbox)
        #button.connect("pressed", move_buttao)
        #button.connect("released", move_widget)
        box.pack_start(sbox,False, False)
        #sbox.do_realize()
        window.show_all()
        gtk.main()

        
    def move_buttao(widget):
        #pass
    
        sbox.remove(button)
        sbox.remove(label)
        #sbox.set_selected(label)
        #sbox.update_selection()
        sbox.add(button) 
        sbox.add(label)
    def move_widget(widget):
        sbox.remove(widget)
        sbox.remove(label)
        sbox.add(label)
        sbox.add(widget)
        
if __name__ == "__main__":
    w = WindowSelect()