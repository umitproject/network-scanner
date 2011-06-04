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

import os
import gtk
from ConfigParser import ConfigParser

from umit.core.I18N import _
from umit.core.Paths import Path
from umit.core.UmitConf import CommandProfile

from umit.gui.SchedulerEdit import SchedProfileEditor
from umit.gui.ProfileCombo import ProfileCombo
from umit.gui.Wizard import Wizard

from umit.inventory.HostDiscovery import HostDiscovery
from umit.inventory.InventoryCommonDialog import NoScheduleDlg
from umit.inventory.InventoryException import NoInventory

from higwidgets.higdialogs import HIGAlertDialog
from higwidgets.higwindows import HIGWindow
from higwidgets.higbuttons import HIGButton
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder

pixmaps_dir = Path.pixmaps_dir

if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'wizard_logo.png')
else:
    logo = None

class NewInventory(HIGWindow):
    """
    A window for creating new or editing existing Inventories.
    """

    def __init__(self, inventory=None, edit_mode=False):
        """
        If you want to load an inventory at startup, pass it to inventory.
        If you want to run this in edit mode, set to True edit_mode.
        """
        HIGWindow.__init__(self)

        self.schemawin = None
        self.discoverywin = None
        self.edit_mode = edit_mode
        if edit_mode:
            self.wtitle = _("Editing Inventory")
        else:
            self.wtitle = _("New Inventory")

        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # inventory
        self.invname_lbl = HIGEntryLabel(_("Inventory's name"))
        self.invname = gtk.Entry()
        self.invname.connect('changed', self._check_invname)
        self.invname_inuse = HIGEntryLabel(_("in use"))
        self.invname_inuse.set_sensitive(False)
        self.invenabled = gtk.CheckButton(_("Enabled"))
        self.invenabled.set_active(True)
        # scan command
        self.scandefault = gtk.CheckButton(_("Use default scan options"))
        img_info = gtk.Image()
        img_info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
        self.scandefault_tip = gtk.EventBox()
        self.scandefault_tip.add(img_info)

        self.scanadv = gtk.Expander(_("Use advanced scan options"))
        self.scan_name_lbl = HIGEntryLabel(_("Scan Profile"))
        self.scan_name = ProfileCombo()
        self.scan_name.update()
        self.scan_name.set_active(0)
        self.scan_name.connect('changed', self._set_scan_command)
        self.cmd_wizard = gtk.Button(stock=gtk.STOCK_CONVERT)
        blbl = self.cmd_wizard.get_children(
            )[0].get_children()[0].get_children()[1]
        blbl.set_text(_("Command Wizard"))
        self.cmd_wizard.connect('clicked', self._open_cmd_wizard)

        self.scan_command_lbl = HIGEntryLabel(_("Command"))
        self.scan_command = gtk.Entry()
        self.scan_command.connect('changed', self._set_scan_type)
        self._set_scan_command(None)
        self.scandefault.set_active(True)
        # scan target
        self.scantarget_lbl = HIGEntryLabel(_("Scan target"))
        self.scantarget = gtk.Entry()
        self.scantarget_discovery = HIGButton(_("Use host discovery"))
        self.scantarget_discovery.connect('clicked', self._open_host_discovery)
        # scheduling profiles
        self.sched_name_lbl = HIGEntryLabel(_("Scheduling Profile"))
        self.sched_name = gtk.combo_box_new_text()
        self.sched_name_edit = gtk.Button(stock=gtk.STOCK_EDIT)
        blbl = self.sched_name_edit.get_children(
            )[0].get_children()[0].get_children()[1]
        blbl.set_text(_("Edit Profiles"))
        self.sched_name_edit.connect('clicked', self._edit_schedprofiles)
        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.ok = HIGButton(stock=gtk.STOCK_OK)
        self.ok.connect('clicked', self._save_inventory_and_leave)

        self.tooltips = gtk.Tooltips()
        self.tooltips.set_tip(self.scandefault_tip,
            _("nmap -T Aggressive -sV -n -O -v target"))

        # disable controls if edit_mode=True
        if edit_mode:
            self.invname.set_sensitive(False)
            self.scandefault.set_sensitive(False)
            self.scandefault_tip.set_sensitive(False)
            self.scanadv.set_sensitive(False)
            self.scan_name.set_sensitive(False)
            self.scan_command.set_sensitive(False)
            self.scantarget_lbl.set_sensitive(False)
            self.scantarget.set_sensitive(False)
            self.scantarget_discovery.set_sensitive(False)

        self.connect('destroy', self._exit)
        self.profile_running = None # no SchedProfileEditor instance is running.
        self.load_schemas()
        self._load_pscheds()

        # load an inventory if especified
        self.loaded_command = None
        if inventory:
            self.load_inventory(inventory)

        self.__set_props()
        self.__do_layout()


    def load_inventory(self, inventory):
        """
        Load inventory.
        """
        inv = ConfigParser()
        inv.read(Path.sched_schemas)

        if not inv.has_section(inventory):
            dlg = NoScheduleDlg()
            dlg.run()
            dlg.destroy()
            raise NoInventory(inventory)

        self.invname.set_text(inventory)
        for item in inv.items(inventory):
            if item[0] == 'profile':
                pindx = self.profiles.index(item[1])
                self.sched_name.set_active(pindx)
            if item[0] == 'enabled':
                self.invenabled.set_active(int(item[1]))
            if item[0] == 'command':
                self.loaded_command = item[1]


    def load_schemas(self):
        """
        Load scheduler schemas profiles.
        """
        schemas = ConfigParser()
        schemas.read(Path.sched_schemas)

        self.sections = [ ]
        for section in schemas.sections():
            self.sections.append(section)


    def _load_pscheds(self):
        """
        Load scheduling profiles.
        """
        pscheds = ConfigParser()
        pscheds.read(Path.sched_profiles)

        self.profiles = [ ]
        self.sched_name.get_model().clear()
        for section in pscheds.sections():
            self.sched_name.append_text(section)
            self.profiles.append(section)

        self.sched_name.set_active(0)


    def _check_invname(self, event):
        """
        Check if Inventory's name isn't in use.
        """
        if self.invname.get_text() and \
           (self.invname.get_text() in self.sections) and \
            not self.edit_mode:
            self.invname_inuse.set_sensitive(True)
        else:
            self.invname_inuse.set_sensitive(False)


    def _edit_schedprofiles(self, event):
        """
        Open Scheduling Profiles Editor.
        """
        if self.profile_running:
            return

        win = SchedProfileEditor(self, self.sched_name.get_active_text())
        win.show_all()
        self.profile_running = win


    def _set_scan_type(self, event):
        """
        When scan command is changed, unset "Default scan options" if it is
        selected.
        """
        if self.scandefault.get_active():
            self.scandefault.set_active(False)


    def _open_cmd_wizard(self, event):
        """
        Run command wizard window and update combobox when it finishes.
        """
        def update_scan_profiles(wwin):
            self.scan_name.update()

        w = Wizard()
        w.show_all()
        w.connect('destroy', update_scan_profiles)


    def _open_host_discovery(self, event):
        """
        Open host discovery window.
        """
        if self.discoverywin:
            return

        w = HostDiscovery(self)
        w.show_all()

        self.discoverywin = w


    def get_discoverywin(self):
        """
        Get HostDiscovery running instance.
        """
        return self.__discoverywin


    def set_discoverywin(self, win):
        """
        Set HostDiscovery instance.
        """
        self.__discoverywin = win


    def get_schemawin(self):
        """
        Get scheduelr schemas editor running instance.
        """
        return self.__schemawin


    def set_schemawin(self, win):
        """
        Set scheduler schemas editor instance.
        """
        self.__schemawin = win


    def get_profile_running(self):
        """
        Get profile editor running instance.
        """
        return self.__profilerunning


    def set_profile_running(self, running):
        """
        Set profile editor instance.
        """
        self.__profilerunning = running


    def _save_inventory(self, event):
        """
        Save inventory.
        """
        target = self.scantarget.get_text()
        invname = self.invname.get_text()
        notinuse = (self.invname_inuse.state == gtk.STATE_INSENSITIVE)
        command_adv = self.scan_command.get_text()
        
        # checking for errors
        if not notinuse or not len(invname) and not self.edit_mode:
            dlg = HIGAlertDialog(self,
                message_format=_("New Inventory - Error while creating."),
                secondary_text=_("You tried to use an existing Inventory "
                    "name or you didn't specify one."))

            dlg.run()
            dlg.destroy()
            return 0

        if not len(target) and not self.edit_mode:
            dlg = HIGAlertDialog(self,
                message_format=_("New Inventory - Error  while creating."),
                    secondary_text=_("You didn't specify any target."))

            dlg.run()
            dlg.destroy()
            return 0

        if not len(command_adv) and not self.scandefault.get_active() \
            and not self.edit_mode:
            dlg = HIGAlertDialog(self,
                message_format=_("New Inventory - Error while creating."),
                secondary_text=_("You need to toggle \"Use default scan "
                    "options\" or specify a command."))

            dlg.run()
            dlg.destroy()
            return 0
        # end error checking

        if self.scandefault.get_active() and not self.edit_mode:
            command = "nmap -T Aggressive -sV -n -O -v " + target
        elif not self.edit_mode:
            target_cmd = "<target>"
            target_pos = command_adv.find(target_cmd)
            if target_pos != -1:
                start = target_pos
                end = target_pos + len(target_cmd)
                command = command_adv[:start] + target + command_adv[end:]
            else:
                dlg = HIGAlertDialog(self,
                    message_format=_("New Inventory - Error while creating."),
                    secondary_text=_("It seems you removed <target> from the "
                        "Scan command entry, you need to leave it somewhere "
                        "there."))

                dlg.run()
                dlg.destroy()
                return 0

        schedule = self.sched_name.get_active_text()
        enabled = int(self.invenabled.get_active())
        # write inventory to schema's file
        s_cfg = ConfigParser()
        s_cfg.read(Path.sched_schemas)

        if not s_cfg.has_section(invname):
            new_sec = True
            s_cfg.add_section(invname)
        elif self.edit_mode:
            new_sec = False
        else:
            print "How the hell did we get here?!"
            print "Report as BUG"
            return 0

        if new_sec:
            # New Section
            s_cfg.set(invname, 'profile', schedule)
            s_cfg.set(invname, 'command', command)
            s_cfg.set(invname, 'enabled', enabled)
            s_cfg.set(invname, 'addtoinv', '2')
            s_cfg.set(invname, 'saveto', '')
            s_cfg.set(invname, 'mailto', '')
            s_cfg.set(invname, 'smtp', '')
        else:
            # Edit Mode
            s_cfg.set(invname, 'profile', schedule)
            s_cfg.set(invname, 'enabled', enabled)
            s_cfg.set(invname, 'command', self.cmd_entry.get_text())

        s_cfg.write(open(Path.sched_schemas, 'w'))

        self.load_schemas()

        return 1


    def _save_inventory_and_leave(self, event):
        """
        Save Inventory and close window.
        """
        close_win = self._save_inventory(None)
        if close_win:
            self._exit(None)


    def _set_scan_command(self, event):
        """
        Set scan command based on chosen profile.
        """
        profile = self.scan_name.get_selected_profile()
        cmd_profile = CommandProfile()
        command = cmd_profile.get_command(profile)
        self.scan_command.set_text(command % '<target>')


    def _show_help(self, event):
        """
        Show help for creating a New Inventory.
        """
        pass


    def _exit(self, event):
        """
        Close window.
        """
        if self.schemawin:
            self.schemawin._exit(None)

        if self.profile_running:
            self.profile_running._exit(None)

        self.destroy()


    def __set_props(self):
        """
        Set window properties.
        """
        self.set_title(self.wtitle)


    def __do_layout(self):
        """
        Layout widgets.
        """
        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        header_hbox = HIGHBox()
        invname_hbox = HIGHBox()
        scan_hbox = HIGHBox()
        scanadv_hbox = HIGHBox()
        scantarget_hbox = HIGHBox()
        sched_box = HIGHBox()
        btns_hbox = HIGHBox()

        # header
        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)
        # inventory's name
        invname_hbox._pack_noexpand_nofill(self.invname_lbl)
        invname_hbox._pack_expand_fill(self.invname)
        invname_hbox._pack_noexpand_nofill(self.invname_inuse)
        invname_hbox._pack_noexpand_nofill(self.invenabled)
        # scan command
        scan_hbox._pack_noexpand_nofill(self.scandefault)
        scan_hbox._pack_noexpand_nofill(self.scandefault_tip)
        scanadv_hbox._pack_expand_fill(self.scanadv)

        adv_box = HIGVBox()
        scanadv_align = gtk.Alignment(0.5, 0.5, 1, 1)
        scanadv_align.set_padding(6, 0, 12, 0)
        scanname_box = HIGHBox()
        scanname_box._pack_noexpand_nofill(self.scan_name_lbl)
        scanname_box._pack_expand_fill(self.scan_name)
        scanname_box._pack_noexpand_nofill(self.cmd_wizard)
        adv_box.add(scanname_box)
        scancmd_box = HIGHBox()
        scancmd_box._pack_noexpand_nofill(self.scan_command_lbl)
        scancmd_box._pack_expand_fill(self.scan_command)
        adv_box.add(scancmd_box)

        scanadv_align.add(adv_box)
        self.scanadv.add(scanadv_align)
        # scan target
        scantarget_hbox._pack_noexpand_nofill(self.scantarget_lbl)
        scantarget_hbox._pack_expand_fill(self.scantarget)
        scantarget_hbox._pack_noexpand_nofill(self.scantarget_discovery)
        # scheduling profiles
        sched_box._pack_noexpand_nofill(self.sched_name_lbl)
        sched_box._pack_expand_fill(self.sched_name)
        sched_box._pack_noexpand_nofill(self.sched_name_edit)
        # bottom buttons
        btns_hbox.set_homogeneous(True)
        btns_hbox._pack_expand_fill(self.help)
        btns_hbox._pack_expand_fill(hig_box_space_holder())
        btns_hbox._pack_expand_fill(self.cancel)
        btns_hbox._pack_expand_fill(self.ok)


        main_vbox._pack_noexpand_nofill(header_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(invname_hbox)
        main_vbox._pack_noexpand_nofill(scan_hbox)
        main_vbox._pack_noexpand_nofill(scanadv_hbox)
        main_vbox._pack_noexpand_nofill(scantarget_hbox)
        
        if self.loaded_command and self.edit_mode:
            view_cmd_box = HIGHBox()
            view_cmd_box._pack_noexpand_nofill(gtk.Label(_("Command")))
            # XXX Why don't reuse scan_command?
            self.cmd_entry = gtk.Entry()
            self.cmd_entry.set_text(self.loaded_command)
            view_cmd_box._pack_expand_fill(self.cmd_entry)
            img_info = gtk.Image()
            img_info.set_from_stock(gtk.STOCK_INFO, gtk.ICON_SIZE_MENU)
            eb = gtk.EventBox()
            eb.add(img_info)
            self.tooltips.set_tip(eb, _("Changes in command won't be saved!"))
            view_cmd_box.pack_end(eb, False, False, 0)
            main_vbox._pack_noexpand_nofill(view_cmd_box)

        main_vbox._pack_noexpand_nofill(sched_box)
        main_vbox.pack_end(btns_hbox, False, False, 0)
        main_vbox.pack_end(gtk.HSeparator(), False, False, 0)

        self.add(main_vbox)


    # Properties
    schemawin = property(get_schemawin, set_schemawin)
    discoverywin = property(get_discoverywin, set_discoverywin)
    profile_running = property(get_profile_running, set_profile_running)


if __name__ == "__main__":
    w = NewInventory()
    w.show_all()
    w.connect('delete-event', lambda *args: gtk.main_quit())
    gtk.main()
