#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
#         Cleber Rodrigues <cleber.gnu@gmail.com>
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

import sys
import os
import os.path

from types import StringTypes
from time import time
from tempfile import mktemp

from higwidgets.higwindows import HIGMainWindow
from higwidgets.higdialogs import HIGDialog, HIGAlertDialog
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higboxes import HIGHBox, HIGVBox

from umitGUI.FileChoosers import ResultsFileChooserDialog, SaveResultsFileChooserDialog
from umitGUI.ScanNotebook import ScanNotebook, ScanNotebookPage
from umitGUI.ProfileEditor import ProfileEditor
from umitGUI.Wizard import Wizard
from umitGUI.About import About
from umitGUI.DiffCompare import DiffWindow
from umitGUI.SearchWindow import SearchWindow
from umitGUI.BugReport import BugReport

from umitCore.Paths import Path
from umitCore.UmitLogging import log
from umitCore.I18N import _
from umitCore.UmitOptionParser import option_parser
from umitCore.UmitConf import SearchConfig, is_maemo
from umitCore.UmitDB import Scans, UmitDB

root = False
try:
    if sys.platform == 'win32':
        root = True
    elif is_maemo():
        root = True
    elif os.getuid() == 0:
        root = True
except: pass


UmitMainWindow = None
hildon = None

if is_maemo():
    import hildon
    class UmitMainWindow(hildon.Window):
        def __init__(self):
            hildon.Window.__init__(self)
            self.set_resizable(False)
            self.set_border_width(0)
            self.vbox = gtk.VBox()
            self.vbox.set_border_width(0)
            self.vbox.set_spacing(0)

else:
    class UmitMainWindow(HIGMainWindow):
        def __init__(self):
            HIGMainWindow.__init__(self)
            self.vbox = gtk.VBox()


class MainWindow(UmitMainWindow):
    def __init__(self):
        UmitMainWindow.__init__(self)
        self.set_title(_("Umit"))

        self._icontheme = gtk.IconTheme()
        self.main_accel_group = gtk.AccelGroup()
        
        self.add_accel_group(self.main_accel_group)
        
        self.add(self.vbox)
        
        self.connect ('delete-event', self._exit_cb)
        self._create_ui_manager()
        self._create_menubar()
        self._create_toolbar()
        self._create_scan_notebook()
        self._verify_root()
        
        # These dialogs should be instanciated on demand
        # Unfortunately, due to a GTK bug on the filefilters (or our own
        # stupidity), we are creating/destroying them at each callback
        # invocation. sigh.
        self._profile_filechooser_dialog = None
        self._results_filechooser_dialog = None

        # Loading files passed as argument
        files = option_parser.get_open_results()
        if len(files) >= 1:
            for file in files:
                self._load(filename=file)

    def configure_focus_chain(self):
        self.vbox.set_focus_chain()

    def _verify_root(self):
        if not root:
            non_root = NonRootWarning()

    def _create_ui_manager(self):
        self.ui_manager = gtk.UIManager()
        
        # See info on ActionGroup at:
        # * http://www.pygtk.org/pygtk2reference/class-gtkactiongroup.html
        # * http://www.gtk.org/api/2.6/gtk/GtkActionGroup.html
        self.main_action_group = gtk.ActionGroup('MainActionGroup')
        
        # See info on Action at:
        # * http://www.pygtk.org/pygtk2reference/class-gtkaction.html
        # * http://www.gtk.org/api/2.6/gtk/GtkAction.html
        
        # Each action tuple can go from 1 to six fields, example:
        # ('Open Scan Results',      -> Name of the action
        #   gtk.STOCK_OPEN,          -> 
        #   _('_Open Scan Results'), -> 
        #   None,
        #   _('Open the results of a previous scan'),
        #   lambda x: True) 
        
        about_icon = None
        try: about_icon = gtk.STOCK_ABOUT
        except: pass
        
        self.main_actions = [ \
            # Top level
            ('Scan', None, _('Sc_an'), None), 
            
            ('Wizard',
                gtk.STOCK_CONVERT,
                _('_Command Wizard'),
                '<Control>i',
                _('Open nmap command constructor wizard'),
                self._wizard_cb),
            
            ('Save Scan',
                gtk.STOCK_SAVE,
                _('_Save Scan'),
                None,
                _('Save current scan results'),
                self._save_scan_results_cb),
            
            ('Open Scan',
                gtk.STOCK_OPEN,
                _('_Open Scan'),
                None,
                _('Open the results of a previous scan'),
                self._load_scan_results_cb),
                    
            
            ('Tools', None, _('_Tools'), None), 
            
            ('New Scan',
                gtk.STOCK_NEW,
                _('_New Scan'),
                "<Control>T",
                _('Create a new Scan Tab'),
                self._new_scan_cb),
            
            ('Close Scan',
                gtk.STOCK_CLOSE,
                _('Close Scan'),
                "<Control>w",
                _('Close current scan tab'),
                self._close_scan_cb),
            
            ('New Profile',
                gtk.STOCK_JUSTIFY_LEFT,
                _('New _Profile'),
                '<Control>p',
                _('Create a new scan profile'),
                self._new_scan_profile_cb),

            ('Search Scan',
                gtk.STOCK_FIND,
                _('Search Scan Results'),
                '<Control>f',
                _('Search for a scan result'),
                self._search_scan_result),
            
            ('Edit Profile',
                gtk.STOCK_PROPERTIES,
                _('_Edit Selected Profile'),
                '<Control>e',
                _('Edit selected scan profile'),
                self._edit_scan_profile_cb),
            
            ('New Profile with Selected',
                gtk.STOCK_PROPERTIES,
                _('New P_rofile with Selected'),
                '<Control>r',
                _('Use the selected scan profile to create another'),
                self._new_scan_profile_with_selected_cb),
            
            ('Quit',
                gtk.STOCK_QUIT,
                _('_Quit'),
                None,
            _('Quit this application'),
                self._exit_cb),
            
            
            # Top Level
            ('Profile', None, _('_Profile'), None),
            
            ('Compare Results',
                gtk.STOCK_DND_MULTIPLE,
                _('Compare Results'),
                "<Control>D",
                _('Compare Scan Results using Diffies'),
                self._load_diff_compare_cb),
            
            
            # Top Level
            ('Help', None, _('_Help'), None),

            ('Report a bug',
                gtk.STOCK_DIALOG_INFO,
                _('_Report a bug'),
                '<Control>b',
                _("Report a bug"),
                self._show_bug_report
                ),
            
            ('About',
                about_icon,
                _('_About'),
                '<Control>a',
                _("About UMIT"),
                self._show_about_cb
                ),
            
            ('Show Help',
                gtk.STOCK_HELP,
                _('_Help'),
                None,
                _('Shows the application help'),
                self._show_help),
            ]
        
        # See info on UIManager at:
        # * http://www.pygtk.org/pygtk2reference/class-gtkuimanager.html        
        # * http://www.gtk.org/api/2.6/gtk/GtkUIManager.html
        
        # UIManager supports UI "merging" and "unmerging". So, suppose there's
        # no scan running or scan results opened, we should have a minimal
        # interface. When we one scan running, we should "merge" the scan UI.
        # When we get multiple tabs opened, we might merge the tab UI.
        
        # This is the default, minimal UI
        self.default_ui = """<menubar>
        <menu action='Scan'>
            <menuitem action='New Scan'/>
            <menuitem action='Close Scan'/>
            <menuitem action='Save Scan'/>
            <menuitem action='Open Scan'/>
             %s
            <menuitem action='Quit'/>
        </menu>

        <menu action='Tools'>
            <menuitem action='Wizard'/>
            <menuitem action='Compare Results'/>
            <menuitem action='Search Scan'/>
         </menu>
        
        <menu action='Profile'>
            <menuitem action='New Profile'/>
            <menuitem action='New Profile with Selected'/>
            <menuitem action='Edit Profile'/>
        </menu>
        
        <menu action='Help'>
            <menuitem action='Show Help'/>
            <menuitem action='Report a bug'/>
            <menuitem action='About'/>
        </menu>
        
        </menubar>
        
        <toolbar>
            <toolitem action='New Scan'/>
            <toolitem action='Wizard'/>
            <toolitem action='Save Scan'/>
            <toolitem action='Open Scan'/>
            <separator/>
            <toolitem action='Report a bug'/>
            <toolitem action='Show Help'/>
        </toolbar>
        """
        
        self.get_recent_scans()
        
        self.main_action_group.add_actions(self.main_actions)
        
        for action in self.main_action_group.list_actions():
            action.set_accel_group(self.main_accel_group)
            action.connect_accelerator()
        
        self.ui_manager.insert_action_group(self.main_action_group, 0)
        self.ui_manager.add_ui_from_string(self.default_ui)

    def _show_bug_report(self, widget):
        bug = BugReport()
        bug.show_all()

    def _search_scan_result(self, widget):
        search_window = SearchWindow(self._load_search_result, self.scan_notebook)
        search_window.show_all()

    def _load_search_result(self, results):
        for result in results:
            if results[result][1].is_unsaved():
                for i in range(self.scan_notebook.get_n_pages()):
                    if results[result][0] == "Unsaved " + \
                    self.scan_notebook.get_nth_page(i).get_tab_label():
                        self.scan_notebook.set_current_page(i)
            else:
                page = self._load(parsed_result=results[result][1],
                              title=results[result][1].scan_name)
                page.status.set_search_loaded()

    def _close_scan_cb(self, widget, data=None):
        # data can be none, if the current page is to be closed
        if data == None:
            page_num = self.scan_notebook.get_current_page()
        # but can also be this page's content, which will be used
        # to find this page number
        else:
            page_num = self.scan_notebook.page_num(data)
        page = self.scan_notebook.get_nth_page(page_num)
        filename = None
        
        if page.status.unsaved_unchanged \
               or page.status.unsaved_changed\
               or page.status.loaded_changed:
            
            log.debug("Found changes on closing tab")
            dialog = HIGDialog(buttons=(gtk.STOCK_SAVE, gtk.RESPONSE_OK,
                            _('Close anyway'), gtk.RESPONSE_CLOSE,
                            gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            
            title = self.scan_notebook.get_tab_title(page)
            
            alert = None
            if title:
                alert = HIGEntryLabel('<b>%s "%s"</b>' % (_("Save changes on"), title))
            else:
                alert = HIGEntryLabel('<b>%s</b>' % _("Save changes"))
            
            text = HIGEntryLabel(_('The given scan has unsaved changes.\n\
What do you want to do?'))
            hbox = HIGHBox()
            hbox.set_border_width(5)
            hbox.set_spacing(12)
            
            vbox = HIGVBox()
            vbox.set_border_width(5)
            vbox.set_spacing(12)
            
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_DIALOG_QUESTION,gtk.ICON_SIZE_DIALOG)
            
            vbox.pack_start(alert)
            vbox.pack_start(text)
            hbox.pack_start(image)
            hbox.pack_start(vbox)
            
            dialog.vbox.pack_start(hbox)
            dialog.vbox.show_all()
            
            response = dialog.run()
            dialog.destroy()
            
            if response == gtk.RESPONSE_OK:
                filename = self._save_scan_results_cb(page)
                # filename = None means that user didn't saved the result
            elif response == gtk.RESPONSE_CANCEL:
                return False

            self.store_result(page, filename)
            
        elif page.status.scanning:
            log.debug("Trying to close a tab with a running scan")
            dialog = HIGDialog(buttons=(_('Close anyway'), gtk.RESPONSE_CLOSE,
                                        gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL))
            
            title = self.scan_notebook.get_tab_title(page)
            
            alert = None
            if title:
                alert = HIGEntryLabel('<b>%s "%s"</b>' % (_("Trying to close"), title))
            else:
                alert = HIGEntryLabel('<b>%s</b>' % _("Trying to close"))
            
            text = HIGEntryLabel(_('The page you are trying to close has a scan \
running at the background.\nWhat do you want to do?'))
            hbox = HIGHBox()
            hbox.set_border_width(5)
            hbox.set_spacing(12)
            
            vbox = HIGVBox()
            vbox.set_border_width(5)
            vbox.set_spacing(12)
            
            image = gtk.Image()
            image.set_from_stock(gtk.STOCK_DIALOG_WARNING, gtk.ICON_SIZE_DIALOG)
            
            vbox.pack_start(alert)
            vbox.pack_start(text)
            hbox.pack_start(image)
            hbox.pack_start(vbox)
            
            dialog.vbox.pack_start(hbox)
            dialog.vbox.show_all()
            
            response = dialog.run()
            dialog.destroy()
            
            if response == gtk.RESPONSE_CLOSE:
                page.kill_scan()
            elif response == gtk.RESPONSE_CANCEL:
                return False
        elif not page.status.empty:
            alert = HIGAlertDialog(message_format=_('Closing current Scan Tab'),
                                   secondary_text=_('Are you sure you want to close current \
Scan Tab?'),
                                   buttons=gtk.BUTTONS_OK_CANCEL,
                                   type=gtk.MESSAGE_WARNING)
            response = alert.run()
            alert.destroy()

            if response != gtk.RESPONSE_OK:
                return False
        
        page.close_tab()
        del(page)
        self.scan_notebook.remove_page(page_num)
        return True

    def store_result(self, page, filename):
        page.parsed.scan_name = self.scan_notebook.get_tab_title(page)
        
        if not filename:
            filename = mktemp()
            f = open(filename, "w")
            page.parsed.write_xml(f)
            f.close()

        search_config = SearchConfig()
        if search_config.store_results:
            try:
                log.debug(">>> Saving result into data base...")
                scan = Scans(scan_name=self.scan_notebook.get_tab_title(page),
                             nmap_xml_output=open(filename).read(),
                             date=time())
            except:
                log.debug("Error while trying to store result in Data Base!")



    def get_recent_scans(self):
        r_scans = []
        new_rscan_xml = ''
        
        try:
            recent = open(Path.recent_scans)
            r_scans = recent.readlines()

            recent.close()
        except: pass
        
        for scan in r_scans[:7]:
            scan = scan.replace('\n','')
            #print '>>> Exists:', scan, os.path.isfile(scan)
            if os.access(os.path.split(scan)[0],os.R_OK) and os.path.isfile(scan):
                
                scan = scan.replace('\n','')
                new_rscan = (scan, None, scan, None, scan, self._load_recent_scan)
                new_rscan_xml += "<menuitem action='%s'/>\n" % scan
                
                self.main_actions.append(new_rscan)
        else:
            new_rscan_xml += "<separator />\n"
        
        self.default_ui %= new_rscan_xml
    
    def _create_menubar(self):
        # Get and pack the menubar
        menubar = self.ui_manager.get_widget('/menubar')
        
        if is_maemo():
            menu = gtk.Menu()
            for child in menubar.get_children():
                child.reparent(menu)
            self.set_menu(menu)
            menubar.destroy()
            self.menubar = menu
        else:
            self.menubar = menubar
            self.vbox.pack_start(self.menubar, False, False, 0)

        self.menubar.show_all()

    def _create_toolbar(self):
        toolbar = self.ui_manager.get_widget('/toolbar')
        
        if is_maemo():
            tb = gtk.Toolbar()
            for child in toolbar.get_children():
                child.reparent(tb)
            self.add_toolbar(tb)
            self.toolbar = tb
            toolbar.destroy()
        else:
            self.toolbar = toolbar
            self.vbox.pack_start(self.toolbar, False, False, 0)

        self.toolbar.show_all()

    def _create_scan_notebook(self):
        self.scan_notebook = ScanNotebook()
        self.scan_notebook.close_scan_cb = self._close_scan_cb

        page = self._new_scan_cb()
        self.scan_notebook.show_all()

        # Applying some command line options
        target = option_parser.get_target()
        profile = option_parser.get_profile()
        nmap = option_parser.get_nmap()

        if nmap:
            page.command_toolbar.command = " ".join(nmap)
            page.start_scan_cb()

        else:
            if target:
                page.toolbar.selected_target = target

            if profile:
                page.toolbar.selected_profile = profile

            if target and profile:
                log.debug(">>> Executing scan with the given args: %s \
with %s" % (target, profile))
                page.start_scan_cb()

        if is_maemo():
            # No padding. We need space!
            self.vbox.pack_start(self.scan_notebook, True, True, 0)
        else:
            self.vbox.pack_start(self.scan_notebook, True, True, 4)

    def _create_statusbar(self):
        self.statusbar = gtk.Statusbar()
        self.vbox.pack_start(self.statusbar, False, False, 0)

    def _wizard_cb(self, widget):
        w = Wizard()
        w.set_notebook(self.scan_notebook)
        
        w.show_all()

    def _load_scan_results_cb(self, p):
        self._results_filechooser_dialog = ResultsFileChooserDialog(title=p.get_name())
        
        if (self._results_filechooser_dialog.run() == gtk.RESPONSE_OK):
            self._load(filename=self._results_filechooser_dialog.get_filename())
        
        self._results_filechooser_dialog.destroy()
        self._results_filechooser_dialog = None
    
    def _load_recent_scan(self, widget):
        self._load(widget.get_name())

    def _verify_page_usage(self, page):
        """Verifies if given page is empty and can be used to load a result, or
        if it's not empty and shouldn't be used to load a result. Returns True, if
        it's ok to be used, and False if not.
        """
        if page == None \
               or page.status.saved\
               or page.status.unsaved_unchanged\
               or page.status.unsaved_changed\
               or page.status.loaded_unchanged\
               or page.status.loaded_changed\
               or page.status.parsing_result\
               or page.status.scanning\
               or page.status.search_loaded:
            return False
        else:
            return True
    
    def _load(self, filename=None, parsed_result=None, title=None):
        scan_page = None
        
        if filename or parsed_result:
            current_page = self.scan_notebook.get_nth_page(self.scan_notebook.get_current_page())

            if self._verify_page_usage(current_page):
                log.debug(">>> Loading inside current scan page.")
                scan_page = current_page
            else:
                log.debug(">>> Creating a new page to load it.")
                scan_page = self._new_scan_cb()

            log.debug(">>> Enabling page widgets")
            scan_page.enable_widgets()

        if filename and os.access(filename, os.R_OK):
            # Load scan result from file
            log.debug(">>> Loading file: %s" % filename)
            log.debug(">>> Permissions to access file? %s" % os.access(filename, os.R_OK))

            # Parse result
            f = open(filename)
            scan_page.parse_result(f)
            scan_page.saved_filename = filename
            
            # Closing file to avoid problems with file descriptors
            f.close()

            log.debug(">>> Setting tab label")
            self.scan_notebook.set_tab_title(scan_page, title)
            
        elif parsed_result:
            # Load scan result from parsed object
            scan_page.load_from_parsed_result(parsed_result)

            log.debug(">>> Setting tab label")
            self.scan_notebook.set_tab_title(scan_page, None)

        elif filename and not os.access(filename, os.R_OK):
            alert = HIGAlertDialog(message_format=_('Permission denied'),
                                   secondary_text=_('Don\'t have read access to the path'))
            alert.run()
            alert.destroy()
            return 
        else:
            alert = HIGAlertDialog(message_format=_('Could not load result'),
                                   secondary_text=_('An unidentified error occouried and the \
scan result was unable to be loaded properly.'))
            alert.run()
            alert.destroy()
            return 

        log.debug(">>> Setting flag that defines that there is no changes at \
this scan result yet")
        scan_page.changes = False
        scan_page.status.set_loaded_unchanged()

        log.debug(">>> Showing loaded result page")
        self.scan_notebook.set_current_page(self.scan_notebook.get_n_pages()-1)
        return scan_page
    
    def _save_scan_results_cb(self, saving_page):
        current_page = self.scan_notebook.get_nth_page(self.scan_notebook.get_current_page())

        try:
            status = current_page.status
        except:
            alert = HIGAlertDialog(message_format=_('No scan tab'),
                                   secondary_text=_('There is no scan tab or scan result \
been shown. Run a scan and then try to save it.'))
            alert.run()
            alert.destroy()
            return None


        log.debug(">>> Page status: %s" % current_page.status.status)

        if status.empty or status.unknown:    # EMPTY or UNKNOWN
            # Show a dialog saying that there is nothing to be saved
            alert = HIGAlertDialog(message_format=_('Nothing to save'),
                                   secondary_text=_('No scan on this tab. Start a scan an \
then try again'))
            alert.run()
            alert.destroy()

        elif status.scan_failed:
            alert = HIGAlertDialog(message_format=_('Nothing to save'),
                                   secondary_text=_('The scan has failed! There is nothing \
to be saved.'))
            alert.run()
            alert.destroy()

        elif status.parsing_result:    # PARSING_RESULT
            # Say that the result is been parsed
            alert = HIGAlertDialog(message_format=_('Parsing the result'),
                                   secondary_text=_('The result is still been parsed. \
You can not save the result yet.'))
            alert.run()
            alert.destroy()

        elif status.scanning:    # SCANNING
            # Say that the scan is still running
            alert = HIGAlertDialog(message_format=_('Scan is running'),
                                   secondary_text=_('The scan process is not finished yet. \
Wait until the scan is finished and then try to save it again.'))
            alert.run()
            alert.destroy()

        elif status.unsaved_unchanged or status.unsaved_changed or status.search_loaded:
            # UNSAVED_UNCHANGED and UNSAVED_CHANGED
            # Show the dialog to choose the path to save scan result
            self._save_results_filechooser_dialog = SaveResultsFileChooserDialog(\
                                                                    title=_('Save Scan'))    
            response = self._save_results_filechooser_dialog.run()

            filename = None
            if (response == gtk.RESPONSE_OK):
                filename = self._save_results_filechooser_dialog.get_filename()
                # add .usr to filename if there is no other extension
                if filename.find('.') == -1:
                    filename += ".usr"
                self._save(current_page, filename)
                
            self._save_results_filechooser_dialog.destroy()
            self._save_results_filechooser_dialog = None

            return filename

        elif status.loaded_changed:    # LOADED_CHANGED
            # Save the current result at the loaded file
            self._save(current_page, current_page.saved_filename)
        elif status.saved or status.loaded_unchanged:
            pass
        else:    # UNDEFINED status
            alert = HIGAlertDialog(message_format=_('Nothing to save'),
                                   secondary_text=_('No scan on this tab. Start a scan \
 an then try again'))
            alert.run()
            alert.destroy()

    def _show_about_cb(self, widget):
        a = About()
        a.show_all()
    
    def _save(self, saving_page, saved_filename):
        log.debug(">>> File been saved: %s" % saved_filename)
        if os.access(os.path.split(saved_filename)[0], os.W_OK):
            f = None
            try:
                f = open(saved_filename, 'w')
            except:
                alert = HIGAlertDialog(message_format=_('Can\'t save file'),
                            secondary_text=_('Can\'t open file to write'))
                alert.run()
                alert.destroy()
            else:
                saving_page.saved = True
                saving_page.changes = False
                saving_page.saved_filename = saved_filename
                saving_page.collect_umit_info()

                log.debug(">>> Page saved? %s" % saving_page.status.saved)
                log.debug(">>> Changes on page? %s" % saving_page.status.status)
                log.debug(">>> File to be saved at: %s" % saving_page.saved_filename)
                
                saving_page.parsed.write_xml(f)

                # Closing file to avoid problems with file descriptors
                f.close()

                # Setting page status to saved
                saving_page.status.set_saved()

                # Saving recent scan information
                rs = ['']
                try:
                    recent = open(Path.recent_scans)
                    rs = recent.readlines()

                    recent.close()
                except:
                    return None
                else:
                    rs.insert(0, saved_filename+'\n')

                try:
                    recent = open(Path.recent_scans,'w')
                    recent.writelines(rs[:7])

                    recent.close()
                except:
                    pass
                
        else:
            alert = HIGAlertDialog(message_format=_('Permission denied'),
                                   secondary_text=_('Don\'t have write access to this path.'))
            alert.run()
            alert.destroy()
    
    def _new_scan_cb(self, widget=None, data=None):
        """Append a new ScanNotebookPage to ScanNotebook
        New tab properties:
        - Empty
        - Disabled widgets
        - Ready to start a new scan
        - Untitled scan
        """
        return self.scan_notebook.add_scan_page(data)

    def _new_scan_profile_cb(self, p):
        pe = ProfileEditor()
        pe.set_notebook(self.scan_notebook)
        
        pe.show_all()
    
    def _edit_scan_profile_cb(self, p):
        page = self.scan_notebook.get_nth_page\
                (self.scan_notebook.get_current_page())
        profile = page.toolbar.selected_profile
        
        pe = ProfileEditor(profile)
        pe.set_notebook(self.scan_notebook)
        
        pe.show_all()
    
    def _new_scan_profile_with_selected_cb(self, p):
        page = self.scan_notebook.get_nth_page(self.scan_notebook.get_current_page())
        profile = page.toolbar.selected_profile
        
        pe = ProfileEditor(profile, delete=False)
        pe.clean_profile_info()
        pe.set_notebook(self.scan_notebook)
        
        pe.show_all()
    
    def _alert_with_action_name_cb(self, p):
        d = HIGAlertDialog(parent=self,
                           message_format=p.get_name(),
                           secondary_text=_("The text above is this action's name"))
        d.run()
        d.destroy()

    def _show_help(self, action):
        import webbrowser

        new = 0
        if sys.hexversion >= 0x2050000:
            new = 2

        webbrowser.open("file://%s" % os.path.join(Path.docs_dir,
                                                   "help.html"), new=new)
        

    def _exit_cb (self, widget=None, extra=None):
        for page in self.scan_notebook.get_children():
            if not self._close_scan_cb(page):
                self.show_all()
                return True
        else:
            # Cleaning up data base
            UmitDB().cleanup(SearchConfig().converted_save_time)
            
            gtk.main_quit()

    def _load_diff_compare_cb (self, widget=None, extra=None):
        # We must change this test dict
        # This dict has the following sintax:
        # key = Scan name
        # value = nmap output in string format
        dic = {}
        
        for i in range(self.scan_notebook.get_n_pages()):
            page = self.scan_notebook.get_nth_page(i)
            scan_name = self.scan_notebook.get_tab_title(page)

            if not scan_name:
                scan_name = _("Scan ") + str(i+1)
            
            dic[scan_name] = page.parsed
        
        self.diff_window = DiffWindow(dic)
        
        self.diff_window.show_all()


class NonRootWarning (HIGAlertDialog):
    def __init__(self):
        warning_text = _('''You are trying to run UMIT with a non-root user!\n
Some nmap options need root privileges to work.''')
        
        HIGAlertDialog.__init__(self, message_format=_('Non root user'),
                                secondary_text=warning_text)

        self.run()
        self.destroy()


if __name__ == '__main__':
    w = MainWindow()
    w.show_all()
    gtk.main()
