# Copyright (C) 2005-2007 Insecure.Com LLC.
#
# Authors: Adriano Monteiro Marques <py.adriano@gmail.com>
#          Frederico Silva Ribeiro <ribeiro.fsilva@gmail.com>
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
from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGHBox, HIGVBox

from umitCore.BugRegister import BugRegister
from umitCore.I18N import _

class CrashReport(HIGWindow):
    def __init__(self, summary, description):
        HIGWindow.__init__(self)
        gtk.Window.__init__(self)
        self.set_title(_('Crash Report'))
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        
        self.response_id = False
        
        self._create_widgets()
        self._pack_widgets()
        self._connect_widgets()

        self.summary = summary
        self.description = description

    def _create_widgets(self):
        self.vbox = HIGVBox()
        self.button_box = gtk.HButtonBox()
        
        self.private_check = gtk.CheckButton(_("Only Umit project members should read this \
bug report"))
        
        self.email_label = HIGHintSectionLabel(_("Email"),
                                               _("Please, inform a valid e-mail address, from \
where you can be reached to be notified when the bug get fixed. Not used for other purposes."))
        self.email_entry = gtk.Entry()

        self.description_label = HIGHintSectionLabel(_("Description"),
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
        
        self.table.attach_label(self.email_label, 0, 1, 0, 1)
        self.table.attach_entry(self.email_entry, 1, 2, 0, 1)

        self.table.attach_label(self.description_label, 0, 1, 1, 2)
        self.table.attach_entry(self.description_scrolled, 0, 2, 2, 3)

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
        if self.description == "" or self.email == "":
            cancel_dialog = HIGAlertDialog(type=gtk.MESSAGE_ERROR,
                                               message_format=_("Bug report is incomplete!"),
                                               secondary_text=_("The bug report is incomplete. \
You must inform a description that explains clearly what is happening and a valid e-mail, \
so you can be contacted when the bug get fixed."))
            cancel_dialog.run()
            cancel_dialog.destroy()
            return None

        bug_register = BugRegister()

        bug_register.is_private = self.private
        bug_register.category_id = "862568"
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

        if bug_page:
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
        gtk.main_quit()
        sys.exit(0)

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

    def get_email(self):
        return self.email_entry.get_text()

    def set_email(self, email):
        self.email_entry.set_text(email)

    def run_unblocked(self):
        if not self.modal:
            self.set_modal(True)
        self.show_all()

    description = property(get_description, set_description)
    private = property(get_private, set_private)
    email = property(get_email, set_email)


if __name__ == "__main__":
    c = CrashReport("Sumariu", "Descricao")
    c.show_all()
    c.connect("delete-event", lambda x, y: gtk.main_quit())
    
    gtk.main()
