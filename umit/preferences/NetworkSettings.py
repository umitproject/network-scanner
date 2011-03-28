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

import gtk

from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higentries import HIGTextEntry

from umit.core.UmitLogging import log
from umit.core.I18N import _

from umit.preferences.FramesHIG import *

from umit.preferences.conf.NetworkConf import network_conf


class NetworkTab(TabBox, object):

    def __init__(self, name):
        """
        Create widgets of Proxy
        """
        TabBox.__init__(self, name)
        self._connect_events()

        #Propertys:
        self.proxy = network_conf.proxy
        self.hostname = network_conf.hostname
        self.port = network_conf.port
        self.username = network_conf.username
        self.password = network_conf.password


    def _create_widgets(self):
        self._create_widgets_proxy()
        self.pack_start(self.__frame, False, False)

    def _create_widgets_proxy(self):


        self.__frame = TabFrame(_("Proxy Settings"))
        self.__frame.set_shadow_type(gtk.SHADOW_NONE)
        self.__frame_box = HIGTable(6,2, True)
        self._radio_no_proxy = gtk.RadioButton(None, _('No proxy server'))
        self._radio_proxy = gtk.RadioButton(self._radio_no_proxy,
                                            _('Configure server'))

        # Core Structure of data of proxy:

        fields = []
        fields.append({'name':'hostname',
                       'label':_('Hostname'),
                       'values': network_conf.hostname,
                       'entry' : None
                       })

        fields.append({'name':'port',
                       'label':_('Port'),
                       'values': network_conf.port,
                        'entry' : None ,
                        'type' : 'spin'
                       })

        fields.append({'name':'username',
                       'label':_('Username'),
                       'values': network_conf.username,
                        'entry' : None
                       })

        fields.append({'name': 'password',
                       'label':_('Password'),
                       'values': network_conf.password,
                       'entry' : None,
                       'type' : 'password'
                       })

        self.__proxy_fields = fields
        # Create, attach and set values of widgets of proxy


        xopt = gtk.FILL|gtk.EXPAND| gtk.SHRINK
        yopt = gtk.FILL

        self.__frame_box.attach(self._radio_no_proxy, 0,1,0,1, xopt, yopt)
        self.__frame_box.attach(self._radio_proxy,0,1,1,2)

        row = 2

        # Create list of labels/entrys
        self.__label_list = []
        self.__entry_list = []



        for field in fields:

            # Create widgets
            label = gtk.Label(field['label'])
            if field.has_key('type') and field['type'] == 'spin':
                entry = IntSpin()
            else:
                entry = HIGTextEntry()

            # Add widgets to lists
            self.__label_list.append(label)
            self.__entry_list.append(entry)
            field['entry'] = entry

            # Customize
            label.set_alignment(1.0, 0.0)

            # Attachment Table
            self.__frame_box.attach(label, 0,1,row,row+1, \
                                    xopt, yopt)
            self.__frame_box.attach(entry,1,2,row,row+1)

            # Increment row
            row = row + 1






        self.__frame.add(self.__frame_box)

    def _connect_events(self):

        # Radio Connects
        self._radio_no_proxy.connect("toggled", self.update_proxy_details)
        self._radio_proxy.connect("toggled", self.update_proxy_details)

        # Proxy fields
        self.__get_proxy_entry('hostname').connect('changed', \
                                                   self.update_hostname)
        self.__get_proxy_entry('port').connect('changed', \
                                                   self.update_port)
        self.__get_proxy_entry('username').connect('changed', \
                                                   self.update_username)
        self.__get_proxy_entry('password').connect('changed', \
                                                   self.update_password)

    # Callbacks

    def update_proxy_details(self, widget):
        if not widget.get_active():
            return


        if widget==self._radio_no_proxy:
            self.__active_proxy_details(False)
            network_conf.proxy = False
        elif widget==self._radio_proxy:
            self.__active_proxy_details(True)
            network_conf.proxy = True

    def update_hostname(self, widget):
        network_conf.hostname = widget.get_text()

    def update_port(self, widget):
        network_conf.port = widget.get_text()

    def update_username(self, widget):
        network_conf.username = widget.get_text()

    def update_password(self, widget):
        network_conf.password = widget.get_text()

    #############

    def __get_proxy_entry(self, name):
        for field in self.__proxy_fields:
            if field['name'] == name:
                result =  field['entry']
                break
        assert result != None

        return result


    def __active_proxy_details(self, active):
        # Labels
        for label in self.__label_list:
            label.set_sensitive(active)

        # Entrys
        for entry in self.__entry_list:
            entry.set_sensitive(active)


    # API

    def get_proxy(self):
        if self._radio_no_proxy.get_active():
            return False
        elif self._radio_proxy.get_active():
            return True
    def set_proxy(self, proxy):
        print "setting proxy"
        if proxy:
            self._radio_proxy.set_active(True)
            self.__active_proxy_details(True)
        else:
            self._radio_no_proxy.set_active(True)
            self.__active_proxy_details(False)

    def get_hostname(self):
        entry = self.__get_proxy_entry('hostname')
        return entry.get_text()
    def set_hostname(self, hostname):
        entry = self.__get_proxy_entry('hostname')
        entry.set_text(hostname)

    def get_port(self):
        entry = self.__get_proxy_entry('port')
        return entry.get_text()
    def set_port(self, port):
        entry = self.__get_proxy_entry('port')
        entry.set_text(port)

    def get_username(self):
        entry = self.__get_proxy_entry('username')
        return entry.get_text()

    def set_username(self, username):
        entry = self.__get_proxy_entry('username')
        entry.set_text(username)

    def get_password(self):
        entry = self.__get_proxy_entry('password')
        return entry.get_text()
    def set_password(self, password):
        entry = self.__get_proxy_entry('password')
        entry.set_text(password)


    proxy = property(get_proxy, set_proxy)
    hostname = property(get_hostname, set_hostname)
    port = property(get_port, set_port)
    username = property(get_username, set_username)
    password = property(get_password, set_password)


class IntSpin(gtk.SpinButton):
    def __init__(self, initial=80):
        gtk.SpinButton.__init__(self,
                                gtk.Adjustment(int(initial),0,10**100,0),
                                0.0,0)
