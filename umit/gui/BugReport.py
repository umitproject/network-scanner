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
import gobject
import webbrowser

from higwidgets.higdialogs import HIGDialog, HIGAlertDialog
from higwidgets.higlabels import HIGHintSectionLabel
from higwidgets.higtables import HIGTable
from higwidgets.higboxes import HIGHBox, hig_box_space_holder
from higwidgets.higbuttons import HIGStockButton

from umit.core.BugRegister import BugRegister
from umit.core.Version import VERSION
from umit.core.I18N import _


def show_report(reuse_mainloop, bug_page):
    if not bug_page:
        return
    try:
        webbrowser.open(bug_page)
    except: # XXX What exceptions should be caught here ?
        page_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                message_format=_("Could not open default Web Browser"),
                secondary_text=_("Umit was unable to open your default "
                    "web browser to show the bug tracker page with the "
                    "report status. Try visiting Umit's bug tracker "
                    "page to see if your bug was reported."))
        run_dialog(reuse_mainloop, page_dialog)

def destroy_dialog(dialog, response, callback=None, *args):
    dialog.destroy()
    if callback is not None:
        callback(*args)

def run_dialog(reuse_mainloop, dialog, callback=None, *args):
    """If reuse_mainloop is true, the current mainloop is reused instead
    of starting another.

    callback is a function to be called with args after the dialog is
    destroyed.
    """
    if not dialog.modal:
        dialog.set_modal(True)
    dialog.connect('response', destroy_dialog, callback, *args)
    if reuse_mainloop:
        dialog.show_all()
    else:
        dialog.run()

class BugReport(HIGDialog):
    def __init__(self, title=_('Bug Report'), summary=None, description=None,
                 category=None, crashreport=False, description_dialog=None,
                 reuse_mainloop=True):
        HIGDialog.__init__(self, title=title,
            buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT,
                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))

        # If reuse_mainloop is true, then dialogs created inside this dialog
        # will not start another mainloop.
        self._reuse_mainloop = reuse_mainloop

        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)

        self.crashreport = crashreport
        self.description_dialog = description_dialog
        self._create_widgets()
        self._set_category_list()
        self._pack_widgets()
        self._connect_widgets()
        self.summary = summary or ''
        self.description_report = description
        if self.crashreport:
            self.description = _("CrashReport automatically created")
        else:
            if self.description_dialog is None:
                self.description = description or ''
            else:
                self.description = description_dialog or ''
        self.category = category or ''

    def _set_category_list(self):
        # Obtained at bug tracker page source code
        # The following two lines are commented due to component deprecation
        #self.category_list.append(["umitCore","umitCore"])
        #self.category_list.append(["umitGUI","umitGUI"])
        self.category_list.append(["Umit","Umit"])
        self.category_list.append(["CrashReport","CrashReport"])
        self.category_list.append(["Documentation", "Documentation"])
        self.category_list.append(["UmitWeb","UmitWeb"])
        self.category_list.append(["InterfaceEditor", "InterfaceEditor"])
        self.category_list.append(["NetworkInventory", "NetworkInventory"])
        self.category_list.append(["website","website"])

    def _create_widgets(self):
        self.category_label = HIGHintSectionLabel(_("Category (optional)"),
            _("If you know in which section of the program "
            "is the bug, please, select it from the choosebox. "
            "If you don't know what section to choose, leave it blank."))
        self.category_list = gtk.ListStore(str, str)
        self.category_combo = gtk.ComboBoxEntry(self.category_list, 0)

        self.email_label = HIGHintSectionLabel(_("Email"),
            _("Please inform a valid e-mail address from "
            "where you can be reached to be notified when the bug gets "
            "fixed. Not used for other purposes."))
        self.email_entry = gtk.Entry()

        self.summary_label = HIGHintSectionLabel(_("Summary"),
            _("This should be a quick description of the issue. "
            "Try to be clear and concise."))
        self.summary_entry = gtk.Entry()

        self.description_label = HIGHintSectionLabel(_("Description"),
            _("This is where you should write about the bug, "
            "describing it as clear as possible and giving as many "
            "informations as you can and how to reproduce the bug."))
        self.description_scrolled = gtk.ScrolledWindow()
        self.description_text = gtk.TextView()

        self.bug_icon = gtk.Image()
        self.bug_text = gtk.Label(_("This Bug Report dialog allows you "
            "to easily tell us about a problem that you may have found on "
            "Umit. Doing so, you help us to help you, by fixing and "
            "improving Umit faster than usual."))
        
        if self.crashreport:
            # Create a button to show details 
            self.show_details = HIGStockButton(gtk.STOCK_DIALOG_INFO,
                                           _("Show Details"))

        self.hbox = HIGHBox()
        self.table = HIGTable()

    def _pack_widgets(self):
        self.description_scrolled.add(self.description_text)
        self.description_scrolled.set_policy(gtk.POLICY_AUTOMATIC, 
            gtk.POLICY_AUTOMATIC)
        self.description_scrolled.set_size_request(400, 150)
        self.description_text.set_wrap_mode(gtk.WRAP_WORD)

        self.bug_icon.set_from_stock(gtk.STOCK_DIALOG_INFO, 
            gtk.ICON_SIZE_DIALOG)
        self.bug_icon.set_padding(10, 0)
        self.bug_text.set_line_wrap(True)

        self.hbox.set_border_width(12)
        
        nextpos = (0, 1)
        if not self.crashreport:
            self.table.attach_label(self.category_label, 0, 1, 0, 1)
            self.table.attach_entry(self.category_combo, 1, 2, 0, 1)
            nextpos = (1, 2)

        self.table.attach_label(self.email_label, 0, 1, *nextpos)
        self.table.attach_entry(self.email_entry, 1, 2, *nextpos)

        nextpos = (2, 3)
        if not self.crashreport:
            self.table.attach_label(self.summary_label, 0, 1, 2, 3)
            self.table.attach_entry(self.summary_entry, 1, 2, 2, 3)
            nextpos = (3, 4)

        self.table.attach_label(self.description_label, 0, 2, *nextpos)
        nextpos = nextpos[0] + 1, nextpos[1] + 1
        self.table.attach_entry(self.description_scrolled, 0, 2, *nextpos)

        self.hbox._pack_noexpand_nofill(self.bug_icon)
        self.hbox._pack_expand_fill(self.bug_text)

        self.vbox.pack_start(self.hbox, False, False)
        self.vbox.pack_start(self.table)
       
        # Just need because in crash report some aditional 
        # information will be show 
        if self.crashreport:
            # Add a button to action-area
            spaceholder = hig_box_space_holder()
            self.action_area.pack_end(spaceholder)
            self.action_area.pack_end(self.show_details)
            # Put "Show details" to left side respecting HIG
            self.action_area.reorder_child(self.show_details,0)
            self.action_area.reorder_child(spaceholder, 1)
        
        
        
    def _connect_widgets(self):
        self.connect('response', self.check_response)
        if self.crashreport:
            self.show_details.connect('clicked',
                                      self._show_details)
        
    def _show_details(self, widget):
        # Create info necessary
        desc = [ self.email,
                 self.summary,
                 self.description_report,
                 self.description,
                 self.category] 
        # Create another dialog to show details
        details = BugReportDescription(*desc)
        details.show_all()
        details.run()
        details.destroy()
        
        
    def check_response(self, widget, response_id):
        if response_id == gtk.RESPONSE_ACCEPT: # clicked on Ok btn
            self.send_report()
        elif response_id in (gtk.RESPONSE_DELETE_EVENT, gtk.RESPONSE_CANCEL,
                gtk.RESPONSE_NONE):
            # there are tree possibilities to being here:
            # 1) user clicked on 'x' button
            # 2) user clicked on 'cancel' button
            # 3) report was sent successfully and now we can destroy this
            self.destroy()

    def send_report(self):
        """Prepare dialog to send a bug report and then call _send_report."""
        # set cursor to busy cursor (supposing it will take some time
        # to submit the report)
        self.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))

        # disable dialog controls
        for child in self.vbox.get_children():
            child.set_sensitive(False)

        # attempt sending report
        gobject.idle_add(self._send_report)

    def restore_state(self):
        """Restore dialog state, just like it was before calling
        send_report."""
        self.window.set_cursor(None)
        for child in self.vbox.get_children():
            child.set_sensitive(True)

    def _send_report(self):
        if self.summary == "" or self.description == "" or self.email == "":
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                message_format=_("Bug report is incomplete!"),
                secondary_text=_("The bug report is incomplete. "
                    "You must inform a description that explains clearly "
                    "what is happening and a valid e-mail, so you can be "
                    "contacted when the bug gets fixed."))
            run_dialog(self._reuse_mainloop, cancel_dialog)
            return self.restore_state()

        bug_register = BugRegister()

        bug_register.component = self.category
        bug_register.summary = self.summary
        if self.description_report is not None:
            bug_register.details = self.description_report
        else:
            bug_register.details = self.description.replace("\n", "[[BR]]")
        bug_register.reporter = self.email

        bug_page = None
        try:
            bug_page = bug_register.report()
            assert bug_page
        except:
            import traceback
            traceback.print_exc()
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                message_format=_("Bug not reported!"),
                secondary_text=_("The bug description could not be "
                    "reported. This problem may be caused by the lack "
                    "of Internet access or indisponibility of the bug "
                    "tracker server. Please, verify your internet access, "
                    "and then try to report the bug once again."))
            run_dialog(self._reuse_mainloop, cancel_dialog)
            return self.restore_state()
        else:
            ok_dialog = HIGAlertDialog(type=gtk.MESSAGE_INFO,
                message_format=_("Bug sucessfully reported!"),
                secondary_text=_("The bug description was sucessfully "
                    "reported. A web page with detailed description about "
                    "this report will be opened in your default web browser "
                    "now."))
            run_dialog(self._reuse_mainloop, ok_dialog,
                    show_report, # callback
                    self._reuse_mainloop, bug_page) # args

        # report sent successfully
        self.response(gtk.RESPONSE_DELETE_EVENT)

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

    def get_email(self):
        return self.email_entry.get_text()

    def set_email(self, email):
        self.email_entry.set_text(email)


    category = property(get_category, set_category)
    summary = property(get_summary, set_summary)
    description = property(get_description, set_description)
    email = property(get_email, set_email)

class CrashReport(BugReport):
    def __init__(self, summary, description, title=_('Crash Report'),\
                 description_dialog=None):
        BugReport.__init__(self, title, summary, description,
                           "CrashReport", True,
                           reuse_mainloop=False,
                           description_dialog=description_dialog)
        
class BugReportDescription(HIGDialog):
    def __init__(self, reporter, summary, description, 
                 comments, category):
        HIGDialog.__init__(self,
                           title='Details of Crash Report',
                           buttons=(gtk.STOCK_OK, gtk.RESPONSE_ACCEPT)
                           )
        # Save information about Bug Report
        self._reporter = reporter
        self._summary = summary
        self._description = description
        self._comments = comments
        self._category = category
        
        # Widgets matter
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self._create_widgets()
        self._pack_widgets()
        
    def _create_widgets(self):
        
        self.bug_text = gtk.Label(_("Bug report details that "
                                  "will be send!"))
        
        self.description_scrolled = gtk.ScrolledWindow()
        self.description_text = gtk.TextView()

        # Fill the text entry
        description =  _("Reporter: %s\nSummary: %s\nCategory: %s\n"
                         "Comments: %s\n\nDescription: %s" % 
                         (self._reporter, self._summary, self._category,
                          self._comments, self._description))
        self.description_text.get_buffer().set_text(description.replace("[[BR]]", "\n"))
        self.description_text.set_editable(False)
        
    def _pack_widgets(self):
        self.description_scrolled.add(self.description_text)
        self.description_scrolled.set_policy(gtk.POLICY_AUTOMATIC, 
            gtk.POLICY_AUTOMATIC)
        self.description_scrolled.set_size_request(400, 150)
        self.description_text.set_wrap_mode(gtk.WRAP_WORD)

        self.vbox.pack_start(self.bug_text, False, False)
        self.vbox.pack_start(self.description_scrolled)
       
        
        
if __name__ == "__main__":
    c = BugReport()
    c.show_all()
    c.connect('destroy', gtk.main_quit)
    gtk.main()
