# vim: set encoding=utf-8 :

# Copyright (C) 2009 Adriano Monteiro Marques
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

import gtk
import umit.gui.radialnet.RadialNet as RadialNet

from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higlabels import HIGLabel, HIGSectionLabel
from higwidgets.higboxes import HIGHBox, HIGVBox
from umit.core.I18N import _


TYPES = {"PDF - Portable Document Format": (RadialNet.FILE_TYPE_PDF,".pdf"),
         "PNG - Portable Network Graphics": (RadialNet.FILE_TYPE_PNG,".png"),
         "PS - PostScript": (RadialNet.FILE_TYPE_PS,".ps"),
         "SVG - Scalable Vectorial Graphics": (RadialNet.FILE_TYPE_SVG,".svg")}


class SaveDialog(gtk.FileChooserDialog):
    def __init__(self):
        """
        """
        super(SaveDialog, self).__init__(title=_("Save Topology"),
                action=gtk.FILE_CHOOSER_ACTION_SAVE,
                buttons=(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                    gtk.STOCK_SAVE, gtk.RESPONSE_OK))

        self.__combo = gtk.combo_box_new_text()

        types_list = TYPES.keys()
        types_list.sort()

        for i in types_list:
            self.__combo.append_text(i)

        self.__combo.set_active(1)
        self.__label = HIGLabel(_("Select the output type:"))

        self.__hbox = HIGHBox()
        self.__hbox._pack_noexpand_nofill(self.__label)
        self.__hbox._pack_expand_fill(self.__combo)

        self.set_extra_widget(self.__hbox)
        self.set_do_overwrite_confirmation(True)

        self.__hbox.show_all()

    def show_error(self):
        """
        """
        alert = HIGAlertDialog(parent=self,
                type=gtk.MESSAGE_ERROR,
                message_format=_("Can't create file"),
                secondary_text=_("Please check if you have permission to "
                    "write this file."))
        alert.run()
        alert.destroy()

    def get_filetype(self):
        """
        """
        return TYPES[self.__combo.get_active_text()]
