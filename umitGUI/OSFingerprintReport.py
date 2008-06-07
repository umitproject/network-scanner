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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
import cPickle

from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higboxes import HIGHBox, HIGVBox
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGHintSectionLabel

from umitCore.OSFingerprintRegister import OSFingerprintRegister
from umitCore.OSClassificationDump import os_classification_file
from umitCore.I18N import _

class OSFingerprintReport(gtk.Window, object):
    def __init__(self, fingerprint, ip):
        gtk.Window.__init__(self)
        self.set_title(_('Operating System Fingerprint Report'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        self.fingerprint = fingerprint
        self.ip = ip

        self._create_widgets()
        self._set_classification_list()
        self._pack_widgets()
        self._connect_widgets()

    def _set_classification_list(self):
        class_file = open(os_classification_file, "rb")
        class_list = cPickle.load(class_file)
        class_file.close()
        
        for classification in class_list:
            self.classification_list.append([classification[1],
                                             classification[0]])

    def _create_widgets(self):
        self.vbox = HIGVBox()
        self.button_box = gtk.HButtonBox()
        
        self.submitted_label = HIGHintSectionLabel(_("Submitted by (optional)"),
                                                   _("Enter your name and \
e-mail address if we can contact you with any questions. (kept private, \
used for nothing else)"))
        self.submitted_entry = gtk.Entry()

        self.target_device_label = HIGHintSectionLabel(_("Target OS/device info"),
                                                       _("<b>The more details \
the better!</b> For UNIX machines, '<i>uname -a</i>' often gives the proper \
version number. On Linux, please also specify the distribution version (such as\
Redhat 9.0) if you are using a vendor-provided kernel. For Windows, the \
'<i>winver</i>' command (if available) should show you any service pack \
information. If a Windows target has no service packs installed, \
please say so explicitly. For appliances/embedded devices, please mention \
the model number and what it is (printer, webcam, DSL router, VOIP phone, \
etc). Try to provide the architecture (X86, SPARC, etc.) where appropriate."))
        self.target_device_entry = gtk.Entry()

        self.classification_label = HIGHintSectionLabel(_("Classification"),
                                                        _("Please select \
the Device/OS info from this alphabetized choosebox"))
        self.classification_list = gtk.ListStore(str, str)
        self.classification_combo = gtk.ComboBoxEntry(self.classification_list,
                                                      0)

        self.notes_label = HIGHintSectionLabel(_("Notes"),
                                               _("Fill with further info on \
the device, any special network conditions, etc."))
        self.notes_scrolled = gtk.ScrolledWindow()
        self.notes_text = gtk.TextView()

        self.fingerprint_icon = gtk.Image()
        self.fingerprint_text = gtk.Label(_("This form allows you to \
contribute new operating system fingerprints to the Nmap database. Thanks for \
helping! <b>Please do not fill this out unless you are sure that you know \
what application is running on the machine you are submitting</b>. Incorrect \
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
        
        self.table.attach_label(self.target_device_label, 0, 1, 1, 2)
        self.table.attach_entry(self.target_device_entry, 1, 2, 1, 2)

        self.table.attach_label(self.classification_label, 0, 1, 2, 3)
        self.table.attach_entry(self.classification_combo, 1, 2, 2, 3)

        self.table.attach_label(self.notes_label, 0, 2, 3, 4)
        self.table.attach_entry(self.notes_scrolled, 0, 2, 4, 5)

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
        if self.target_device == "":
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                           message_format=_("Operating System \
Fingerprint report is incomplete!"),
                                           secondary_text=_("The Operating \
System Fingerprint report is incomplete. Please, try to provide as much \
information as possible."))
            cancel_dialog.run()
            cancel_dialog.destroy()
            return None

        os_register = OSFingerprintRegister()

        os_register.email = self.submitted
        os_register.os = self.target_device
        os_register.classification = self.classification
        os_register.ip = self.ip
        os_register.fingerprint = self.fingerprint
        os_register.notes = self.notes

        try:
            os_register.report()
        except:
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                           message_format=_("Operating System \
Fingerprint not registered!"),
                                           secondary_text=_("The Operating \
System Fingerprint could not be registered. This problem may be caused by \
the lack of Internet Access or indisponibility of the fingerprint server. \
Please, verify your internet access, and then try to register the operating \
system fingerprint once again."))
            cancel_dialog.run()
            cancel_dialog.destroy()
        else:
            ok_dialog = HIGAlertDialog(type=gtk.MESSAGE_INFO,
                                       message_format=_("Operating System \
Fingerprint sucessfully registered!"),
                                       secondary_text=_("The Operating System \
Fingerprint was sucessfully registered. A web page with detailed description \
about this registration is going to be openned in your default web browser."))
            ok_dialog.run()
            ok_dialog.destroy()

            self.close()

    def run_unblocked(self):
        if not self.modal:
            self.set_modal(True)
        self.show_all()

    def dialog_response_cb(self, dialog, response):
        self.response_id = response

    def get_submitted(self):
        return self.submitted_entry.get_text()

    def set_submitted(self, submitted):
        self.submitted_entry.set_text(submitted)

    def get_target_device(self):
        return self.target_device_entry.get_text()

    def set_target_device(self, target_device):
        self.target_device_entry.set_text(target_device)

    def get_classification(self):
        selected = self.classification_combo.child.get_text()
        for i in self.classification_list:
            if i[0] == selected:
                return i[1]
        return ""

    def set_classification(self, classification):
        self.classification.child.set_text(classification)

    def get_notes(self):
        buff = self.notes_text.get_buffer()
        return buff.get_text(buff.get_start_iter(), buff.get_end_iter())

    def set_notes(self, notes):
        self.notes_text.get_buffer().set_text(notes)

    submitted = property(get_submitted, set_submitted)
    target_device = property(get_target_device, set_target_device)
    classification = property(get_classification, set_classification)
    notes = property(get_notes, set_notes)

if __name__ == "__main__":
    w = OSFingerprintReport("Testing umit fingerprint submission", "IP Address")
    w.connect("delete-event", lambda x, y: gtk.main_quit())
    w.show_all()
    
    gtk.main()
