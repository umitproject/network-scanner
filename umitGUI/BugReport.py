#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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
import gobject
import webbrowser

from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higlabels import HIGSectionLabel, HIGHintSectionLabel
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, HIGVBox

from umitCore.BugRegister import BugRegister
from umitCore.I18N import _

class BugReport(gtk.Window, object):
    def __init__(self):
        gtk.Window.__init__(self)
        self.set_title(_('Bug Report'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self.response_id = False
        
        self._create_widgets()
        self._set_category_list()
        self._pack_widgets()
        self._connect_widgets()

    def _set_category_list(self):
        # Obtained at bug tracker page source code
        self.category_list.append(["None", "100"])
        self.category_list.append(["Search Window", "883332"])
        self.category_list.append(["Colored Nmap Output", "862566"])
        self.category_list.append(["Command Constructor (Wizard)", "862564"])
        self.category_list.append(["Compare Results", "862563"])
        self.category_list.append(["Interface (example)", "750538"])
        self.category_list.append(["Other", "862568"])
        self.category_list.append(["Profile Editor", "862565"])
        self.category_list.append(["umitCore", "862561"])
        self.category_list.append(["umitGUI", "862562"])
        self.category_list.append(["XML Parser", "862567"])
        
    def _create_widgets(self):
        self.vbox = HIGVBox()
        self.button_box = gtk.HButtonBox()
        
        self.private_check = gtk.CheckButton(_("Only Umit project members should read this \
bug report"))
        
        self.category_label = HIGHintSectionLabel(_("Category (optional)"),
                                                  _("If you know in which section of the \
program is the bug, please, seclect it from the choosebox. If you don't know what section to \
choose, leave it blank."))
        self.category_list = gtk.ListStore(str, str)
        self.category_combo = gtk.ComboBoxEntry(self.category_list, 0)

        self.email_label = HIGHintSectionLabel(_("Email"),
                                               _("Please, inform a valid e-mail address, from \
where you can be reached to be notified when the bug get fixed. Not used for other purposes."))
        self.email_entry = gtk.Entry()

        self.summary_label = HIGHintSectionLabel(_("Summary"),
                                                 _("This should be a quick description of \
the issue. Try to be clear and concise."))
        self.summary_entry = gtk.Entry()

        self.description_label = HIGHintSectionLabel(_("Detailed Description"),
                                                     _("This is where you should really write \
about the bug, describing it as clear as possible, and giving as many informations as you can \
along with your system informations, like: Which operating system you're using? \
Which Nmap version you have insalled?"))
        self.description_scrolled = gtk.ScrolledWindow()
        self.description_text = gtk.TextView()

        self.bug_icon = gtk.Image()
        self.bug_text = gtk.Label(_("This Bug Report dialog, allows you to easily tell us \
about a problem that you may have found on Umit. Doing so, you help us to help you, by \
fixing and improving Umit faster than usual."))

        self.btn_ok = gtk.Button(stock=gtk.STOCK_OK)
        self.btn_cancel = gtk.Button(stock=gtk.STOCK_CANCEL)

        self.hbox = HIGHBox()
        self.table = HIGTable()

    def _pack_widgets(self):
        self.description_scrolled.add(self.description_text)
        self.description_scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        self.description_scrolled.set_size_request(400, 150)
        self.description_text.set_wrap_mode(gtk.WRAP_WORD)

        self.bug_icon.set_from_stock(gtk.STOCK_DIALOG_INFO, gtk.ICON_SIZE_DIALOG)
        self.bug_icon.set_padding(10, 0)
        self.bug_text.set_line_wrap(True)

        self.hbox.set_border_width(12)
        self.vbox.set_border_width(6)
        
        self.table.attach_label(self.category_label, 0, 1, 0, 1)
        self.table.attach_entry(self.category_combo, 1, 2, 0, 1)

        self.table.attach_label(self.email_label, 0, 1, 1, 2)
        self.table.attach_entry(self.email_entry, 1, 2, 1, 2)

        self.table.attach_label(self.summary_label, 0, 1, 2, 3)
        self.table.attach_entry(self.summary_entry, 1, 2, 2, 3)

        self.table.attach_label(self.description_label, 0, 2, 3, 4)
        self.table.attach_entry(self.description_scrolled, 0, 2, 4, 5)

        #self.table.attach_label(self.private_check, 0, 2, 5, 6)

        self.hbox._pack_noexpand_nofill(self.bug_icon)
        self.hbox._pack_expand_fill(self.bug_text)

        self.button_box.set_layout(gtk.BUTTONBOX_END)
        self.button_box.pack_start(self.btn_ok)
        self.button_box.pack_start(self.btn_cancel)
        
        self.vbox._pack_noexpand_nofill(self.hbox)
        self.vbox._pack_expand_fill(self.table)
        self.vbox._pack_noexpand_nofill(self.button_box)
        self.add(self.vbox)

    def _connect_widgets(self):
        self.btn_ok.connect("clicked", self.send_report)
        self.btn_cancel.connect("clicked", self.close)
        self.connect("delete-event", self.close)

    def send_report(self, widget):
        if self.summary == "" or self.description == "" or self.email == "":
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                               message_format=_("Bug report is incomplete!"),
                                               secondary_text=_("The bug report is incomplete. \
You must inform a short summary that describes the issue, a detailed description that \
explains clearly what is happening and a valid e-mail, so you can be contacted when the bug \
get fixed."))
            cancel_dialog.run()
            cancel_dialog.destroy()
            return None

        bug_register = BugRegister()

        bug_register.is_private = self.private
        bug_register.category_id = self.category_id
        bug_register.summary = self.summary
        bug_register.details = "%s\n\nEmail: %s" % (self.description, self.email)
        
        bug_page = None
        try:
            bug_page = bug_register.report()
        except:
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                           message_format=_("Bug not reported!"),
                                           secondary_text=_("The bug description could \
not be reported. This problem may be caused by the lack of Internet Access or \
indisponibility of the bug tracker server. Please, verify your internet access, and \
then try to report the bug once again."))
            cancel_dialog.run()
            cancel_dialog.destroy()
        else:
            ok_dialog = HIGAlertDialog(type=gtk.MESSAGE_INFO,
                                       message_format=_("Bug sucessfully reported!"),
                                       secondary_text=_("The bug description was \
sucessfully reported. A web page with detailed description about this report is \
going to be openned in your default web browser."))
            ok_dialog.run()
            ok_dialog.destroy()

            self.close()

        try:
            webbrowser.open(bug_page)
        except:
            page_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                       message_format=_("Could not open default Web Browser"),
                                       secondary_text=_("Umit was unable to open your default \
web browser to show the bug tracker page with the report status. Try to visit the Umit's \
bug tracker page to see if your bug was reported (you won't see if you marked the check box \
that makes the report private)."))
            page_dialog.run()
            page_dialog.destroy()

            self.close()

    def close(self, widget=None, event=None):
        self.destroy()

    def get_category(self):
        return self.category_combo.child.get_text()

    def set_category(self, category):
        self.category_combo.child.set_text(category)

    def get_summary(self):
        return self.summary_entry.get_text()

    def set_summary(self, summary):
        self.summary_entry.set_text(summary)

    def get_description(self):
        buff = self.description_text.get_buffer()
        return buff.get_text(buff.get_start_iter(), buff.get_end_iter())

    def set_description(self, description):
        self.description_text.get_buffer().set_text(description)

    def get_private(self):
        if self.private_check.get_active():
            return "1"
        return "0"

    def set_private(self, private):
        self.private_check.set_active(private)

    def get_category_id(self):
        for i in self.category_list:
            if i[0] == self.category:
                return i[1]
        return "100"

    def get_email(self):
        return self.email_entry.get_text()

    def set_email(self, email):
        self.email_entry.set_text(email)

    def run_unblocked(self):
        if not self.modal:
            self.set_modal(True)
        self.show_all()

    category_id = property(get_category_id)
    category = property(get_category, set_category)
    summary = property(get_summary, set_summary)
    description = property(get_description, set_description)
    private = property(get_private, set_private)
    email = property(get_email, set_email)

if __name__ == "__main__":
    w = BugReport()
    w.show_all()
    w.connect("delete-event", lambda x, y: gtk.main_quit())
    
    gtk.main()
