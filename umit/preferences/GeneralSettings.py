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
from higwidgets.higbuttons import HIGButton
from umit.preferences.FramesHIG import *


from umit.core.UmitLogging import log
from umit.core.I18N import _
from umit.core.UmitConf import GeneralSettingsConf

from umit.core.UserConf import * 
from umit.core.BasePaths import base_paths


general_settings = GeneralSettingsConf()



class GeneralSettings(TabBox, object):
    """
    General Settings
    - Splash enable/disable
    - Warnings
    - Erros, log, configure bugreport
    - Autosave: clean up, define folder etc
    - Define Nmap Command
    """

    def __init__(self, name):
        TabBox.__init__(self, name)


    def _create_widgets(self):
        """
        Design all
        """
        # Create general widgets
        self._create_widgets_common()
        self._create_widgets_autosave()
        self._create_widgets_error()
        # Packing main section
        self.pack_start(self._box_common, False, False)
        self.pack_start(self._box_error_frame, False, False)
        self.pack_start(self._box_save_frame, False, False)
        self._box_error_frame.set_shadow_type(gtk.SHADOW_NONE)
        self._box_error_frame.set_shadow_type(gtk.SHADOW_NONE)


        # Settings Values

        self.splash = general_settings.splash
        self.warnings_extensions = general_settings.warnings_extensions
        self.silent_root = general_settings.silent_root
        self.crash_report = general_settings.crash_report
        self.log = general_settings.log
        self.log_file = general_settings.log_file
        self.warnings_save = general_settings.warnings_save

        self._connect_events()
    def _create_widgets_common(self):
        """ generally tab """
        self._box_common = HIGVBox() # pack main section
        self.__check_splash = gtk.CheckButton(_('Enable Splash on start'))
        self.__check_silent_root = gtk.CheckButton(\
            _('Silent Warning Non-Root'))
        self.__check_warning_extensions = gtk.CheckButton(\
            _('Set/Check extensions - Windows only'))
        self._box_common.pack_start(self.__check_splash, False, False)
        #self._box_common.pack_start(self.__check_warning_extensions, False, \
        #                            False)
        self._box_common.pack_start(self.__check_silent_root, False, False)
        self.__label_nmap = HIGEntryLabel(_('Nmap Command'))
        self.__entry_nmap = HIGTextEntry()
        # Files usr saved on predefined directory:
        self.__label_path = HIGEntryLabel(_('Nmap Command'))
        self.__entry_path = HIGTextEntry()
        self.__button_path = HIGButton(_('Choose'))
        self.__box_path = HIGHBox()
        self.__box_path.pack_start(self.__label_path, False, False)
        self.__box_path.pack_end(self.__button_path, False, False)

        self._box_common.set_border_width(0)




    def _create_widgets_error(self):

        # Create Widgets
        self._box_error_frame = HIGFrame('Error')

        self._box_error = HIGTable(5, 2)
        self._box_error.set_border_width(10)
        self._box_error_frame.add(self._box_error)
        self.__crash_report = gtk.CheckButton(_('Enable Crash Report'))
        # Radio Button List
        self.__log_no = gtk.RadioButton(None, _('No log'))
        self.__log_terminal = gtk.RadioButton(self.__log_no, _('Enable log in terminal'))
        self.__log_file = gtk.RadioButton(self.__log_terminal,\
                                         _('Enable log file'))

        self.__log_file_label = HIGEntryLabel(_('Log file'))
        self.__log_file_entry = HIGTextEntry()
        self.__log_file_entry.set_editable(False)
        # FIXME: Do default file ~/.umit/umit.log
        self.__log_file_browser = HIGButton(_('Browse file'), \
                                            gtk.STOCK_DIRECTORY)

        tmpbox = HIGHBox()
        tmpbox.pack_start(self.__log_file_entry, False, False)
        tmpbox.pack_start(self.__log_file_browser, False, False)


        # attach table
        self._box_error.attach(self.__crash_report, 0,1,0,1,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
        self._box_error.attach(self.__log_no, 0,1,1,2,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
        self._box_error.attach(self.__log_terminal, 0,1,2,3,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
        self._box_error.attach(self.__log_file, 0,1,3,4,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
        self._box_error.attach(self.__log_file_label, 0,1,4,5,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
        self._box_error.attach(tmpbox, 1,2,4,5,\
                               gtk.FILL|gtk.EXPAND| gtk.SHRINK, gtk.FILL)
    def _create_widgets_autosave(self):

        # Create Widgets
        self._box_save_frame = HIGFrame('Auto-save')

        self._box_save = HIGVBox()
        self._box_save_frame.add(self._box_save)
        self._box_save.set_border_width(10)

        self._warnings_save = gtk.CheckButton(
            _('Enable warnings without saving'))
        self._clean_b = HIGButton(_('Delete saved files'), gtk.STOCK_CLEAR)
        self._clean_b_box = HIGHBox()
        self._clean_b_box.pack_start(self._clean_b, False, True)

        # pack

        self._box_save.pack_start(self._warnings_save, False, False)
        self._box_save.pack_start(self._clean_b_box, False, False)
    def _connect_events(self):
        """
        connect call backs
        """

        self.__check_splash.connect('toggled', self.update_splash)
        self.__check_silent_root.connect('toggled', self.update_silent_root)
        self.__crash_report.connect('toggled', self.update_crash_report)


        self.__log_file.connect('toggled', self.update_log)
        self.__log_file.connect('toggled', self.update_log_file)
        self.__log_terminal.connect('toggled', self.update_log)
        self.__log_no.connect('toggled', self.update_log)

        self.__log_file_browser.connect('clicked', self.read_file)
        self.__log_file_entry.connect('changed', self.update_log_file_text)

        self._warnings_save.connect('toggled', self.update_save_warn)
        
        self._clean_b.connect('clicked', self.delete_files)
        
        self.update_log_file(None)
    # Callbacks
    def delete_files(self, widget):
        # NOTE: This method should be adapted in umit.core.UserConf
        # Creating an empty recent_scans file
        
        log.debug('>>> Reset store files:  -  %s' % base_paths['user_dir'])

        reset_user_dir(base_paths['user_dir'])
        
    
    def update_save_warn(self, widget):
        general_settings.warnings_save = self.warnings_save

    def read_file(self, widget):
        dialog = gtk.FileChooserDialog("Open..",
                                       None,
                                       gtk.FILE_CHOOSER_ACTION_SAVE,
                                       (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                        gtk.STOCK_SAVE_AS, gtk.RESPONSE_OK))
        dialog.set_default_response(gtk.RESPONSE_OK)
        response = dialog.run()
        if response == gtk.RESPONSE_OK:
            # Get name of file
            self.__log_file_entry.set_text(dialog.get_filename())
        dialog.destroy()

    def update_crash_report(self, widget):
        general_settings.crash_report = self.crash_report
    def update_splash(self, widget):
        general_settings.splash = self.splash
    def update_silent_root(self, widget):
        general_settings.silent_root = self.silent_root
    def update_log_file_text(self, widget):
        general_settings.log_file = self.log_file
    def update_log_file(self, widget):
        if not self.__log_file.get_active():
            self.__log_file_active(False)
        else:
            self.__log_file_active(True)
    def update_log(self, widget):
        """ Verify if is enable, if it is not enable nothing to do """
        if not widget.get_active():
            return
        # Widget is enable.
        ## But which is enable?

        # Setting kind of log
        if widget == self.__log_no:
            general_settings.log = "None"
        elif widget == self.__log_terminal:
            general_settings.log = "Debug"
        elif widget == self.__log_file:
            general_settings.log = "File"


    # API
    def get_splash(self):
        return self.__check_splash.get_active()
    def set_splash(self, splash):
        self.__check_splash.set_active(splash)

    def set_warnings_extensions(self, extensions):
        self.__check_warning_extensions.set_active(extensions)
    def get_warnings_extensions(self):
        return self.__check_warning_extensions.get_active()
    def set_silent_root(self, root):
        self.__check_silent_root.set_active(root)
    def get_silent_root(self):
        return self.__check_silent_root.get_active()


    def set_crash_report(self, crash):
        self.__crash_report.set_active(crash)
    def get_crash_report(self):
        return self.__crash_report.get_active()

    def get_log(self):
        """
        filter a str with None, Debug or File
        return: int (means 0 - No debug, 1 - debug, 2 - debug file)
        """
        if self.__log_no.get_active():
            return "None"
        elif self.__log_terminal.get_active():
            return "Debug"
        elif self.__log_file.get_active():
            return "File"
        else:
            raise LogException()



    def set_log(self, log):
        if log == "None":
            self.__log_no.set_active(True)
        elif log == "Debug":
            self.__log_terminal.set_active(True)
        elif log == "File":
            self.__log_file.set_active(True)


    def __log_file_active(self, bool):
        self.__log_file_label.set_sensitive(bool)
        self.__log_file_entry.set_sensitive(bool)
        self.__log_file_browser.set_sensitive(bool)

    def set_log_file(self, filename):
        self.__log_file_entry.set_text(filename)
    def get_log_file(self):
        return self.__log_file_entry.get_text()

    def set_warnings_save(self, save):
        self._warnings_save.set_active(save)
    def get_warnings_save(self):
        return self._warnings_save.get_active()

    # Propertys
    splash = property(get_splash, set_splash)
    warnings_extensions = property(get_warnings_extensions, \
                                   set_warnings_extensions)
    silent_root = property(get_silent_root, set_silent_root)
    crash_report = property(get_crash_report, set_crash_report)
    log = property(get_log, set_log)
    log_file = property(get_log_file, set_log_file)
    warnings_save = property(get_warnings_save, set_warnings_save)


class LogException(Exception):
    def __init__(self):
        Exception.__init__(_('Log Exception'))
