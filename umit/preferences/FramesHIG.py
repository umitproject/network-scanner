import gtk
from higwidgets.higframe import HIGFrame
from higwidgets.higboxes import HIGVBox, HIGHBox

class TabFrame(HIGFrame):
    """
    Each frame extends TabFrame should have contents of section
    """
    def __init__(self, name):
        HIGFrame.__init__(self,name)
        self.set_shadow_type(gtk.SHADOW_IN)

class TabBox(gtk.ScrolledWindow):
    """
    it's a page of TabsWidget
    """
    def __init__(self, name):
        gtk.ScrolledWindow.__init__(self)
        self.frame = TabFrame(name)
        self.frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        self.__main_box = HIGVBox()
        self.frame.add(self.__main_box)
        self._create_widgets()
        self.viewport = gtk.Viewport()
        self.viewport.add(self.frame)
        self.add(self.viewport)
        self.viewport.set_shadow_type(gtk.SHADOW_NONE)
        self.props.shadow_type = gtk.SHADOW_NONE
        self.__main_box.set_border_width(6)
        self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    def _create_widgets(self):
        """ Overwrite me, it's subclass """
    # Box Interface
    def pack_start(self, *args):
        self.__main_box.pack_start(*args)

    def pack_end(self, *args):
        self.__main_box.pack_end(*args)
    def destroy(self):
        pass
