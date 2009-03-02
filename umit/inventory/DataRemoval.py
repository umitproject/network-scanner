# Copyright (C) 2007 Adriano Monteiro Marques
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
Controls data removal for Network Inventory.
"""

import gtk
import gobject

from umit.core.I18N import _
from umit.core.DataDecay import get_decays, set_decay, remove_old_data

from higwidgets.higwindows import HIGWindow
from higwidgets.higlabels import HIGSectionLabel
from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGHBox, HIGVBox

class ConfigureDataRemoval(HIGWindow):
    """
    Sets for how long to keep Inventory data.
    """

    def __init__(self):
        HIGWindow.__init__(self)

        self.tooltips = gtk.Tooltips()
        self.data_lbl = HIGSectionLabel(_("Delete data older than"))
        self.days_lbl = HIGSectionLabel(_("days"))
        self.days = gtk.SpinButton(gtk.Adjustment(value=get_decays()[1],
            lower=0, upper=5000, step_incr=1), 1)

        self.tooltips.set_tip(self.days,
            _("Set value as 0 to disable data removal"))

        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)

        self.cancel.connect("clicked", self._exit)
        self.apply.connect("clicked", self._set_new_decay)

        self.__set_props()
        self.__do_layout()


    def _set_new_decay(self, event):
        """
        Set new decay value for inventories in config file.
        """
        set_decay("inventory_decay", self.days.get_value_as_int())
        self._exit(None)


    def _exit(self, event):
        """
        Destroy window.
        """
        self.destroy()


    def __set_props(self):
        """
        Window properties.
        """
        self.set_title(_("Configure Inventory Data Removal"))


    def __do_layout(self):
        """
        Layout window widgets.
        """
        main_vbox = HIGVBox()
        days_box = HIGHBox()
        btns_box = HIGHBox()

        days_box._pack_noexpand_nofill(self.data_lbl)
        days_box._pack_expand_fill(self.days)
        days_box._pack_noexpand_nofill(self.days_lbl)

        btns_box.pack_end(self.apply, False, False, 0)
        btns_box.pack_end(self.cancel, False, False, 0)

        main_vbox._pack_noexpand_nofill(days_box)
        main_vbox.pack_end(btns_box, False, False, 0)

        self.add(main_vbox)


class RemoveOldData(HIGWindow):
    """
    Called if needed before finishing Network Inventory to remove old data.
    """

    def __init__(self):
        HIGWindow.__init__(self)

        self.iimg = gtk.Image()
        self.iimg.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)

        self.topic = gtk.Label()
        self.topic.set_markup(_("<b>Please wait...</b>"))
        self.message = gtk.Label(
            _("Removing data from Network Inventory database"))

        self.connect('realize', self.start_removal)

        self.__layout()


    def start_removal(self, widget):
        widget.set_decorated(False)
        gobject.timeout_add(100, self.remove_and_leave)


    def remove_and_leave(self):
        remove_old_data()
        self.destroy()


    def __layout(self):
        self.set_position(gtk.WIN_POS_CENTER)

        main_vbox = HIGVBox()
        top_hbox = HIGHBox()

        top_hbox._pack_noexpand_nofill(self.iimg)
        top_hbox._pack_noexpand_nofill(self.topic)

        main_vbox._pack_noexpand_nofill(top_hbox)
        main_vbox._pack_noexpand_nofill(self.message)

        self.add(main_vbox)

