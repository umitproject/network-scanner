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
from umit.core.UmitConf import CommandProfile
from umit.core.CronParser import CronParser
from umit.core.Utils import open_url_as

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higframe import HIGFrame
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog

from umit.gui.ProfileCombo import ProfileCombo
from umit.gui.FileChoosers import DirectoryChooserDialog
from umit.gui.Help import show_help

pixmaps_dir = Path.pixmaps_dir
    
if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'wizard_logo.png')
else:
    logo = None

class SchedSchemaEditor(HIGWindow):
    """
    Scheduler Schemas Editor
    """
    
    def __init__(self, daddy=None):
        HIGWindow.__init__(self)

        self.daddy = daddy
        self.wtitle = _("Scan Scheduler Editor")
        
        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # schemas name
        self.schema_name_lbl = HIGEntryLabel(_("Schema Name"))
        self.schema_name = gtk.combo_box_entry_new_text()
        self.schema_name.connect('changed', self._check_schema)
        # target and scan profiles
        #self.target_lbl = HIGEntryLabel(_("Target"))
        #self.target = gtk.Entry()
        self.scan_name_lbl = HIGEntryLabel(_("Scan Profile"))
        self.scan_name = ProfileCombo()
        self.scan_name.update()
        self.scan_name.set_active(0)
        self.scan_name.connect('changed', self._set_scan_command)
        # scan command
        self.scan_command_lbl = HIGEntryLabel(_("Command"))
        self.scan_command = gtk.Entry()
        # scheduling profile
        self.sched_name_lbl = HIGEntryLabel(_("Scheduling Profile"))
        self.sched_name = gtk.combo_box_new_text()
        self.sched_name_edit = gtk.Button(stock=gtk.STOCK_EDIT)
        blbl = self.sched_name_edit.get_children()[0].get_children()[0].get_children()[1]
        blbl.set_text(_("Edit Profiles"))
        self.sched_name_edit.connect('clicked', self._edit_schedprofiles)
        # schema settings
        self.schema_sett_frame = HIGFrame()
        self.setting_saveto = gtk.CheckButton(_("Save outputs to"))
        self.setting_saveto_entry = gtk.Entry()
        self.setting_saveto_browse = gtk.Button(_("..."))
        self.setting_saveto_browse.connect('clicked', self._select_saveto)
        self.setting_mailto = gtk.CheckButton(_("Send output to email"))
        self.setting_mailto_entry = gtk.Entry()
        self.setting_smtp_lbl = HIGEntryLabel(_("SMTP Schema"))
        self.setting_smtp = gtk.combo_box_new_text()
        self.setting_addtoinv = gtk.CheckButton(_("Add to the Inventory"))
        self.setting_enabled = gtk.CheckButton(_("Enabled"))
        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.apply.connect('clicked', self._save_schema)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.ok = HIGButton(stock=gtk.STOCK_OK)
        self.ok.connect('clicked', self._save_schema_and_leave)
        
        self.load_smtp_schemas()
        self._set_scan_command(None)
        self.profile_running = None # no SchedProfileEditor instance is running.
        self._load_pscheds()
        self.load_schemas()
        
        self.__set_props()
        self.__do_layout()

        self.connect('destroy', self._exit)
        
    def load_smtp_schemas(self):
        """
        Load smtp profiles.
        """
        schemas = ConfigParser()
        schemas.read(Path.smtp_schemas)
        
        self.smtp_sections = [ ]
        self.setting_smtp.get_model().clear()
        for section in schemas.sections():
            self.smtp_sections.append(section)
            self.setting_smtp.append_text(section)
            
        self.setting_smtp.set_active(0)
        

    def load_schemas(self):
        """
        Load schemas profiles.
        """
        schemas = ConfigParser()
        schemas.read(Path.sched_schemas)
        
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
        schema.read(Path.sched_schemas)
        
        values = {'command':self.scan_command.set_text,
                  'saveto':self.setting_saveto_entry.set_text,
                  'mailto':self.setting_mailto_entry.set_text}
        enable = {'saveto':self.setting_saveto.set_active,
                  'mailto':self.setting_mailto.set_active}
        
        for item in schema.items(self.schema_name.get_active_text()):
            if item[0] == 'addtoinv':
                self.setting_addtoinv.set_active(int(item[1]))
                if item[1] == '2':
                    self.apply.set_sensitive(False)
                    self.ok.set_sensitive(False)
                else:
                    self.apply.set_sensitive(True)
                    self.ok.set_sensitive(True)                    
            elif item[0] == 'enabled':
                self.setting_enabled.set_active(int(item[1]))
            elif item[0] == 'profile':
                pindx = self.profiles.index(item[1])
                self.sched_name.set_active(pindx)
            elif item[0] == 'smtp':
                if item[1]:
                    pindx = self.smtp_sections.index(item[1])
                    self.setting_smtp.set_active(pindx)
            else:
                values[item[0]](item[1])
                if item[0] in ('saveto', 'mailto'):
                    if len(item[1]):
                        enable[item[0]](True)
                    else:
                        enable[item[0]](False)
            
            
    def _check_schema(self, event):
        """
        Check if current text in schema_name combobox is a schema name.
        """
        if self.schema_name.get_active_text() in self.sections: 
            # load schema
            self._load_schema()
        else:
            # reset to default values
            self.apply.set_sensitive(True)
            self.ok.set_sensitive(True)
            self.setting_addtoinv.set_active(False)
            self.setting_enabled.set_active(False)
            self.setting_mailto.set_active(False)
            self.setting_mailto_entry.set_text('')
            self.setting_saveto.set_active(False)
            self.setting_saveto_entry.set_text('')
        
        self.schema_sett_frame._set_label(self.schema_name.get_active_text() \
+ " - Settings")
            

    def _set_scan_command(self, event):
        """
        Set scan command based on chosen profile.
        """
        profile = self.scan_name.get_selected_profile()
        cmd_profile = CommandProfile()
        command = cmd_profile.get_command(profile)
        self.scan_command.set_text(command % '<target>')
        
    
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
    
    
    def _edit_schedprofiles(self, event):
        """
        Open Scheduling Profiles Editor.
        """
        if self.profile_running:
            return
        
        win = SchedProfileEditor(self, self.sched_name.get_active_text())
        win.show_all()
        self.profile_running = win
    
    
    def _select_saveto(self, event):
        """
        Select directory to save file.
        """
        dir_chooser = DirectoryChooserDialog(_("Select a directory"))
        
        dir_chooser.run()
        dir_chosen = dir_chooser.get_filename()
        dir_chooser.destroy()
        self.setting_saveto_entry.set_text(dir_chosen)
        
    
    def _save_schema(self, event):
        """
        Save current schema.
        """
        schema = self.schema_name.get_active_text()
        command = self.scan_command.get_text()
        schedule = self.sched_name.get_active_text()
        mailto = self.setting_mailto.get_active()
        
        if not schema or not schedule or not command or '<target>' in command:
            dlg = HIGAlertDialog(self, 
                                 message_format=_('Scheduling Schema - Error\
 while saving.'),
                                 secondary_text=_("There is some error in at \
least one of the following fields: \"Schema name\", \"Command\" or \"Scheduling\
 Profile\"\n\nCheck if \"Schema name\" is not empty.\nCheck if \"Command\" does\
 contain \"<target>\" on it.\nCheck if there is some \"Scheduling Profile\" \
selected."))
            
            dlg.run()
            dlg.destroy()
            return
        
        if mailto and not self.setting_smtp.get_active_text():
            dlg = HIGAlertDialog(self, 
                                 message_format=_('Scheduling Schema - Error\
 while saving.'),
                                 secondary_text=_("You need to create a \
a SMTP Schema for sending email."))
            
            dlg.run()
            dlg.destroy()
            return
        
        # check for output existance
        if self.setting_saveto.get_active() and \
           not os.path.isdir(self.setting_saveto_entry.get_text()):
            
            dlg = HIGAlertDialog(self, 
                                 message_format=_('Scheduling Schema - Error\
 while saving.'),
                                 secondary_text=_("You especified an invalid \
directory to save scans output."))
            
            dlg.run()
            dlg.destroy()
            return 
    
        # write schema to file
        s_cfg = ConfigParser()
        s_cfg.read(Path.sched_schemas)
        
        if not s_cfg.has_section(schema):
            new_sec = True
            s_cfg.add_section(schema)
        else:
            new_sec = False
            
        s_cfg.set(schema, 'profile', schedule)
        s_cfg.set(schema, 'command', command)
        if self.setting_enabled.get_active():
            s_cfg.set(schema, 'enabled', '1')
        else:
            s_cfg.set(schema, 'enabled', '0')
        if self.setting_addtoinv.get_active():
            s_cfg.set(schema, 'addtoinv', '1')
        else:
            s_cfg.set(schema, 'addtoinv', '0')
        if self.setting_saveto.get_active():
            s_cfg.set(schema, 'saveto', self.setting_saveto_entry.get_text())
        else:
            s_cfg.set(schema, 'saveto', '')
        if mailto:
            s_cfg.set(schema, 'mailto', self.setting_mailto_entry.get_text())
            s_cfg.set(schema, 'smtp', self.setting_smtp.get_active_text())
        else:
            s_cfg.set(schema, 'mailto', '')
            s_cfg.set(schema, 'smtp', '')
            
        s_cfg.write(open(Path.sched_schemas, 'w'))
        
        if new_sec:
            self.load_schemas()
            
        if self.daddy:
            self.daddy.load_schemas()
        

    def _save_schema_and_leave(self, event):
        """
        Save current schema and close editor.
        """
        self._save_schema(None)
        self._exit(None)


    def _show_help(self, event):
        """
        Show help for Scan Scheduler Editor.
        """
        show_help(self, "scheduler.html#setting-up-a-schedule")

    def __set_props(self):
        """
        Set window properties.
        """
        self.set_title(self.wtitle)
        self.set_default_size(440, -1)

    def __do_layout(self):
        """
        Layout widgets in window.
        """
        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        header_hbox = HIGHBox()
        schema_table = HIGTable()
        schedsn_hbox = HIGHBox()
        sett_table = HIGTable()
        btns_hbox = HIGHBox()

        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)
        
        # schema name
        schema_table.attach_label(self.schema_name_lbl, 0, 1, 0, 1)
        schema_table.attach_entry(self.schema_name, 1, 2, 0, 1)
        
        # target and scan profile
        schema_table.attach_label(self.scan_name_lbl, 0, 1, 1, 2)
        schema_table.attach_entry(self.scan_name, 1, 2, 1, 2)
        
        # scan command
        schema_table.attach_label(self.scan_command_lbl, 0, 1, 2, 3)
        schema_table.attach_label(self.scan_command, 1, 2, 2, 3)
        
        # scheduling profile
        schedsn_hbox._pack_expand_fill(self.sched_name)
        schedsn_hbox._pack_noexpand_nofill(self.sched_name_edit)

        schema_table.attach_label(self.sched_name_lbl, 0, 1, 3, 4)
        schema_table.attach_entry(schedsn_hbox, 1, 2, 3, 4)

        # settings frame
        settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        settings_align.set_padding(6, 0, 12, 0)
        schemasett_hbox = HIGVBox()
        
        # saveto
        sett_hbox = HIGHBox()
        sett_hbox._pack_expand_fill(self.setting_saveto_entry)
        sett_hbox._pack_noexpand_nofill(self.setting_saveto_browse)
        sett_table.attach_label(self.setting_saveto, 0, 1, 0, 1)
        sett_table.attach_entry(sett_hbox, 1, 2, 0, 1)

        # mailto, smtp
        sett_hbox = HIGHBox()
        sett_hbox._pack_expand_fill(self.setting_mailto_entry)
        sett_hbox._pack_noexpand_nofill(self.setting_smtp_lbl)
        sett_hbox._pack_expand_fill(self.setting_smtp)
        sett_table.attach_label(self.setting_mailto, 0, 1, 1, 2)
        sett_table.attach_entry(sett_hbox, 1, 2, 1, 2)
        schemasett_hbox._pack_noexpand_nofill(sett_table)

        # add to inventory
        sett_hbox = HIGHBox()
        sett_hbox._pack_noexpand_nofill(self.setting_addtoinv)
        schemasett_hbox._pack_noexpand_nofill(sett_hbox)

        # enabled/disabled
        sett_hbox = HIGHBox()
        sett_hbox._pack_noexpand_nofill(self.setting_enabled)
        schemasett_hbox._pack_noexpand_nofill(sett_hbox) 
        settings_align.add(schemasett_hbox)

        self.schema_sett_frame.add(settings_align)
        
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
        main_vbox._pack_noexpand_nofill(self.schema_sett_frame)
        main_vbox.pack_end(btns_hbox, False, False, 0)
        
        self.add(main_vbox)


    def _exit(self, event):
        """
        Close current and window and profile editor if it is running.
        """
        if self.profile_running:
            self.profile_running._exit(None)
        
        if self.daddy:
            self.daddy.schemawin = None
            
        self.destroy()
        

    def _get_profile_running(self):
        """
        Get profile editor running instance.
        """
        return self.__profilerunning
    
    
    def _set_profile_running(self, running):
        """
        Set profile editor instance.
        """
        self.__profilerunning = running


    # Properties
    profile_running = property(_get_profile_running, _set_profile_running)


class SchedProfileEditor(HIGWindow):
    """
    Scheduling Profiles Editor
    """
    
    def __init__(self, daddy, profile=None):
        HIGWindow.__init__(self)
        self.daddy = daddy
        
        self.wtitle = _("Scheduling Profiles Editor")
        self.start_profile = profile
        
        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # profiles name
        self.schedp_name_lbl = HIGEntryLabel(_("Scheduling Profile"))
        self.schedp_name = gtk.combo_box_entry_new_text()
        self.schedp_name.connect('changed', self._check_profile)
        # cron format
        self.cron_frame = HIGFrame(_("Schedule"))
        self.cron_minute_lbl = HIGEntryLabel(_("Minute"))
        self.cron_minute = gtk.Entry()
        self.cron_hour_lbl = HIGEntryLabel(_("Hour"))
        self.cron_hour = gtk.Entry()
        self.cron_day_lbl = HIGEntryLabel(_("Day of month"))
        self.cron_day = gtk.Entry()
        self.cron_month_lbl = HIGEntryLabel(_("Month"))
        self.cron_month = gtk.Entry()
        self.cron_weekday_lbl = HIGEntryLabel(_("Weekday"))
        self.cron_weekday = gtk.Entry()
        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.apply.connect('clicked', self._save_profile)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.ok = HIGButton(stock=gtk.STOCK_OK)
        self.ok.connect('clicked', self._save_profile_and_leave)

        self.load_profiles()
        self.__set_props()
        self.__do_layout()
        
        self.connect('destroy', self._exit)


    def load_profiles(self):
        """
        Load scheduling profiles.
        """
        profiles = ConfigParser()
        profiles.read(Path.sched_profiles)
        
        self.sections = [ ]
        ind = 0
        for indx, section in enumerate(profiles.sections()):
            self.sections.append(section)
            self.schedp_name.append_text(section)
            if section == self.start_profile:
                ind = indx
            
        self.schedp_name.set_active(ind)

        self._check_profile(None)

    def _load_profile(self):
        """
        Load current set schedule profile.
        """
        profile = ConfigParser()
        profile.read(Path.sched_profiles)
        
        values = {'minute':self.cron_minute.set_text,
                  'hour':self.cron_hour.set_text,
                  'day':self.cron_day.set_text,
                  'month':self.cron_month.set_text,
                  'weekday':self.cron_weekday.set_text}
        
        for item in profile.items(self.schedp_name.get_active_text()):
            values[item[0]](item[1])
        

    def _check_profile(self, event):
        """
        Check if current text in schedp_name combobox is a profile name.
        """
        if self.schedp_name.get_active_text() in self.sections:
            self._load_profile()
        else:
            self.cron_minute.set_text('')
            self.cron_hour.set_text('')
            self.cron_day.set_text('')
            self.cron_month.set_text('')
            self.cron_weekday.set_text('')
        

    def _save_profile(self, event):
        """
        Save scheduling profile.
        """
        pname = self.schedp_name.get_active_text()
        if not len(pname):
            dlg = HIGAlertDialog(self, 
                                 message_format=_('Scheduling Profile - Error \
while saving'),
                                 secondary_text=_("You need to specify a name \
for Profile."))
            dlg.run()
            dlg.destroy()
            return
        
        parser = CronParser()
        minute = self.cron_minute.get_text()
        hour = self.cron_hour.get_text()
        day = self.cron_day.get_text()
        month = self.cron_month.get_text()
        weekday = self.cron_weekday.get_text()
        try:
            parser.parse_minute(minute)
            parser.parse_hour(hour)
            parser.parse_day(day)
            parser.parse_month(month)
            parser.parse_weekday(weekday)
        except Exception, e:
            dlg = HIGAlertDialog(self, 
                                 message_format=_('Scheduling Profile - Error \
while saving'),
                                 secondary_text=_("Check your cron syntax and \
try to save again."))
            dlg.run()
            dlg.destroy()
            return
        
        # write profile to file
        p_cfg = ConfigParser()
        p_cfg.read(Path.sched_profiles)
        
        
        if not p_cfg.has_section(pname):
            new_sec = True
            p_cfg.add_section(pname)
        else:
            new_sec = False
            
        p_cfg.set(pname, 'minute', minute)
        p_cfg.set(pname, 'hour', hour)
        p_cfg.set(pname, 'day', day)
        p_cfg.set(pname, 'month', month)
        p_cfg.set(pname, 'weekday', weekday)
            
        p_cfg.write(open(Path.sched_profiles, 'w'))
        
        if new_sec: # update daddy scheduling profiles list
            self.daddy._load_pscheds()


    def _save_profile_and_leave(self, event):
        """
        Save scheduling profile and leave.
        """
        self._save_profile(None)
        self._exit(None)


    def _show_help(self, event):
        """
        Show help for Scheduling Profiles.
        """
        show_help(self,"scheduler.html#creating-a-new-scheduling-profile")


    def __set_props(self):
        """
        Set window properties
        """
        self.set_title(self.wtitle)


    def __do_layout(self):
        """
        Layout window widgets.
        """
        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        header_hbox = HIGHBox()
        schedp_hbox = HIGHBox()
        cron_box = HIGVBox()
        cron_table = HIGTable(5, 2)
        btns_hbox = HIGHBox()
        
        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)
        
        schedp_hbox._pack_noexpand_nofill(self.schedp_name_lbl)
        schedp_hbox._pack_expand_fill(self.schedp_name)
                
        # cron format
        settings_align = gtk.Alignment(0.5, 0.5, 1, 1)
        settings_align.set_padding(6, 0, 12, 0)
        
        cron_table.attach(self.cron_minute_lbl, 0, 1, 0, 1)
        cron_table.attach(self.cron_minute, 1, 2, 0, 1)
        cron_table.attach(self.cron_hour_lbl, 0, 1, 1, 2)
        cron_table.attach(self.cron_hour, 1, 2, 1, 2)
        cron_table.attach(self.cron_day_lbl, 0, 1, 2, 3)
        cron_table.attach(self.cron_day, 1, 2, 2, 3)
        cron_table.attach(self.cron_month_lbl, 0, 1, 3, 4)
        cron_table.attach(self.cron_month, 1, 2, 3, 4)
        cron_table.attach(self.cron_weekday_lbl, 0, 1, 4, 5)
        cron_table.attach(self.cron_weekday, 1, 2, 4, 5)

        cron_box._pack_noexpand_nofill(cron_table)
        settings_align.add(cron_box)
        self.cron_frame.add(settings_align)
        
        # bottom buttons
        btns_hbox.set_homogeneous(True)
        btns_hbox._pack_expand_fill(self.help)
        btns_hbox._pack_expand_fill(hig_box_space_holder())
        btns_hbox._pack_expand_fill(self.apply)
        btns_hbox._pack_expand_fill(self.cancel)
        btns_hbox._pack_expand_fill(self.ok)
        
        main_vbox._pack_noexpand_nofill(header_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(schedp_hbox)
        main_vbox._pack_noexpand_nofill(self.cron_frame)
        main_vbox.pack_end(btns_hbox, False, False, 0)
        self.add(main_vbox)
        
        
    def _exit(self, event):
        """
        Close window and change profile editor instance on daddy.
        """
        self.daddy.profile_running = None
        self.destroy()
        

if __name__ == "__main__":
    w = SchedSchemaEditor()
    w.show_all()
    w.connect('destroy', gtk.main_quit)
    gtk.main()
    
