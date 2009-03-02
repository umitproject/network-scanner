# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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

import gtk

from higwidgets.higdialogs import HIGAlertDialog

class GenericAlert(HIGAlertDialog):
    """
    An alert dialog that allows arbitrary stock buttons.
    """

    def __init__(self, title, text, buttons=None, 
                 dlg_type=gtk.MESSAGE_WARNING):
        """
        when passing buttons, use a format like this:
        
           {key: (response: stock)}
        
           -> where key should be an integer, so it will pack buttons
              in the order you want.
        """

        HIGAlertDialog.__init__(self, type=dlg_type, buttons=gtk.BUTTONS_NONE,
                                message_format=title, secondary_text=text)
                                
        dlg_vbox = self.get_children()[0]
        buttons_box = dlg_vbox.get_children()[-1]

        if not buttons:
            buttons = { }

        # pack buttons in dialog's buttonsbox
        for resp_button in buttons.values():
            resp = resp_button[0]
            button = resp_button[1]
            
            btn = gtk.Button(stock=button)
            btn.show()
            buttons_box.pack_start(btn, False, False, 0)

            btn.connect('clicked', self._send_response, resp)


    def _send_response(self, event, resp):
        """
        Emit "standard" signal used for returning value in dialogs.
        """
        self.emit('response', resp)


if __name__ == "__main__":
    # sample
    alert = GenericAlert("Teste", "Testing", 
                         buttons={2: (gtk.RESPONSE_OK, gtk.STOCK_OK),
                                  1: (gtk.RESPONSE_CANCEL, gtk.STOCK_CANCEL)})
    resp = alert.run()
    if resp == gtk.RESPONSE_OK:
        print "ok"
    elif resp == gtk.RESPONSE_CANCEL:
        print "cancel"
    alert.destroy()
    gtk.main()
