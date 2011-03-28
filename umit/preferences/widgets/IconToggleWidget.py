


import gtk
import cairo
import gobject

"""
Icon contains: text + image 
"""
class IconToggleWidget(gtk.EventBox):
    __gsignals__ = {
	'toggle':  (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
		     (gobject.TYPE_STRING,))
    }

    def __init__(self, text, image, image_bw):
        """
        Constructor
        """
        gtk.EventBox.__init__(self)
	self._text = text 
        self._label = gtk.Label("<b>"+text+"</b>")
	self._label.set_use_markup(True)
        self.active = False 
        self._image = gtk.Image()
	self._img = image
	self._img_bw = image_bw
        self._image.set_from_file(image)
        self.vbox = gtk.VBox()
        self.vbox.pack_end(self._label)
        self.vbox.pack_start(self._image)
        self.add(self.vbox)
	self.vbox.show_all()
	
	# Enable / Disable 
	self.__enable = False 
	
	# Static colors

	self.__color_unselected = [float(255/255.0), float(255/255.0), \
				   float(255/255.0), 1]
	self.__color_selected = [float(255/255.0),float(223/255.0),\
				 float(109/255.0),0.5]
	self.__color_on = self.__color_unselected
	
    def do_realize(self):
        gtk.EventBox.do_realize(self)
        self.add_events( gtk.gdk.MOTION_NOTIFY | \
			 gtk.gdk.BUTTON_PRESS )
	
    def draw_select_bg(self, x,y,w,h, cr,color):
	"""
	draw without change contents
	@param x coordenate x axis
	@param y coordenate y axis
	@param w width bg
	@param h height bg
	@param cr gtk.gdk.CairoContext - cairo window
	@param color tupple color
	"""
	cr.set_source_rgba(*color)
	cr.rectangle(0,0,w, h)
	cr.fill_preserve()
	cr.stroke()
	
    def toggle_blackwhite(self):
	""" 
	change black white mode
	"""
	self._image.set_from_file(self._img_bw)
	    
	
    def toggle(self):
		
	if self.active == True:
	    self._image.set_from_file(self._img_bw)
	else:
	    self._image.set_from_file(self._img)
	
	self.active = not self.active
	
	if self.__color_on == self.__color_selected:
	    self.__color_on = self.__color_unselected
	else:
	    self.__color_on = self.__color_selected
	
	self.queue_draw()
    def __toggle(self):
	self.toggle()
	self.emit('toggle', self._text)
    def set_enable(self, bool):
	self.__enable = bool
    def is_enable(self):
	return self.__enable
    def do_expose_event(self, event):
	gtk.EventBox.do_expose_event(self, event)
	cr = self.window.cairo_create()
	alloc = self.allocation
	self.draw_select_bg(alloc.x, alloc.y, alloc.width, alloc.height, cr,\
			    self.__color_on)
	self.propagate_expose(self.vbox, event)
	
    
    def do_size_allocate(self, alloc):
	gtk.EventBox.do_size_allocate(self, alloc)
    def do_button_press_event(self, event):
	
	# if isn't selected do toggle
	if not self.__enable:
	    self.__toggle()
        
    def do_motion_notify_event(self, event):
	pass
    # No overwrite public functions yet

gobject.type_register(IconToggleWidget)


