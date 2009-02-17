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
Network Inventory About window.
"""

import os
import gtk

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higbuttons import HIGButton

from umitCore.I18N import _
from umitCore.Paths import Path, VERSION
from umitInventory import __author__, __version__, __copyright__

pixmaps_dir = Path.pixmaps_dir
if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'logo.png')
else:
    logo = None

class About(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self)

        self.lbl_program_version = gtk.Label(
                ("<span size='30000' weight='heavy'>UMIT %s</span>" % VERSION) +
                ("\n<span size='10000' weight='heavy'>Network Inventory ") +
                _("Build") + (" %s</span>" % __version__))

        self.lbl_program_description = gtk.Label(
                _("UMIT Network Inventory and UMIT Scheduler are UMIT\n") +
                _("extensions developed by") + (" %s\n" % __author__) +
                _("and was sponsored by Google during the Summer of Code "
                    "2007.\nThanks Google!"))

        self.lbl_copyright = gtk.Label("<small>%s</small>" % __copyright__)
        self.logo_img = gtk.Image()
        self.logo_img.set_from_file(logo)
        self.btn_close = HIGButton(stock=gtk.STOCK_CLOSE)

        self.btn_close.connect('clicked', lambda x, y=None:self.destroy())

        self.__set_props()
        self.__do_layout()


    def __set_props(self):
        """
        Set widget properties.
        """
        self.set_title(_("About UMIT Network Inventory"))
        self.set_position(gtk.WIN_POS_CENTER)
        self.lbl_program_version.set_use_markup(True)
        self.lbl_copyright.set_use_markup(True)
        self.lbl_program_description.set_justify(gtk.JUSTIFY_CENTER)

        self.lbl_copyright.set_selectable(True)
        self.lbl_program_description.set_selectable(True)
        self.lbl_program_version.set_selectable(True)


    def __do_layout(self):
        """
        Layout window widgets.
        """
        main_vbox = HIGVBox()
        btns_box = HIGHBox()

        main_vbox.pack_start(self.logo_img)
        main_vbox.pack_start(self.lbl_program_version)
        main_vbox.pack_start(self.lbl_program_description)
        main_vbox.pack_start(self.lbl_copyright)

        btns_box.pack_end(self.btn_close)
        main_vbox._pack_noexpand_nofill(btns_box)

        self.btn_close.grab_focus()

        self.add(main_vbox)
