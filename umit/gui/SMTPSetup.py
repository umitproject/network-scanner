# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author: Guilherme Polo <ggpolo@gmail.com>
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

import os
import gtk
from ConfigParser import ConfigParser

from umit.core.Paths import Path
from umit.core.I18N import _

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog

from umit.gui.Help import show_help

pixmaps_dir = Path.pixmaps_dir
    
if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'wizard_logo.png')
else:
    logo = None

class SMTPSetup(HIGWindow):
    """
    SMTP editor.
    """
    
    def __init__(self):
        HIGWindow.__init__(self)
        
        self.wtitle = _("SMTP Account Editor")

        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # schemas name
        self.schema_name_lbl = HIGEntryLabel(_("Schema name"))
        self.schema_name = gtk.combo_box_entry_new_text()
        self.schema_name.connect('changed', self._check_schema)
        # smtp server
        self.smtp_server_lbl = HIGEntryLabel(_("Server"))
        self.smtp_server = gtk.Entry()
        self.smtp_port_lbl = HIGEntryLabel(_("Port"))
        self.smtp_port = gtk.Entry()
        # sending mail..
        self.smtp_mailfrom_lbl = HIGEntryLabel(_("Mail from"))
        self.smtp_mailfrom = gtk.Entry()
        # smtp auth
        self.smtp_need_auth = gtk.CheckButton(_("Servers requires authentication"))
        self.smtp_need_auth.connect('toggled', self._auth_need)
        self.smtp_login_lbl = HIGEntryLabel(_("Username"))
        self.smtp_login = gtk.Entry()
        self.smtp_passwd_lbl = HIGEntryLabel(_("Password"))
        self.smtp_passwd = gtk.Entry()
        self.smtp_passwd.set_visibility(False)
        self._auth_need(None)
        # smtp encryption
        self.smtp_encrypt_tls = gtk.CheckButton(_("Use TLS Encryption"))

        """
        Missing: SSL encryption,
                 Other authentication methods.
        """ 

        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.apply.connect('clicked', self._save_schema)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.ok = HIGButton(stock=gtk.STOCK_OK)
        self.ok.connect('clicked', self._save_schema_and_leave)
        
        self.load_schemas()
        
        self.__set_props()
        self.__do_layout()

        self.connect('destroy', self._exit)
        

    def load_schemas(self):
        """
        Load schemas profiles.
        """
        schemas = ConfigParser()
        schemas.read(Path.smtp_schemas)
        
        self.sections = [ ]
        self.schema_name.get_model().clear()
        for section in schemas.sections():
            self.sections.append(section)
            self.schema_name.append_text(section)
            
        self.schema_name.set_active(0)
        self._check_schema(None)

    
    def _load_schema(self):
        """
        Load current set schedule schema.
        """
        schema = ConfigParser()
        schema.read(Path.smtp_schemas)
        
        enable = {'tls':self.smtp_encrypt_tls.set_active,
                  'auth':self.smtp_need_auth.set_active}
        values = {'user':self.smtp_login.set_text,
                  'pass':self.smtp_passwd.set_text,
                  'server':self.smtp_server.set_text,
                  'port':self.smtp_port.set_text,
                  'mailfrom':self.smtp_mailfrom.set_text}
        
        for item in schema.items(self.schema_name.get_active_text()):
            if item[0] in ('tls', 'auth'):
                enable[item[0]](int(item[1]))
            else:
                values[item[0]](item[1])
                

    def _check_schema(self, event):
        """
        Check if current text in schema_name combobox is a schema name.
        """
        if self.schema_name.get_active_text() in self.sections: 
            # load schema
            self._load_schema()
        else:
            # reset to default values
            self.smtp_mailfrom.set_text('')
            self.smtp_server.set_text('')
            self.smtp_port.set_text('')
            self.smtp_encrypt_tls.set_active(False)
            self.smtp_login.set_text('')
            self.smtp_passwd.set_text('')
            self.smtp_need_auth.set_active(False)
            self._auth_need(None)
            
    
    def _auth_need(self, event):
        """
        SMTP Authentication toggled.
        """
        status = self.smtp_need_auth.get_active()
        self.smtp_login.set_sensitive(status)
        self.smtp_passwd.set_sensitive(status)
        self.smtp_login_lbl.set_sensitive(status)
        self.smtp_passwd_lbl.set_sensitive(status)
    
    
    def _save_schema(self, event):
        """
        Save current schema.
        """
        schema = self.schema_name.get_active_text()
        server = self.smtp_server.get_text()
        port = self.smtp_port.get_text()
        auth = self.smtp_need_auth.get_active()
        mailfrom = self.smtp_mailfrom.get_text()
        
        if auth:
            user = self.smtp_login.get_text()
            passwd = self.smtp_passwd.get_text()
        
        if auth and not (user and passwd):
            dlg = HIGAlertDialog(self, 
                                 message_format=_('SMTP Schema - Error\
 while saving.'),
                                 secondary_text=_("You need to specify an \
username and password for this SMTP Schema."))
            
            dlg.run()
            dlg.destroy()
            return
        
        if not schema or not server or not port or not mailfrom:
            dlg = HIGAlertDialog(self, 
                                 message_format=_('SMTP Schema - Error\
 while saving.'),
                                 secondary_text=_("The following fields \
need to be filled: Schema Name, Server, Port and Mail from."))
            
            dlg.run()
            dlg.destroy()
            return
        
        # write schema to file
        s_cfg = ConfigParser()
        s_cfg.read(Path.smtp_schemas)
        
        if not s_cfg.has_section(schema):
            new_sec = True
            s_cfg.add_section(schema)
        else:
            new_sec = False
        
        if auth:
            s_cfg.set(schema, 'auth', '1')
        else:
            s_cfg.set(schema, 'auth', '0')
            user = ''
            passwd = ''
            
        s_cfg.set(schema, 'port', port)
        s_cfg.set(schema, 'server', server)
        s_cfg.set(schema, 'user', user)
        s_cfg.set(schema, 'pass', passwd)
        s_cfg.set(schema, 'mailfrom', mailfrom)
        
        if self.smtp_encrypt_tls.get_active():
            s_cfg.set(schema, 'tls', '1')
        else:
            s_cfg.set(schema, 'tls', '0')
            
        s_cfg.write(open(Path.smtp_schemas, 'w'))
        
        if new_sec:
            self.load_schemas()
        
        
    def _save_schema_and_leave(self, event):
        """
        Save current schema and close editor.
        """
        self._save_schema(None)
        self._exit(None)
        
        
    def __set_props(self):
        """
        Set window properties.
        """
        self.set_title(self.wtitle)
       
    
    def _show_help(self, event):
        """
        Open SMTP Setup help
        """
        show_help(self, "smtpsetup.html")


    def __do_layout(self):
        """
        Layout widgets in window.
        """
        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        header_hbox = HIGHBox()
        schema_table = HIGTable()
        auth_table = HIGTable()
        btns_hbox = HIGHBox()

        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)
        
        # schema name
        schema_table.attach_label(self.schema_name_lbl, 0, 1, 0, 1)
        schema_table.attach_entry(self.schema_name, 1, 2, 0, 1)
        
        # smtp server
        schema_table.attach_label(self.smtp_server_lbl, 0, 1, 1, 2)
        schema_table.attach_entry(self.smtp_server, 1, 2, 1, 2)

        # smtp server port
        schema_table.attach_label(self.smtp_port_lbl, 0, 1, 2, 3)
        schema_table.attach_entry(self.smtp_port, 1, 2, 2, 3)
        
        # smtp mail from
        schema_table.attach_label(self.smtp_mailfrom_lbl, 0, 1, 3, 4)
        schema_table.attach_entry(self.smtp_mailfrom, 1, 2, 3, 4)
        
        # smtp user
        auth_table.attach_label(self.smtp_login_lbl, 0, 1, 0, 1)
        auth_table.attach_entry(self.smtp_login, 1, 2, 0, 1)
        
        # smtp passwd
        auth_table.attach_label(self.smtp_passwd_lbl, 0, 1, 1, 2)
        auth_table.attach_label(self.smtp_passwd, 1, 2, 1, 2)
        
        # bottom buttons
        btns_hbox.set_homogeneous(True)
        btns_hbox._pack_expand_fill(self.help)
        btns_hbox._pack_expand_fill(hig_box_space_holder())
        btns_hbox._pack_expand_fill(self.apply)
        btns_hbox._pack_expand_fill(self.cancel)
        btns_hbox._pack_expand_fill(self.ok)
                
        main_vbox._pack_noexpand_nofill(header_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(schema_table)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(self.smtp_need_auth)
        main_vbox._pack_noexpand_nofill(auth_table)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(self.smtp_encrypt_tls)
        main_vbox.pack_end(btns_hbox, False, False, 0)
        
        self.add(main_vbox)


    def _exit(self, event):
        """
        Close current window.
        """
        self.destroy()
        

if __name__ == "__main__":
    w = SMTPSetup()
    w.show_all()
    w.connect('destroy', gtk.main_quit)
    gtk.main()
    
