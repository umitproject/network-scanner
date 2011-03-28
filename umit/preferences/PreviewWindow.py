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
PreviewWindow
"""
import gtk
import gobject
import cairo
import pango

from umit.core.UmitLogging import log
from umit.core.I18N import _


from higwidgets.higboxes import HIGHBox

from math import pi


from higwidgets.higcairodesign import cr_rectangule_curve

from umit.preferences.ToggleLabel import ToggleLabelCr



"""
Its Umit Preview Window

What have Umit?

- Menu
- Toolbar
- ScanNotebook
    - List Ports
    - Nmap Results

How is it exposed?

Show / Hide
- Hide ToolBar
- Hide ListPorts
1- Hide Nmap Results

"""



class PreviewWindow(gtk.EventBox):
    __gtype_name__ = "PreviewWindow"
    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     (gobject.TYPE_STRING,object)),
    }

    def __init__(self):
        """ Constructor of Preview Widget """
        gtk.EventBox.__init__(self)
        self.__text_color = True
        self.add_events(self.get_events() | gtk.gdk.BUTTON_MOTION_MASK)
        #self.set_border_width(3)
        self.__box = gtk.VBox()
        self.l1 = None
        self.__text = ""
        self.__toggle_list = []
        self.__realized = 0
        self._create_toggle_widgets()
    def draw_umit_preview(self,event):
        """
        Draw mainly strucure of Umit
        """

        # Create window to draw
        cr = self.window.cairo_create()
        # Get sizes and allocate
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        height = height-height/10
        width = alloc.width

        ####################### FILL ##################################
        # Rectangule Curver
        cr.set_source_rgb(0.0, 0,1)
        cr_rectangule_curve(cr, 0, 0, width, self.allocation.height, 25)
        cr.fill_preserve()

        cr.set_source_rgba(0.1, 0.1, 0.9, 0.5)



        # Menu
        cr.rectangle(15, 15, width-15, height/9.0)
        cr.set_source_rgba(0.8,0.8,0.8,0.8)
        cr.fill()

        # Toolbar
        cr.rectangle(0, height/10.0, width, height/7.0)
        cr.set_source_rgba(0.1,0.5,0.3,0.5)
        cr.fill()

        # ScanNotebook
        cr.rectangle(0, height/7.0+height/9.0, width, \
                     height-(height/7.0+height/9.0))
        cr.set_source_rgba(0.5,0.8,0.1,0.4)
        cr.fill()

        ######################### LINES ###################################

        # Define line colours
        cr.set_source_rgb(0.0, 0.0,0.0)

        #### UP ########

        # First horizontal line
        cr.move_to(10, height/10.0)
        cr.rel_line_to(width-20, 0)

        # Second horizontal line
        #cr.move_to(0, height/7.0+height/9.0)
        #cr.rel_line_to(width, 0)

        ### DOWN - Scan Notebook ####

        # Left vertical line

        w_tmp = width/20.0
        h_tmp_up = height/9.0+(height/9.5)*2
        h_tmp_down = height-height/30
        cr.move_to(w_tmp, h_tmp_up)
        cr.line_to(w_tmp, h_tmp_down)

        # Right vertical line
        w_tmp_right = width-width/20.0
        cr.move_to(w_tmp_right, h_tmp_up)
        cr.line_to(w_tmp_right, h_tmp_down)


        # Down horizontal line
        h_tmp = height-height/9.7
        cr.move_to(w_tmp, h_tmp_down)
        cr.line_to(w_tmp_right, h_tmp_down)

        # Up horizontal line
        cr.move_to(w_tmp, h_tmp_up)
        cr.line_to(w_tmp_right, h_tmp_up)

        #### Notebook's label ####

        # Left vertical line
        cr.move_to(w_tmp+width/30, h_tmp_up-height/25)
        cr.line_to(w_tmp+width/30, h_tmp_up)

        # Right vertical line
        cr.move_to(w_tmp+width/7, h_tmp_up-height/25)
        cr.line_to(w_tmp+width/7, h_tmp_up)

        # Up Horizontal line
        cr.move_to(w_tmp+width/30, h_tmp_up-height/25)
        cr.line_to(w_tmp+width/7, h_tmp_up-height/25)

        cr.stroke()





        self.draw_text(cr,w_tmp, h_tmp_down, width, height)

        #cr.set_source_rgb(1.0, 0.0, 0.0)
        #radius = min(width, height)
        #cr.arc(width / 2.0, height / 2.0, radius / 2.0 - 20, 0, 2 * pi)
        #cr.stroke()
        #cr.arc(width / 2.0, height / 2.0, radius / 3.0 - 10, 0, 2 * pi )
        #cr.stroke()



    def set_text(self, text):
        """ Set label text on enter notify motion """
        self.__text = text

    def change_color(self, cr,result=True):
        w = self.__w
        h = self.__h
        try:
            cr.rectangle(0, h-h/40, w, h)
            cr.set_source_rgb(0.8,0.8,0.8)
            cr.fill()
            cr.move_to(w/2-w/4, h-h/30)
            self.__text_color = not self.__text_color
            if (self.__text_color):
                cr.set_source_rgb(0,0.3,1)
            else:
                cr.set_source_rgb(0.3,0.3,0.3)
            self._layout.set_text(self.__text)
            cr.show_layout(self._layout)
            return result
        except cairo.Error, e:
            return False


    def draw_text(self, cr, w_tmp, h_tmp_down, width, height):
        ############# Text ##################

        cr.set_source_rgba(0,0.3,1,0.5)


        cr.move_to(w_tmp+width/30, h_tmp_down+height/30)
        self._layout = self.create_pango_layout(self.__text)
        self._layout.set_font_description(pango.FontDescription(\
            "Sans Serif 16"))
        cr.update_layout(self._layout)
        cr.show_layout(self._layout)
        self.__h = height+10
        self.__w = width
        self.change_color(cr, False)

        gobject.timeout_add(100, self.change_color, cr)


    def press_toolbar(self):
        """
        Verify if toolbar was pressed
        """

        # Get sizes and allocate
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width

    def press_nmap_results(self):
        """
        Verify if nmap results was pressed
        """
        # Get sizes and allocate
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width
    def do_enter_notify_event(self, event):
        #print "enter over x=%d y=%d" % (event.x, event.y)
        pass
    def do_leave_notify_event(self, event):
        #print "leave over x=%d y=%d" % (event.x, event.y)
        pass

    def do_button_press_event(self, event):
        cr = self.window.cairo_create()
        # Get sizes and allocate
        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width


        # Menu
        #cr.rectangle(0, 0, width, height/9)
        #cr.set_source_rgba(0.5,0.5,0.3,0.5)
        #cr.fill()

    def do_expose_event(self, event):
        """
        Render widget
        """
        gtk.EventBox.do_expose_event(self, event)
        self.draw_umit_preview(event)

        # It's to show after change window
        # allocations size is to fix expose recursion loop
        #print "\[\033[1;31m\] EXPOSURE WIDTH \[\033[0m\]"
        #print self.allocation.width-3
        width= self.allocation.width
        self.l1.set_size_request(self.allocation.width-20, \
                               (self.allocation.height/13)-1)
        self.l2.set_size_request(self.allocation.width-20,\
                               (self.allocation.height/9)-1)
        self.l3.set_size_request(self.allocation.width/4,\
                               (self.allocation.height/2)-1)
        self.l4.set_size_request(self.allocation.width/2-1,\
                               (self.allocation.height/2)-1)

        #Expose after REALIZE - ToggleButtonCr Notebook
        if self.__realized==gtk.REALIZED:
            self.__realized = 0
            self.__cont3.set_padding(width/10,width/20,width/10,0)
            self.__cont4.set_padding(width/10,width/20,1,width/20)
        #print "expose previewwindow"


        def do_size_request(self, request):
            gtk.EventBox.do_size_request(request)

    def _create_toggle_widgets(self):
        pass

        self.l1 = ToggleLabelCr(self, _("Menubar"))
        self.l2 = ToggleLabelCr(self, _("Toolbar"))
        self.l3 = ToggleLabelCr(self, _("Services/Hosts"))
        self.l4 = ToggleLabelCr(self, _("Scan Details"))


    def do_realize(self):
        """
        Build window of widget/create widget
        """

        gtk.EventBox.do_realize(self)
        self.add_events(self.get_events() | gtk.REALIZED)
        self.__realized = gtk.REALIZED
        #print "\[\033[1;32m\] DO_REALIZE - PREVIEW WINDOW \[\033[0m\]"
        #self.draw_umit_preview(None)

        self.add(self.__box)

        alloc = self.allocation
        x = alloc.x
        y = alloc.y
        height = alloc.height
        width = alloc.width

        self.__cont1 = gtk.Alignment(0,0, 0, 0)
        self.__cont2 = gtk.Alignment(0,0, 0, 0)
        self.__cont3 = gtk.Alignment(0,0, 0, 0)
        self.__cont4 = gtk.Alignment(0,0, 0, 0)

        self.__cont1.set_padding(3,0,10,5)
        self.__cont2.set_padding(5,0,10,5)



        self.__toggle_list.append(self.l1)
        self.l1.set_size_request(width, height/10)
        self.l1.set_toggle(False)


        self.__toggle_list.append(self.l2)
        self.l2.set_size_request(width,height/10)



        self.__toggle_list.append(self.l3)
        self.l3.set_size_request(width/4, height/5)


        self.__toggle_list.append(self.l4)
        #self.__l4.set_size_request(width/4, height/5)

        self.__cont1.add(self.l1)
        self.__cont2.add(self.l2)
        self.__cont3.add(self.l3)
        self.__cont4.add(self.l4)

        self.__notebook_box = HIGHBox()
        self.__notebook_box.pack_start(self.__cont3, False, True)
        self.__notebook_box.pack_start(self.__cont4, False, True)
        self.__box.pack_start(self.__cont1, False, True)
        self.__box.pack_start(self.__cont2,False, True)
        self.__box.pack_start(self.__notebook_box, False, True)

        self.__box.show_all()

    def do_unrealize(self):
        self.remove(self.__box)
        self.__cont1.remove(self.l1)
        self.__cont2.remove(self.l2)
        self.__cont3.remove(self.l3)
        self.__cont4.remove(self.l4)

    def do_size_allocate(self, allocation):
        '''Resizes the window'''
        gtk.EventBox.do_size_allocate(self, allocation)
        self.allocation = allocation
        #if self.flags() & gtk.REALIZED:
        #    self.window.move_resize(*allocation)
            #print "allocation preview window!"

            #self.l1.set_size_request(self.allocation.width, \
            #                           self.allocation.height/10)
            #self.__l2.set_size_request(self.allocation.width,\
            #                           self.allocation.height/10)
    def toggle_cb(self, widget, str):
        """
        Overwrite function
        """
        pass






# Testing - develpment

#if __name__ == "__main__":
    #w = gtk.Window()

    #s = PreviewWindow()
    #s.set_size_request(300,300)
    #p = PreviewLabel(s, 'lol')
    #aa = ToggleLabelCr(w, 'lol')
    #aa.show_all()
    #w.add(aa)
    #w.show_all()
    #gtk.main()
