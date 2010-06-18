#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques
#
# Author: Francesco Piccinno <stack.box@gmail.com>
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
import pango

import os.path

from higwidgets.higtooltips import *

from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.UmitLogging import log

from umit.plugin.Core import Core
from umit.plugin.Engine import Plugin
from umit.plugin.Parser import Parser

WIN32_PRESENT = False

if os.name == 'nt':
    try:
        from notification.win32 import StatusIcon
        WIN32_PRESENT = True
    except ImportError:
        raise Exception('If you are using Windows you need Win32 Extensions package for python to use that plugin.\nDownload a copy from\n\nhttp://starship.python.net/crew/mhammond/win32/\n\nand reenable the plugin.')

try:
    import pynotify
    NOTIFY_PRESENT = True
except ImportError:
    NOTIFY_PRESENT = False

class Preferences(object):
    def __init__(self):
        self.change_cb = None
        self.parser = Parser()
        self.conf_file = os.path.join(Path.config_dir, "TrayIcon.xml")
        self.def_config = """
<preferences>
  <section name="notifications">
    <i name="type" default="1" description="Type of notifications (0 for libnotify, 1 for higtooltip)" min='0' max='1' value="1"/>
  </section>
</preferences>
"""
        self.read_conf()

        log.debug("Notification type set to %d" % \
                  self.parser['notifications']['type'].value)

    def read_conf(self):
        good = False

        if os.path.exists(self.conf_file):
            try:
                log.debug("Parsing conf_file placed at %s" % self.conf_file)
                
                self.parser.parse_file(self.conf_file)
                good = True
            except:
                pass

        if not good:
            log.debug("Loading default values for TrayIcon")
            self.parser.parse_string(self.def_config)

    def save_conf(self):
        # Let's save our configuration to self.conf_file
        log.debug("Saving configuration to %s" % self.conf_file)
        self.parser.save_to_file(self.conf_file)

    def update(self):
        if self.change_cb is not None:
            self.change_cb(self.parser['notifications']['type'].value)

if not WIN32_PRESENT:
    tray_prefs = Preferences()

class TrayPlugin(Plugin):
    TYPE_LIBNOTIFY = 0
    TYPE_HIGTOOLTIP = 1
    TYPE_WINDOWS = 2

    def start(self, reader):
        self.reader = reader

        self.icon = None
        self.wnd_pos = (0, 0)

        self.menu = gtk.Menu()
        self.menu.show()

        action = gtk.Action(None, '_Quit', 'Quit from UMIT', gtk.STOCK_QUIT)
        action.connect('activate', self.__on_quit)

        item = action.create_menu_item()
        item.show()

        self.menu.append(item)

        self.type = self.notifier = None

        # Force to use win32 module
        if WIN32_PRESENT:
            self.set_type(TrayPlugin.TYPE_WINDOWS)
        else:
            self.set_type(tray_prefs.parser['notifications']['type'].value)
            tray_prefs.parser['notifications']['type'].value = self.type

            logo = os.path.join(Path.icons_dir, 'umit_16.ico')
            log.debug('Creating status icon with %s as logo' % logo)

            self.icon = gtk.status_icon_new_from_file(logo)
            tray_prefs.change_cb = self.set_type

        self.icon.connect('popup-menu', self.__on_right_click)
        self.icon.connect('activate', self.__on_activate)

    def set_type(self, typo):
        log.debug('called with type = %d' % typo)

        if typo == TrayPlugin.TYPE_WINDOWS and WIN32_PRESENT:

            self.icon = StatusIcon()
            self.type = TrayPlugin.TYPE_WINDOWS

            log.debug('Now notifications will use win32 api')

        elif typo == TrayPlugin.TYPE_LIBNOTIFY and NOTIFY_PRESENT:
            
            if pynotify.init('UMIT'):
                self.notifier = pynotify.Notification
                self.type = TrayPlugin.TYPE_LIBNOTIFY

                log.debug('Now notifications will use LibNotify')
            else:
                self.set_type(TrayPlugin.TYPE_HIGTOOLTIP)
        else:

            self.type = TrayPlugin.TYPE_HIGTOOLTIP
            self.notifier = HIGTooltip()

            log.debug('Now notifications will use HIGTooltip')

    def remove_status_icon(self):
        if not self.icon:
            return

        if self.type == TrayPlugin.TYPE_WINDOWS:
            self.icon.remove()
        else:
            self.icon.set_visible(False)
            del self.icon

        self.icon = None

    def stop(self):
        self.remove_status_icon()

    def __on_right_click(self, w, evt, evt_time):
        self.popup_menu.popup(None, None,
            (self.type != TrayPlugin.TYPE_WINDOWS) and \
                 (gtk.status_icon_position_menu)or (None), evt, \
                              evt_time, w)

    def __on_activate(self, widget):
        mainwnd = Core().mainwindow

        if mainwnd.flags() & gtk.VISIBLE:
            self.wndpos = mainwnd.get_position()
            mainwnd.hide()
        else:
            mainwnd.move(*self.wndpos)
            mainwnd.show()

    def __on_quit(self, action):
        # Ask to the main window to exit
        Core().mainwindow.emit('delete-event', None)

    def show_notification(self, msg, title=_("<span size=\"medium\">"
                                             "<b>Information</b></span>"),
                          stock=gtk.STOCK_DIALOG_INFO, fname=None, \
                          timeout=5000):
        """
        Show a notification message by using libnotify or HIGTooltip class
        @param msg The text message of the notification
        @param title The title of the notification
        @param stock The stock image to use
        @param fname The image filename with full path to be used as image
                     instead the stock image
        @param timeout Time to live of the notification expressed in msecs.
                       (pass None for persistent notification)
        """

        if self.type == TrayPlugin.TYPE_WINDOWS:
            if self.icon.notify_icon:
                title = pango.parse_markup(title)[1]
                msg = pango.parse_markup(msg)[1]
                self.icon.notify_icon.show_balloon(title, msg,
                    (timeout is None) and (0) or (timeout), stock)

        elif self.type == TrayPlugin.TYPE_HIGTOOLTIP:
            rect = self.icon.get_geometry()

            if rect is not None:
                rect = rect[1]
            else:
                return

            data = HIGTooltipData(msg, title, stock, fname)
            self.notifier.show_at(self.icon, data, rect.x, rect.y, timeout)
        else:
            title = pango.parse_markup(title)[1]
            notify = self.notifier(title, msg, \
                                   (fname is None) and (stock) or (None))
            if fname:
                pixbuf = gtk.gdk.pixbuf_new_from_file(fname)
                notify.set_icon_from_pixbuf(pixbuf)
            if timeout:
                notify.set_timeout(timeout)
            notify.show()

    def get_popup_menu(self):
        return self.menu

    def get_status_icon(self):
        return self.icon

    popup_menu = property(get_popup_menu)
    status_icon = property(get_status_icon)

class PrefDialog(gtk.Dialog):
    def __init__(self):
        gtk.Dialog.__init__(self, "UMIT - Tray Icon Preferences",
                            Core().mainwindow,
                            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                            (gtk.STOCK_CANCEL, gtk.RESPONSE_REJECT,
                             gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))

        self.typenot = gtk.RadioButton(None, 'Use LibNotify for notifications')
        self.typehig = gtk.RadioButton(self.typenot, \
                                             'Use HIGTooltip for notifications')

        vbox = gtk.VBox(False, 2)
        vbox.pack_start(self.typenot, False, False, 0)
        vbox.pack_start(self.typehig, False, False, 0)

        frame = gtk.Frame('Type of notifications')
        frame.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        frame.add(vbox)

        self.vbox.pack_start(frame)
        self.set_size_request(300, 150)

        self.connect('response', self.__on_response)
        self.show_all()
    
    def update(self):
        # Adjusting to the current preferences

        if tray_prefs.parser['notifications']['type'].value == 0:
            self.typenot.set_active(True)
        else:
            self.typehig.set_active(True)

        if not NOTIFY_PRESENT:
            self.typenot.set_sensitive(False)
            self.typehig.set_active(True)

    def __on_response(self, dialog, response_id):
        if response_id == gtk.RESPONSE_ACCEPT:
            if self.typehig.get_active():
                tray_prefs.parser['notifications']['type'].value = 1
            else:
                tray_prefs.parser['notifications']['type'].value = 0

            tray_prefs.save_conf()
            tray_prefs.update()

        self.hide()
        self.destroy()

def show_preferences():
    pref = PrefDialog()
    pref.update()
    pref.show()

__plugins__ = [TrayPlugin]

# No preferences if you are using windows
if os.name != 'nt':
    __pref_func__ = show_preferences
