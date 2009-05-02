# vim: set encoding=utf-8 :

# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: João Paulo de Souza Medeiros <ignotus21@gmail.com>
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

import os
import gtk
import gobject

from umit.gui.radialnet.HostsViewer import HostsViewer
from umit.gui.radialnet.SaveDialog import SaveDialog
from higwidgets.higwindows import HIGWindow
from umit.core.I18N import _


SHOW = True
HIDE = False

REFRESH_RATE = 500



class ToolsMenu(gtk.Menu):
    """
    """
    def __init__(self, radialnet):
        """
        """
        gtk.Menu.__init__(self)

        self.radialnet = radialnet

        self.__export_chooser = None
        self.__create_items()


    def __create_items(self):
        """
        """
        self.__hosts = gtk.ImageMenuItem(_("Hosts viewer"))
        self.__hosts.connect("activate", self.__hosts_viewer_callback)
        self.__hosts_image = gtk.Image()
        self.__hosts_image.set_from_stock(gtk.STOCK_INDEX, gtk.ICON_SIZE_MENU)
        self.__hosts.set_image(self.__hosts_image)

        self.__save = gtk.ImageMenuItem(_("Save snapshot"))
        self.__save.connect("activate", self.__save_image_callback)
        self.__save_image = gtk.Image()
        self.__save_image.set_from_stock(gtk.STOCK_SAVE, gtk.ICON_SIZE_MENU)
        self.__save.set_image(self.__save_image)

        self.append(self.__hosts)
        self.append(self.__save)

        self.__hosts.show_all()
        self.__save.show_all()


    def __hosts_viewer_callback(self, widget):
        """
        """
        window = HostsViewer(self.radialnet.get_scanned_nodes())
        window.show_all()
        window.set_keep_above(True)


    def __save_image_callback(self, widget):
        """
        """
        self.__save_chooser = SaveDialog()

        while self.__save_chooser.run() == gtk.RESPONSE_OK:

            type, ext = self.__save_chooser.get_filetype()
            file = self.__save_chooser.get_filename()

            if not os.path.exists(file):
                file += ext
                if os.path.exists(file):
                    # This hack is a deep inspection in gtk.FileChooser to get
                    # the save button. If the file with the extension exists we
                    # set the filename set a timeout callback to save button
                    # clicked event and call the dialog again.
                    # TODO: Be sure that the timeout will be called after the
                    # dialog run method.
                    self.__save_chooser.set_filename(file)
                    save = self.__save_chooser.action_area.get_children()[0]
                    gobject.timeout_add(REFRESH_RATE, save.clicked)
                    continue

            try:
                open(file, "w").close()
            except:
                self.__save_chooser.show_error()
                continue

            self.radialnet.save_drawing_to_file(file, type)
            break

        self.__save_chooser.destroy()
        self.__save_chooser = None


    def enable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(True)
        self.__save.set_sensitive(True)


    def disable_dependents(self):
        """
        """
        self.__hosts.set_sensitive(False)
        self.__save.set_sensitive(False)



class Toolbar(gtk.Toolbar):
    """
    """
    def __init__(self, radialnet, window, control, fisheye):
        """
        """
        gtk.Toolbar.__init__(self)
        self.set_style(gtk.TOOLBAR_BOTH_HORIZ)
        self.set_property("icon-size", gtk.ICON_SIZE_MENU)
        self.set_tooltips(True)

        self.radialnet = radialnet

        self.__window = window
        self.__control_widget = control
        self.__fisheye_widget = fisheye

        self.__state = {'fisheye':SHOW, 'control':SHOW}

        self.__fullscreen_window = None

        self.__create_widgets()


    def __create_widgets(self):
        """
        """
        self.__tooltips = gtk.Tooltips()

        self.__tools_menu = ToolsMenu(self.radialnet)

        self.__tools_button = gtk.MenuToolButton(gtk.STOCK_PREFERENCES)
        self.__tools_button.set_label(_("Tools"))
        self.__tools_button.set_is_important(True)
        self.__tools_button.set_menu(self.__tools_menu)
        self.__tools_button.connect('clicked', self.__tools_callback)

        self.__control = gtk.ToggleToolButton(gtk.STOCK_PROPERTIES)
        self.__control.set_label(_("Controls"))
        self.__control.set_is_important(True)
        self.__control.connect('clicked', self.__control_callback)
        self.__control.set_tooltip(self.__tooltips, _("Show control panel"))
        self.__control.set_active(False)

        self.__fisheye = gtk.ToggleToolButton(gtk.STOCK_ZOOM_FIT)
        self.__fisheye.set_label(_("Fisheye"))
        self.__fisheye.set_is_important(True)
        self.__fisheye.connect('clicked', self.__fisheye_callback)
        self.__fisheye.set_tooltip(self.__tooltips, _("Enable fisheye"))
        self.__fisheye.set_active(False)

        self.__fullscreen = gtk.ToggleToolButton(gtk.STOCK_FULLSCREEN)
        self.__fullscreen.set_label(_("Fullscreen"))
        self.__fullscreen.set_is_important(True)
        self.__fullscreen.connect('clicked', self.__fullscreen_callback)
        self.__fullscreen.set_tooltip(self.__tooltips, _("Toggle fullscreen"))

        self.__separator = gtk.SeparatorToolItem()
        self.__expander = gtk.SeparatorToolItem()
        self.__expander.set_expand(True)
        self.__expander.set_draw(False)

        self.insert(self.__tools_button, 0)
        self.insert(self.__expander,     1)
        self.insert(self.__control,      2)
        self.insert(self.__fisheye,      3)
        self.insert(self.__fullscreen,   4)

        gobject.timeout_add(REFRESH_RATE, self.__update)


    def disable_controls(self):
        """
        """
        self.__control.set_sensitive(False)
        self.__fisheye.set_sensitive(False)
        self.__tools_menu.disable_dependents()


    def enable_controls(self):
        """
        """
        self.__control.set_sensitive(True)
        self.__fisheye.set_sensitive(True)
        self.__tools_menu.enable_dependents()


    def disable_tools(self):
        self.__tools_menu.disable_dependents()


    def enable_tools(self):
        self.__tools_menu.enable_dependents()


    def __update(self):
        """
        """
        self.__fisheye.set_active(self.radialnet.get_fisheye())

        self.__fisheye_callback()
        self.__control_callback()

        return True


    def __tools_callback(self, widget):
        """
        """
        self.__tools_menu.popup(None, None, None, 1, 0)


    def __control_callback(self, widget=None):
        """
        """
        if self.__control.get_active() != self.__state['control']:

            if self.__control.get_active():
                self.__control_widget.show()
                self.__control_widget.child.show_all()

            else:
                self.__control_widget.hide()
                self.__control_widget.child.hide_all()

            self.__state['control'] = self.__control.get_active()


    def __fisheye_callback(self, widget=None):
        """
        """
        if self.__fisheye.get_active() != self.__state['fisheye']:

            if not self.radialnet.is_in_animation():

                if self.__fisheye.get_active():

                    self.__fisheye_widget.active_fisheye()
                    self.__fisheye_widget.show()

                    for w in self.__fisheye_widget.get_children():
                        w.show_all()

                else:

                    self.__fisheye_widget.deactive_fisheye()
                    self.__fisheye_widget.hide()

                    for w in self.__fisheye_widget.get_children():
                        w.hide_all()

                self.__state['fisheye'] = self.__fisheye.get_active()


    def __fullscreen_exit(self, widget, event):
        """
        """
        self.__fullscreen.set_active(False)


    def __fullscreen_callback(self, widget=None):
        """
        """
        if self.__fullscreen.get_active():

            self.__fullscreen_window = HIGWindow()
            self.__fullscreen_window.connect('delete-event',
                    self.__fullscreen_exit)
            self.__notebook = self.__window.get_parent()
            self.__window.reparent(self.__fullscreen_window)
            self.__fullscreen_window.show()
            self.__fullscreen_window.fullscreen()

        else:

            self.__window.reparent(self.__notebook)
            self.__notebook.set_tab_label_text(self.__window, _('Topology'))
            self.__notebook.set_current_page(
                    self.__notebook.page_num(self.__window))
            self.__fullscreen_window.hide()
