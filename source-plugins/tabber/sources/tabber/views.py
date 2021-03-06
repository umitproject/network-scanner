import gtk, gobject

class UmitViewWidget(gtk.VBox):

    __gtype_name__ = 'UmitViewWidget'
    __gproperties__ = {
        'title-text' : (gobject.TYPE_STRING, 'title-text', 'Title', \
                        'Untitled Pida View', gobject.PARAM_READWRITE)
    }
    __gsinals__ = {
        'close-clicked'  : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ()),
        'detach-clicked' : (gobject.SIGNAL_RUN_LAST, gobject.TYPE_NONE, ())
    }

    def __init__(self):
        gtk.VBox.__init__(self)
        self._child = None
        self._create_ui()

    def _create_ui(self):
        self._create_top_bar()
        self._create_widget_holder()

    def _create_top_bar(self):
        self._top_bar = gtk.HBox()
        self.pack_start(self._top_bar, expand=False)
        self._title_label = gtk.Label()
        self._top_bar.pack_start(self._title_label)
        self._top_buttons = gtk.HBox()
        self._top_bar.pack_start(self._top_buttons, expand=False)
        self._detach_button = gtk.ToolButton(icon_widget=self._create_detach_button())
        self._top_buttons.pack_start(self._detach_button)
        self._close_button = gtk.ToolButton(icon_widget=self._create_close_button())
        self._top_buttons.pack_start(self._close_button)

    def _create_widget_holder(self):
        self._widget_holder = gtk.Frame()
        self.pack_start(self._widget_holder)

    def _create_close_button(self):
        im = gtk.Image()
        im.set_from_file(get_pixmap_path('view_close.gif'))
        return im

    def _create_detach_button(self):
        im = gtk.Image()
        im.set_from_file(get_pixmap_path('view_detach.gif'))
        return im

    def prop_set_title_text(self, val):
        if val is not None:
            self._title_label.set_text(val)

    def add_main_widget(self, child):
        self._widget_holder.add(child)
        self._child = child

    def remove_main_widget(self):
        self._widget_holder.remove(self._child)

    def get_main_widget(self):
        return self._child

    def do_add(self, widget):
        self.add_main_widget(widget)


class UmitViewMixin(object):

    icon_name = gtk.STOCK_INFO
    label_text = 'Umit View'

    def __init__(self, toplevel=None):
        self._toplevel = toplevel

    def create_ui(self):
        """Create the user interface here"""

    def get_unique_id(self):
        return self._uid

    def create_tab_label_icon(self):
        return gtk.image_new_from_stock(self.icon_name, gtk.ICON_SIZE_MENU)

    def get_tab_label_text(self):
        return self.label_text

    def get_parent_window(self):
        return self.get_toplevel().get_parent_window()

    def get_toplevel(self):
        return self._main_widget

    parent_window = property(get_parent_window)

    def on_remove_attempt(self, pane):
        return not self.can_be_closed()

    def can_be_closed(self):
        return False


class UmitView(UmitViewMixin):

    def __init__(self, title=None, icon=None, *args, **kw):
        UmitViewMixin.__init__(self, *args, **kw)

        self._main_widget = gtk.VBox()
        self.label_text = title or self.label_text
        self.icon_name = icon or self.icon_name
        self.create_ui()

    def add_main_widget(self, widget, *args, **kw):
        self._main_widget.pack_start(widget, *args, **kw)

    def get_main_widget(self):
        return self._main_widget
