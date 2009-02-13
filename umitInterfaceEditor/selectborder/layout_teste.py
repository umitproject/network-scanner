import gtk 
import gobject
from gtk import gdk
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
class SelectableBox(object):
    def __init__(self, width=1):
        self._selected = None
        self._draw_gc = None
        self._selection_width = width
        self.unset_flags(gtk.NO_WINDOW)
        self.set_redraw_on_allocate(True)
        self.set_spacing(12)
        self.set_border_width(12)

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

        border = self._selection_width
        x, y, w, h = selected.allocation
        
        self.window.draw_rectangle(self._draw_gc, False,
                                   x - (border / 2), y - (border / 2),
                                   w + border, h + border)
        self.draw_nodes(x,y,w,h)
        
    # GtkWidget
    def draw_nodes(self, x, y, width, height):
        window = self.window
        gc = self._draw_gc

        if width > SELECTION_NODE_SIZE and height > SELECTION_NODE_SIZE:
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
        c = self.get_colormap()
        color = c.alloc_color(1,1,1)
        self._draw_gc = gdk.GC(self.window,
                               line_width=self._selection_width,
                               line_style=gdk.SOLID,
                               #foreground=self.style.bg[gtk.STATE_PRELIGHT])
                               foreground=color)

        
    def do_button_press_event(self, event):
        selected = self._get_child_at_pos(int(event.x), int(event.y))
        if selected:
            self.set_selected(selected)
            print event.x 
            print event.y
        
            

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

    def __init__(self, width=1):
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

    def __init__(self, width=1):
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



class WindowSelect:
    def __init__(self):
        
        window = gtk.Window()
        window.set_size_request(600, 300)
        box = gtk.VBox()
        
        window.add(box)

        label = gtk.Label('Label!!!')
        sbox = SelectableVBox()
        #sbox = SelectableVBox()
        button = gtk.Button('Button')

        hbox = gtk.HBox()
        hbox.pack_start(label)
        hbox.pack_start(button)
        from Border import BackgroundWidget
        cb2=BackgroundWidget()
        cb2.set_size_request(100,200)
        la2= gtk.Label('tres')
        sbox.pack_start(cb2, True, True)
        sbox.add(la2)
        sbox.add(hbox)

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





class gdkteste:
    def __init__(self):
        window = gtk.Window()
        label = gtk.Label('set')
        wgdk = gdk.Window(window.get_parent_window(),
                          100, 200, gdk.WINDOW_CHILD,gdk.INPUT_OUTPUT,
                          window.get_events() | gdk.EXPOSURE_MASK)
        wgdk.set_user_data(window)
        box = SelectableHBox()
        box.pack_end(wgdk)
        window.add(box)

        window.show()
        gtk.main()

if __name__=="__main__":
    w = WindowSelect()
    #w = gdkteste()
    


