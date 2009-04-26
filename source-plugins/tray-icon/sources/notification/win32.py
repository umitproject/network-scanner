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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 US

import gtk
import gobject

import win32api
import win32con
import win32gui

import os

from umit.plugin.Core import Core
from umit.core.Paths import Path
from umit.core.UmitLogging import log

WM_TASKBARCREATED = win32gui.RegisterWindowMessage('TaskbarCreated')
WM_TRAYMESSAGE = win32con.WM_USER + 20

class StatusIcon(gobject.GObject):
    __gtype_name__ = 'Win32StatusIcon'
    __gsignals__ = {
        'activate' : (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_ACTION,
                     gobject.TYPE_NONE, ()),
        'popup-menu' : (gobject.SIGNAL_RUN_FIRST | gobject.SIGNAL_ACTION,
                     gobject.TYPE_NONE, (gobject.TYPE_UINT, gobject.TYPE_UINT)),
    }

    def __init__(self):
        gobject.GObject.__init__(self)

        self._message_map = {}
        self.notify_icon = None            

        if Core().mainwindow.flags() & gtk.REALIZED:
            self.initialize(Core().mainwindow)
        else:
            self._window = self._hwnd = None
            Core().mainwindow.connect('realize', self.initialize)

        Core().mainwindow.connect('unrealize', self.remove)

    def initialize(self, window):
        # The window is realized now so we can hook the WNDPROC

        self._window = window.window
        self._hwnd = window.window.handle

        # Sublass the window and inject a WNDPROC to process messages.
        self._oldwndproc = win32gui.SetWindowLong(self._hwnd, win32con.GWL_WNDPROC,
                                                  self._wndproc)

        self.add_notify_icon()
    
    def wrap_notify_icon_wndproc(self, hWnd, uMsg, wParam, lParam):
        if lParam == win32con.WM_RBUTTONDOWN:
            self.emit('popup-menu', 3, win32api.GetTickCount())
        elif lParam == win32con.WM_LBUTTONDOWN:
            self.emit('activate')

        return 0

    def add_notify_icon(self):
        if not self.notify_icon:
            hinst = win32gui.GetModuleHandle(None)
            icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
            hicon = win32gui.LoadImage(hinst,
                                       os.path.join(Path.icons_dir, 'umit_24.ico'),
                                       win32con.IMAGE_ICON, 0, 0, icon_flags)

            self.notify_icon = NotifyIcon(self._hwnd, hicon)

            # Makes redraw if the taskbar is restarted.   
            self.message_map(
                {
                    WM_TASKBARCREATED: self.notify_icon._redraw,
                    WM_TRAYMESSAGE : self.wrap_notify_icon_wndproc
                }
            )

    def message_map(self, msg_map={}):
        """ Maps message processing to callback functions ala win32gui. """
        if msg_map:
            if self._message_map:
                duplicatekeys = [key for key in msg_map.keys()
                                 if self._message_map.has_key(key)]
                
                for key in duplicatekeys:
                    new_value = msg_map[key]
                    
                    if isinstance(new_value, list):
                        raise TypeError('Dict cannot have list values')
                    
                    value = self._message_map[key]
                    
                    if new_value != value:
                        new_value = [new_value]
                        
                        if isinstance(value, list):
                            value += new_value
                        else:
                            value = [value] + new_value
                        
                        msg_map[key] = value
            self._message_map.update(msg_map)

    def message_unmap(self, msg, callback=None):
        if self._message_map.has_key(msg):
            if callback:
                cblist = self._message_map[key]
                if isinstance(cblist, list):
                    if not len(cblist) < 2:
                        for i in range(len(cblist)):
                            if cblist[i] == callback:
                                del self._message_map[key][i]
                                return
            del self._message_map[key]

    def remove(self, *args):
        self._message_map = {}
        self.remove_notify_icon()
        self = None
        
    def remove_notify_icon(self):
        """ Removes the notify icon. """
        if self.notify_icon:
            self.notify_icon.remove()
            self.notify_icon = None
            
    def remove(self, *args):
        """ Unloads the extensions. """
        self._message_map = {}
        self.remove_notify_icon()
        self = None            

    def show_balloon_tooltip(self, title, text, timeout=10,
                             icon=win32gui.NIIF_NONE):
        """ Shows a baloon tooltip. """
        if not self.notify_icon:
            self.add_notifyicon()
        self.notify_icon.show_balloon(title, text, timeout, icon)

    def _wndproc(self, hwnd, msg, wparam, lparam):
        """ A WINDPROC to process window messages. """
        if self._message_map.has_key(msg):
            callback = self._message_map[msg]
            if isinstance(callback, list):
                for cb in callback:
                    apply(cb, (hwnd, msg, wparam, lparam))
            else:
                apply(callback, (hwnd, msg, wparam, lparam))

        return win32gui.CallWindowProc(self._oldwndproc, hwnd, msg, wparam,
                                       lparam)

gobject.type_register(StatusIcon)

class NotifyIcon:
    def __init__(self, hwnd, hicon):
        self._hwnd = hwnd
        self._id = 0
        self._flags = win32gui.NIF_MESSAGE | win32gui.NIF_ICON
        self._callbackmessage = WM_TRAYMESSAGE
        self._hicon = hicon

        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self._get_nid())

    def _get_nid(self):
        nid = [self._hwnd, self._id, self._flags, self._callbackmessage,
               self._hicon]
        if not hasattr(self, '_tip'): self._tip = ''
        nid.append(self._tip)

        if not hasattr(self, '_info'): self._info = ''
        nid.append(self._info)
            
        if not hasattr(self, '_timeout'): self._timeout = 0
        nid.append(self._timeout)

        if not hasattr(self, '_infotitle'): self._infotitle = ''
        nid.append(self._infotitle)
            
        if not hasattr(self, '_infoflags'):self._infoflags = win32gui.NIIF_NONE
        nid.append(self._infoflags)

        return tuple(nid)
   
    def remove(self):
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, self._get_nid())

    def set_tooltip(self, tooltip):
        self._flags = self._flags | win32gui.NIF_TIP
        self._tip = tooltip
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self._get_nid())

    def show_balloon(self, title, text, timeout=1000, icon=gtk.STOCK_DIALOG_INFO):
        self._flags = self._flags | win32gui.NIF_INFO
        self._infotitle = title
        self._info = text
        self._timeout = timeout

        if icon == gtk.STOCK_DIALOG_INFO:
            icon = win32gui.NIIF_INFO
        elif icon == gtk.STOCK_DIALOG_WARNING:
            icon = win32gui.NIIF_WARNING
        elif icon == gtk.STOCK_DIALOG_ERROR:
            icon = win32gui.NIIF_ERROR
        else:
            icon = win32gui.NIIF_NONE

        self._infoflags = icon
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, self._get_nid())

    def _redraw(self, *args):
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, self._get_nid())
