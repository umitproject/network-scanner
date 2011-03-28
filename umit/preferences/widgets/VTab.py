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
import math


from higwidgets.higcairodesign import cr_rectangule_curve



"""

ScrolledTab is a widget similar like tabs of Skype @ Windows

Depends: cairo


THANKS to: Marcelo Lira 

"""

class IconScroller(gtk.EventBox):
    """
    It's a toggle button that no use gtk.STATE_SELECTED/NORMAL
    because it's cause some troubles in Mac OSX 
    It's a try to make a simulation gtk.STATE_SELECTED
    
    
    Note: following gtk+ engine team gtk.Style and gtk.gdk.Window 
    is old schoo api (Thanks dx for information)
    """

    __gsignals__ = {
        'changed':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     (gobject.TYPE_INT, )),
        'close':  (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE,
                     ()),
    }

    
    def __init__(self, name, image, items = None ):
        gtk.EventBox.__init__(self)
        self.add_events(self.get_events() | gtk.gdk.BUTTON_MOTION_MASK|\
                        gtk.gdk.ENTER_NOTIFY_MASK |\
                        gtk.gdk.LEAVE_NOTIFY_MASK |\
                        gtk.gdk.BUTTON_MOTION_MASK|\
                        gtk.gdk.POINTER_MOTION_MASK )
        
        #self.connect('motion-notify-event', self._mouse_move)
        self.item_list = [] 
        self.items = items
        self.vbox = gtk.VBox()
        self.hbox = gtk.HBox()
        self.__handler_id = self.connect("expose-event", self.cb)
        label = gtk.Label('<b>%s</b>' % name)
        label.set_use_markup(True)
        self.label = label 
        self.image = gtk.Image()
        tmp_box = gtk.VBox()
        tmp_box.pack_start(self.image, False, True, 6) # Temporary Pack Image
        tmp_box.set_border_width(2)
        self.image.set_from_file(image)
        self.hbox.pack_start(tmp_box, False, True, 6) # Pack Image
        self.hbox.pack_start(label, False, False, 6)
        self.vbox.pack_start(self.hbox, False, False)
        self.add(self.vbox)
        self.__enable = True 
        self.__name = name
        self.__toggle = True
        
        
        self.expanded = False
        
        # -1 means something like None. it's y coord
        self.over = -1 
        
        self.background_color = [0,0,0,1]
        
        self.__size = None 
        self.__items = 0
        self.__ibox = gtk.VBox()
        self.vbox.pack_start(self.__ibox, True, True)
        
        
        #####################################
        # Append items 
        if items!=None:
            for item in items:
                if item.has_key('image'):
                    i = item['image']
                else:
                    i = None 
                self.append_item(item['name'], i)
        
    def cb(self, w,e):
        """ Hide items - first time """
        self.disconnect(self.__handler_id)

    def append_item(self, name, image):
        """ 
        Append item (when icon open)
        """
        hbox = gtk.HBox()
        hbox.set_border_width(4)
        
        label = gtk.Label('<b>%s</b>' % name)
        label.set_use_markup(True)
        img = gtk.Image()
        
        hbox.pack_start(img, False, False)
        hbox.pack_start(label, False, False)

        if image!= None:
            img.set_from_file('%s' % image) 
            hbox.set_spacing(10)
        else:
            
            hbox.set_spacing(26)
            
        
        self.__ibox.pack_start(hbox,True, True)
        hbox.hide_all()
        label.hide_all()
        img.hide_all()
        
        self.item_list.append({'name': name, 
                               'image':image, 
                               'label':label, 
                               'img':img,
                               'box': hbox})
        
        self.__items = self.__items + 1 
    
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
        
        cr_rectangule_curve(cr, 0,0,width, height, 20)
        color = gtk.gdk.Color(int(math.pow(2, 16) * 250 / 255), \
                              int(math.pow(2,16) * 250 / 255), \
                              int(math.pow(2,16) * 220 / 255), \
                              0)
        
        state = gtk.STATE_NORMAL
        color = self.get_style().base[state]
        # Parse colors
        cr.set_source_color(color)

        cr.fill()
        #cr.set_source_rgba(210/255.0,230/255.0,110/250.0,1)
        
        state = gtk.STATE_SELECTED
        color = self.get_style().base[state]
        cr.set_source_color(color)
        cr_rectangule_curve(cr, 0, 0, width, height, 20)
        cr.stroke()

        
        # Mouse over - event
        # dont show rectangle in tab title
        if self.__size!=None and self.over>= 33 :
            
            # Get sizes 
            alloc = self.allocation 
            width = alloc.width
            heig = self.__size[1]
            
            h = heig*self.number_item(self.over)
            cr_rectangule_curve(cr, 0, h, width, heig, 20)
            state = gtk.STATE_SELECTED
            color = self.get_style().base[state]
            # Parse colors
            cr.set_source_color(color)
    
            cr.fill()    
    def _mouse_over(self, event):
        """
        Mouse over
        """
        self.over = event.y
    
        
        
        
    def do_size_allocate(self, allocation):
        '''Resizes the window'''
        gtk.EventBox.do_size_allocate(self, allocation)
        
        self.allocation = allocation

        
        if self.flags() & gtk.REALIZED:
            self.window.move_resize(*allocation)
            
    def close(self):
        if self.expanded:
            print("close")
            self.expand()
            
    def expand(self):
        self.set_size_request(-1, 28)
        x = self.get_size_request()

        if not self.expanded:
            # close opened tabs
            self.emit('close')
            # FIXME
            self.__size = self.get_size_request()
            if x[1] >=(self.__items+1)*self.__size[1]:
                return 
            gobject.timeout_add(10, self._animate_show)
            self.queue_draw()
            self.__enable = not self.__enable
            
        else:
            gobject.timeout_add(10, self._animate_hide)
            self.queue_draw()
            self.__enable = not self.__enable
        
        self.expanded= not self.expanded  
        
    def _animate_show(self):
        x = self.get_size_request()
        if x[1] >(self.__items+1)*self.__size[1]:
            return 
        h_resize = x[1]+self.__size[1]/5
        if h_resize> (self.__items+1)*self.__size[1]:
            h_resize = (self.__items+1)*self.__size[1]
        self.set_size_request(x[0], h_resize)
        if x[1]+self.__size[1]/5 < self.__size[1] * (self.__items+1) :
            return True
        else:
            return False

    def _animate_hide(self):
        x = self.get_size_request()

        self.set_size_request(x[0], x[1]-self.__size[1]/5)
        if x[1]-self.__size[1]/5 > self.__size[1] :
            return True
        else:
            self.set_size_request(x[0], 33)
            return False

    def do_expose_event(self, event):
        """
        Render widget
        """
        gtk.EventBox.do_expose_event(self, event)
        self.draw(self.__enable)
        self.propagate_expose(self.vbox, event)
    def do_button_press_event(self, event):
        """
        Enable / Disable label - change color 
        """
        if event.type == 5:
            return 
        if (not self.expanded or ( self.__size != None \
           and self.__size[1] > event.y)) and self.items!=None:
            self.expand()
        for i in self.item_list:
            if self.expanded:
                i['box'].show_all()
            else:
                i['box'].hide_all()
        self.queue_draw()
        self.emit('changed', self.number_item(event.y))
        
    def do_button_release_event(self, event):
        if self.expanded:
            return 
    def do_leave_notify_event(self, event):
        """ 
        Leave notify: put old colour 
        """
        self.draw(self.__enable)
        self.over = -1 
        self.queue_draw()
        
    def do_motion_notify_event(self, event):
        if not self.expanded or ( self.__size != None \
           and self.__size[1] > event.y):
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        else:
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
            
        self._mouse_over(event)
        self.queue_draw()
    def do_enter_notify_event(self, event):
        
        """
        Enter notify event: when activate change colour and change over text
        """
        self.draw(self.__enable)

        if not self.expanded or ( self.__size != None \
           and self.__size[1] > event.y):
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.HAND2))
        else:
            self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
        self.queue_draw()
    def get_name(self):
        return self.__name
    
    def number_item(self, y):
        if self.__size==None:
            return 0 
        return int(y/self.__size[1]) 
        
    
gobject.type_register(IconScroller)


#def main():
    #w = gtk.Window()
    ##vbox = box()
    #vbox = gtk.VBox()
    #w.add(vbox)
    #t1 = IconScroller(w, 'l')
    #t2 = IconScroller(w, 'l')
    #t1.set_size_request(100,24)
    #t2.set_size_request(100,24)
    #vbox.pack_start(t1)
    #vbox.pack_start(t2)
    #vbox.set_border_width(20)
    #vbox.set_spacing(10)
    #w.show_all()
    #gtk.main()

#if __name__=="__main__":
    #main()

