#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import gtk

from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higboxes import HIGHBox, HIGVBox
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGHintSectionLabel, Hint

from umitCore.ServiceFingerprintRegister import ServiceFingerprintRegister
from umitCore.I18N import _

class ServiceFingerprintReport(gtk.Window, object):
    def __init__(self, service_name, fingerprint, ip):
        gtk.Window.__init__(self)
        self.set_title(_('Service Fingerprint Report'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets()

        self.fingerprint = fingerprint
        self.ip = ip
        self.service_name = service_name

    def _create_widgets(self):
        self.vbox = HIGVBox()
        self.button_box = gtk.HButtonBox()
        
        self.submitted_label = HIGHintSectionLabel(_("Submitted by (optional)"),
                                                   _("Enter your name and \
e-mail address if we can contact you with any questions. (kept private, used \
for nothing else)"))
        self.submitted_entry = gtk.Entry()

        self.service_name_label = HIGHintSectionLabel(_("Service Name"),
                                                      _("E.g. smtp, pop-3, \
http, domain, ssh, etc. Umit tries to automaticly fill this field for you, \
based on the Nmap \"SERVICE\" output field. If it is correct, you don't need \
to worry about filling out this field. "))
        self.service_name_entry = gtk.Entry()

        self.platform_label = HIGHintSectionLabel(_("Platform/OS"),
                                                  _('The operating system \
or embedded device the service is running on - Examples are "Linux 2.4.X", \
"Windows XP", "Cisco 3640 router", "Netgear MR814 WAP"'))
        self.platform_entry = gtk.Entry()

        self.service_description_label = HIGHintSectionLabel(_("Service \
Description"),
                                                             _("Please try to \
include vendor name, app name, and version number as applicable. It is OK to \
leave this blank for embedded devices where you have described the hardware \
above and don't have any further details on the service name/version. Here \
are a few examples: ISC Bind 9.2.2, Sendmail 8.12.9/8.10.2, Microsoft Exchange \
5.5.2656.59, Network Associates WebShield 4.5"))
        self.service_description_entry = gtk.Entry()

        self.notes_label = HIGHintSectionLabel(_("Notes"),
                                               _("Further info on the device \
or service, any special customizations, etc. If it isn't obvious, please let \
me know what the service is (Virus scanning email gateway, Gnutella-protocol \
P2P app, print server web configuration port, etc"))
        self.notes_scrolled = gtk.ScrolledWindow()
        self.notes_text = gtk.TextView()

        self.fingerprint_icon = gtk.Image()
        self.fingerprint_text = gtk.Label(_("This form allows you to \
contribute new service/version fingerprints to the Nmap database. Thanks for \
helping! <b>Please do not fill this out unless you are sure that you know what \
application is running on the machine you are submitting</b>. Incorrect \
entries can pollute the database. By submitting fingerprints you are \
transfering any copyright interest in the data to Fyodor so that he \
can modify it, relicense it, incorporate it into programs such as Nmap, etc."))

        self.btn_ok = gtk.Button(stock=gtk.STOCK_OK)
        self.btn_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)

        self.hbox = HIGHBox()
        self.table = HIGTable()

    def _pack_widgets(self):
        self.notes_scrolled.add(self.notes_text)
        self.notes_scrolled.set_policy(gtk.POLICY_AUTOMATIC,
                                       gtk.POLICY_AUTOMATIC)
        self.notes_scrolled.set_size_request(400, 150)
        self.notes_text.set_wrap_mode(gtk.WRAP_WORD)

        self.fingerprint_icon.set_from_stock(gtk.STOCK_DIALOG_INFO,
                                             gtk.ICON_SIZE_DIALOG)
        self.fingerprint_icon.set_padding(10, 0)
        self.fingerprint_text.set_line_wrap(True)
        self.fingerprint_text.set_use_markup(True)

        self.table.attach_label(self.submitted_label, 0, 1, 0, 1)
        self.table.attach_entry(self.submitted_entry, 1, 2, 0, 1)
        
        self.table.attach_label(self.platform_label, 0, 1, 1, 2)
        self.table.attach_entry(self.platform_entry, 1, 2, 1, 2)

        self.table.attach_label(self.service_name_label, 0, 1, 2, 3)
        self.table.attach_entry(self.service_name_entry, 1, 2, 2, 3)

        self.table.attach_label(self.service_description_label, 0, 1, 3, 4)
        self.table.attach_entry(self.service_description_entry, 1, 2, 3, 4)

        self.table.attach_label(self.notes_label, 0, 2, 4, 5)
        self.table.attach_entry(self.notes_scrolled, 0, 2, 5, 6)

        self.hbox.set_border_width(12)
        self.hbox._pack_noexpand_nofill(self.fingerprint_icon)
        self.hbox._pack_expand_fill(self.fingerprint_text)

        self.button_box.set_layout(gtk.BUTTONBOX_END)
        self.button_box.pack_start(self.btn_ok)
        self.button_box.pack_start(self.btn_cancel)

        self.vbox.set_border_width(6)
        self.vbox._pack_noexpand_nofill(self.hbox)
        self.vbox._pack_expand_fill(self.table)
        self.vbox._pack_noexpand_nofill(self.button_box)
        self.add(self.vbox)

    def _connect_widgets(self):
        self.btn_ok.connect("clicked", self.send_report)
        self.btn_cancel.connect("clicked", self.close)
        self.connect("delete-event", self.close)

    def close(self, widget=None, event=None):
        self.destroy()

    def send_report(self, widget):
        if self.service_name == "" or self.service_description == "" or \
           self.platform == "":
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                           message_format=_("Service \
Fingerprint report is incomplete!"),
                                           secondary_text=_("The Service \
Fingerprint report is incomplete. Please, try to provide as much information \
as possible."))
            cancel_dialog.run()
            cancel_dialog.destroy()
            return None

        service_register = ServiceFingerprintRegister()

        service_register.service = self.service_name
        service_register.platform = self.platform
        service_register.description = self.service_description
        service_register.ip = self.ip
        service_register.fingerprint = self.fingerprint
        service_register.email = self.submitted
        service_register.notes = self.notes

        try:
            service_register.report()
        except:
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                           message_format=_("Service \
Fingerprint not registered!"),
                                           secondary_text=_("The Service \
Fingerprint could not be registered. This problem may be caused by the lack \
of Internet Access or indisponibility of the fingerprint server. Please, \
verify your internet access, and then try to register the service fingerprint \
once again."))
            cancel_dialog.run()
            cancel_dialog.destroy()
        else:
            ok_dialog = HIGAlertDialog(type=gtk.MESSAGE_INFO,
                                       message_format=_("Service Fingerprint \
sucessfully registered!"),
                                       secondary_text=_("The Service \
Fingerprint was sucessfully registered. A web page with detailed description \
about this registration is going to be openned in your default web browser."))
            ok_dialog.run()
            ok_dialog.destroy()

            self.close()

    def run_unblocked(self):
        if not self.modal:
            self.set_modal(True)
        self.show_all()

    def get_submitted(self):
        return self.submitted_entry.get_text()

    def set_submitted(self, submitted):
        self.submitted_entry.set_text(submitted)

    def get_platform(self):
        return self.platform_entry.get_text()

    def set_platform(self, platform):
        self.platform_entry.set_text(platform)

    def get_service_name(self):
        return self.service_name_entry.get_text()

    def set_service_name(self, service_name):
        self.service_name_entry.set_text(service_name)

    def get_service_description(self):
        return self.service_description_entry.get_text()

    def set_service_description(self, service_description):
        self.service_description_entry.set_text(service_description)

    def get_notes(self):
        buff = self.notes_text.get_buffer()
        return buff.get_text(buff.get_start_iter(), buff.get_end_iter())

    def set_notes(self, notes):
        self.notes_text.get_buffer().set_text(notes)

    submitted = property(get_submitted, set_submitted)
    platform = property(get_platform, set_platform)
    service_name = property(get_service_name, set_service_name)
    service_description = property(get_service_description,
                                   set_service_description)
    notes = property(get_notes, set_notes)

if __name__ == "__main__":
    w = ServiceFingerprintReport("ssh",
                                 "Testing umit fingerprint submission",
                                 "IP Address")
    w.show_all()

    gtk.main()
