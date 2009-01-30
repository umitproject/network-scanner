# Copyright (C) 2007 Insecure.Com LLC.
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

"""
A GUI for setting every option that may be set for Network Inventory at
startup.
"""

import gtk

from umitCore.I18N import _

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higbuttons import HIGButton
from higwidgets.higframe import HIGFrame

from umitInventory.TLBase import view_mode, view_kind
from umitInventory.StartupSettings import (
    startup_options, write_startup_setting, TL_SECTION, INV_SECTION)

class NISettings(HIGWindow):

    def __init__(self):
        HIGWindow.__init__(self)

        self.timeline = HIGFrame(_("Timeline Settings"))
        self.tl_mode_lbl = gtk.Label(_("Timeline view mode"))
        self.tl_kind_lbl = gtk.Label(_("Timeline view kind"))
        self.tl_mode = gtk.combo_box_new_text()
        self.tl_kind = gtk.combo_box_new_text()

        self.tabs = HIGFrame(_("Devices tab"))
        self.tabs_cbtn = gtk.CheckButton(_("Place close button"))

        self.sbar = HIGFrame(_("Statusbar"))
        self.sbar_tips = gtk.CheckButton(_("Show tips"))

        # bottom buttons
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.ok = HIGButton(stock=gtk.STOCK_OK)

        self.apply.connect("clicked", self._apply_settings)
        self.ok.connect("clicked", self._apply_settings_exit)
        self.cancel.connect("clicked", self._exit)

        self._fill_comboboxes()
        self._load_settings()
        self.__set_props()
        self.__do_layout()


    def _fill_comboboxes(self):
        """
        Fill timeline mode and timeline kind combo boxes with available
        options.
        """
        self.tl_kind_opts = { }
        self.tl_mode_opts = { }

        for opt, value in view_kind.items():
            self.tl_kind.append_text(value)
            self.tl_kind_opts[opt] = value

        for opt, value in view_mode.items():
            self.tl_mode.append_text(value)
            self.tl_mode_opts[opt] = value


    def _load_settings(self):
        """
        Load current settings values.
        """
        options = startup_options()
        start_tlkind = self.tl_kind_opts[options['kind']]
        start_tlmode = self.tl_mode_opts[options['mode']]

        store = self.tl_kind.get_model()
        for indx, item in enumerate(store):
            if item[0] == start_tlkind:
                self.tl_kind.set_active(indx)
                break

        store = self.tl_mode.get_model()
        for indx, item in enumerate(store):
            if item[0] == start_tlmode:
                self.tl_mode.set_active(indx)
                break

        self.tabs_cbtn.set_active(options['tabs_close_btn'])
        self.sbar_tips.set_active(options['tips'])


    def _apply_settings(self, event):
        """
        Apply current settings.
        """
        curr_kind = self.tl_kind.get_active_text()
        for kind, value in self.tl_kind_opts.items():
            if value == curr_kind:
                curr_kind = kind
                break

        curr_mode = self.tl_mode.get_active_text()
        for mode, value in self.tl_mode_opts.items():
            if value == curr_mode:
                curr_mode = mode
                break

        write_startup_setting(TL_SECTION, "mode", curr_mode)
        write_startup_setting(TL_SECTION, "kind", curr_kind)
        write_startup_setting(INV_SECTION, "tabs_close_btn",
            self.tabs_cbtn.get_active())
        write_startup_setting(INV_SECTION, "tips", self.sbar_tips.get_active())


    def _apply_settings_exit(self, event):
        """
        Apply current settings and leave.
        """
        self._apply_settings(None)
        self._exit(None)


    def _exit(self, event):
        """
        Close this window.
        """
        self.destroy()


    def __set_props(self):
        """
        Window properties.
        """
        self.set_title(_("Network Inventory Settings"))
        self.set_default_size(305, -1)


    def __do_layout(self):
        main_vbox = HIGVBox()
        btnsbox = HIGHBox()

        # timeline frame
        tl_settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        tl_settings_align.set_padding(6, 0, 12, 0)
        tl_settings_vbox = HIGVBox()

        mode_hbox = HIGHBox()
        mode_hbox._pack_noexpand_nofill(self.tl_mode_lbl)
        mode_hbox._pack_expand_fill(self.tl_mode)

        kind_hbox = HIGHBox()
        kind_hbox._pack_noexpand_nofill(self.tl_kind_lbl)
        kind_hbox._pack_expand_fill(self.tl_kind)

        tl_settings_vbox._pack_noexpand_nofill(mode_hbox)
        tl_settings_vbox._pack_noexpand_nofill(kind_hbox)
        tl_settings_align.add(tl_settings_vbox)
        self.timeline.add(tl_settings_align)
        main_vbox._pack_noexpand_nofill(self.timeline)
        # end timeline frame

        # statusbar frame
        sbar_settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        sbar_settings_align.set_padding(6, 0, 12, 0)
        sbar_settings_vbox = HIGVBox()

        sbar_settings_vbox._pack_noexpand_nofill(self.sbar_tips)
        sbar_settings_align.add(sbar_settings_vbox)
        self.sbar.add(sbar_settings_align)
        main_vbox._pack_noexpand_nofill(self.sbar)
        # end statusbar frame

        # tabs frame
        tabs_settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        tabs_settings_align.set_padding(6, 0, 12, 0)
        tabs_settings_vbox = HIGVBox()

        tabs_settings_vbox._pack_noexpand_nofill(self.tabs_cbtn)
        tabs_settings_align.add(tabs_settings_vbox)
        self.tabs.add(tabs_settings_align)
        main_vbox._pack_noexpand_nofill(self.tabs)
        # end tabs frame

        btnsbox._pack_noexpand_nofill(self.apply)
        btnsbox._pack_noexpand_nofill(self.cancel)
        btnsbox._pack_noexpand_nofill(self.ok)
        bbox = gtk.HBox()
        bbox.pack_end(btnsbox, False, False, 0)

        main_vbox.pack_end(bbox, False, False, 0)
        main_vbox.pack_end(gtk.HSeparator(), False, False, 0)

        self.add(main_vbox)
