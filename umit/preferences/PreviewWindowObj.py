# Copyright (C) 2008 Adriano Monteiro Marques.
#
# Author: Luis A. Bastiao Silva <luis.kop@gmail.com>
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



from umit.preferences.PreviewWindow import PreviewWindow
from umit.preferences.conf.ExposeConf import expose_conf

class PreviewWindowObj(PreviewWindow, object):
    """
    This class make interaction between widget and conf
    """

    def __init__(self):
        PreviewWindow.__init__(self)
        self._connect_events()

        ## Default property values
        #self.show_toolbar = True
        #self.host_list = True
        #self.details = True
        #self.page_inside = True
        #self.icons_toolbar = True
        self.show_toolbar = expose_conf.show_toolbar
        self.host_list = expose_conf.host_list
        self.details = expose_conf.details



    def _connect_events(self):
        self.l2.connect('toggled', self.toggle_cb_toolbar)
        self.l3.connect('toggled', self.toggle_cb_hl)
        self.l4.connect('toggled', self.toggle_cb_details)

    # Update -- Callbacks

    def toggle_cb_toolbar(self, widget, str):
        expose_conf.show_toolbar = not self.show_toolbar
        print "toolbar"
    def toggle_cb_hl(self, widget, str): # Host List
        expose_conf.host_list = not self.host_list
        print "host list"
    def toggle_cb_details(self, widget, str):
        expose_conf.details = not self.details
        print "details"

    # API

    def get_show_toolbar(self):
        print "get"
        print self.l2.get_active()
        return self.l2.get_active()
    def set_show_toolbar(self, toolbar):
        print "set l2"
        print toolbar
        self.l2.set_active(toolbar)

    def get_details(self):
        return self.l4.get_active()
    def set_details(self, details):
        self.l4.set_active(details)

    def get_host_list(self):
        print "get"
        print self.l3.get_active()
        return self.l3.get_active()
    def set_host_list(self, host_list):
        print "set l3"
        print host_list
        self.l3.set_active(host_list)


    # Propertys

    show_toolbar = property(get_show_toolbar, set_show_toolbar)
    details = property(get_details, set_details)
    host_list = property(get_host_list, set_host_list)
