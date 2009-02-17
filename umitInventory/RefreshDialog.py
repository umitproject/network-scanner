# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Guilherme Polo <ggpolo@gmail.com>
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

"""
Dialog for changing custom time refresh for TLGraph
"""

import gtk

from umitCore.I18N import _

from higwidgets.higdialogs import HIGDialog

class CustomRefreshDialog(HIGDialog):
    """
    Dialog for adjusting custom refresh time for TLGraph.
    """

    def __init__(self, start_value):
        HIGDialog.__init__(self, title=_("Refresh Time"),
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_OK,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        lbl = gtk.Label(_("Minutes"))
        self.spinbtn = gtk.SpinButton(gtk.Adjustment(value=start_value,
            lower=1, upper=10000, step_incr=1), 1)

        hbox = gtk.HBox()
        hbox.add(lbl)
        hbox.add(self.spinbtn)

        self.vbox.pack_start(hbox)
        self.show_all()


def custom_refresh(*args):
    """
    Runs CustomRefreshDialog dialog.
    """
    dialog = CustomRefreshDialog(*args)
    response = dialog.run()
    dialog.destroy()

    if response == gtk.RESPONSE_OK:
        return dialog.spinbtn.get_value_as_int()
