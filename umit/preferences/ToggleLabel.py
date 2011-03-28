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


import gtk
import gobject


class ToggleLabelCr(gtk.EventBox):
    """
    It's a toggle button that no use gtk.STATE_SELECTED/NORMAL
    because it's cause some troubles in Mac OSX
    It's a try to make a simulation gtk.STATE_SELECTED


    Note: following gtk+ engine team gtk.Style and gtk.gdk.Window
    is old schoo api (Thanks dx for information)
    """

    __gsignals__ = {
        'toggled':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     (gobject.TYPE_STRING, )),
    }


    def __init__(self, parent, name):
        gtk.EventBox.__init__(self)
        self.add_events(self.get_events() | gtk.gdk.BUTTON_MOTION_MASK|\
                        gtk.gdk.ENTER_NOTIFY_MASK | gtk.gdk.LEAVE_NOTIFY_MASK  )
        self.__enable = True
        self.__p = parent
        self.__name = name
        self.__toggle = True
        self.background_color = [0,0,0,1]

    def do_realize(self):
        """ build window """
        gtk.EventBox.do_realize(self)
        self.set_flags(self.flags() | gtk.REALIZED)
        #self.draw(self.__enable)


    def draw(self, selected):
        """
        Draw label selected or normal
        @param selected: bool if selected or not changed draw color

        """

        # Create window
        cr = self.window.cairo_create()

        # Get sizes
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width
        #cr.set_source_rgba(*self.background_color)

        #cr_rectangule_curve(cr, 0,0,width, height, 20)
        if selected:
            state = gtk.STATE_SELECTED
        else:
            state = gtk.STATE_INSENSITIVE # gtk.STATE_ACTIVE
        color = self.get_style().base[state]
        # Parse colors
        cr.set_source_color(self.get_style().base[state])

        cr.rectangle(0, 0, width, height)
        cr.fill()
        cr.stroke()
        #print "width = %d, heigth = %d " % (width, height)

    def do_size_allocate(self, allocation):
        '''Resizes the window'''
        gtk.EventBox.do_size_allocate(self, allocation)
        self.allocation = allocation
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
    def do_expose_event(self, event):
        """
        Render widget
        """

        gtk.EventBox.do_expose_event(self, event)
        self.draw(self.__enable)
    def do_button_press_event(self, event):
        """
        Enable / Disable label - change color
        """
        self.emit('toggled',self.__name)
        if not self.__toggle:
            return
        self.__enable = not self.__enable
        self.draw(self.__enable)

    def do_leave_notify_event(self, event):
        """
        Leave notify: put old colour
        """
        self.draw(self.__enable)
    def do_enter_notify_event(self, event):

        """
        Enter notify event: when activate change colour and change over text
        """

        ### Change text

        self.__p.set_text(self.__name)

        ### Change color
        # Create window
        cr = self.window.cairo_create()

        # Get sizes
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width
        #cr.set_source_rgba(*self.background_color)
        cr.rectangle(0, 0, width, height)
        #cr_rectangule_curve(cr, 0,0, width, height, 20)
        cr.set_source_rgba(0.3,0.3,0.3,1)
        cr.fill()
        cr.stroke()

    def set_toggle(self, toggle = True):
        self.__toggle = toggle
    def get_active(self):
        return self.__enable
    def set_active(self, active):
        #self.draw(active)
        self.__enable = active
        self.queue_draw()
    def get_name(self):
        return self.__name

gobject.type_register(ToggleLabelCr)



class PreviewLabel(gtk.Widget):
    """
    It's a label without text, it's like toggle button
    when you press he was go down, or go up
    """

    # Override signals
    __gsignals__ = { 'size_request' : 'override', 'expose-event' : 'override' }



    def __init__(self, parent, text):
        """
        @param parent: it's the container of PreviewLabel with goal change label
        @param text: text to change on enter notify motion
        """
        gtk.Widget.__init__(self)
        self.__enable = True
        self.__p = parent
        self.__text = text
    def do_size_request(self, request):
        self.allocation.width = request.width
        print "request"
    def do_size_allocate(self, allocation):
        '''Resizes the window'''
        print "size allocate"
        self.allocation = allocation

        allocation.width = self.get_parent().allocation.width
        self.allocation.width = self.get_parent().allocation.width
        if self.flags() & gtk.REALIZED and self.window != None:
            self.window.move_resize(*allocation)
            print allocation.width, allocation.height

    def do_realize(self):
        """
        Build widget
        """
        # Add flag by event - REALIZED
        self.set_flags(self.flags() | gtk.REALIZED)
        self.draw_window()

    def draw_window(self):
        # Create window design of Widget

        self.window = gtk.gdk.Window(
            self.get_parent_window(),
            x=self.allocation.x,
            y=self.allocation.y,
            width=self.allocation.width,
            height=self.allocation.height,
            window_type=gtk.gdk.WINDOW_CHILD,
            wclass=gtk.gdk.INPUT_OUTPUT,
            event_mask=(self.get_events() | gtk.gdk.EXPOSURE_MASK |\
            gtk.gdk.BUTTON_PRESS_MASK | gtk.gdk.ENTER_NOTIFY_MASK))


        self.window.set_user_data(self)

        # Define background colour
        self.style.attach(self.window)
        self.style.set_background(self.window, gtk.STATE_SELECTED)

        print "realize"

    def do_button_press_event(self, event):
        if self.__enable:
            state = gtk.STATE_NORMAL
        else:
            state = gtk.STATE_SELECTED

        self.style.set_background(self.window, state)

        self.style.paint_box(self.window, state,
            gtk.SHADOW_ETCHED_IN, None, self, '', 0, 0,
            self.get_parent().allocation.width, self.allocation.height)
        print self.allocation.width
        self.__enable = not self.__enable
        print "button pressed"
        #self.queue_draw()
    def do_enter_notify_event(self, event):
        self.__p.set_text(self.__text)
    def do_unrealize(self):
        if self.window == None:
            return
        self.window.set_user_data(None)
        self.window.destroy()
        print "unrealized"
    def do_expose_event(self, event):
        """
        Render
        """
        print "expose event"
        #self.style.paint_box(self.window, gtk.STATE_SELECTED,
            #gtk.SHADOW_ETCHED_IN, event.area, self, '', 0, 0,
            #self.allocation.width, self.allocation.height)


gobject.type_register(PreviewLabel)
