# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
#         Diogo Pinheiro <diogormpinheiro@gmail.com>
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

import os, os.path
import sys
import threading

#from umit.core.Paths import Path
#Path.set_umit_conf(os.path.join(os.path.split(__file__)[0], 'config', 'umit.conf'))

from umit.core.I18N import _
from umit.core.UmitConf import NSEManagerConfig
from umit.core.Paths import Path
from umit.gui.FileChoosers import DirectoryChooserDialog, AllFilesFileChooserDialog
from umit.gui.BugReport import BugReport

import gobject
import gtk
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higentries import HIGTextEntry
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGDialog
from higwidgets.higframe import HIGFrame
from higwidgets.higprogressbars import HIGLabeledProgressBar
from higwidgets.higwindows import HIGWindow, HIGMainWindow
from higwidgets.higlabels import HIGEntryLabel, HIGSectionLabel

from NmapFetch import NmapFetchScripts
from nseBase import ScriptBase, ScriptItem
from nseConfig import ScriptConfig

from ScriptWindow import ScriptWindow
from ScriptEditor import ScriptEditorWindow, get_templates, DEFAULT_TEMPLATE_PATH
from Utils import *


# Filters
class NoneFilter(object):
    def get_name(self):
        return "None"

    def __call__(self, script):
        return False
    
class AllFilter(object):
    def get_name(self):
        return "<b>" + _("All") + "</b>"
    
    def __call__(self, script):
        return True

class CategoryFilter(object):
    def __init__(self, category):
        self.category = category

    def get_name(self):
        return self.category

    def __call__(self, script):
        return self.category in  script.categories

class SearchFilter(object):
    def __init__(self, pattern):
        self.pattern = pattern

    def get_name(self):
        return "<i>" + _("Search") + " '" + self.pattern + "'</i>"

    def __call__(self, script):
        text = "\n".join([
            script.name,
            script.id,
            script.description,
            script.type,
            script.author,
            script.license,
            ",".join(script.categories)
            ])
        return self.pattern.lower() in text.lower()
    
# GUI classes
class StatusPixbuf(object):
    def __init__(self):
        self.pixbufs = dict(
            [(ScriptItem.STATE_NOT_INSTALLED, 'notinstalled'),
            (ScriptItem.STATE_INSTALLED, 'installed'),
            (ScriptItem.STATE_UPGRADABLE, 'upgradable')]
        )
        self.revers = dict([(v, k) for k, v in self.pixbufs.items()])

    def get_status_pixbuf(self, item, script):
        return self.pixbufs[item.get_state()]

    def compare(self, model, it1, it2, column):
        # FIX: 'get' are workaround for strange behavior (px2 == None) when appends new rows
        state1 = self.revers.get(model[it1][column], -1)
        state2 = self.revers.get(model[it2][column], -1)
        return state1.__cmp__(state2)

_status_pixbuf = StatusPixbuf()

class ScriptManagerWindow(ScriptWindow):
    columns_dict = {
        'I' : (gtk.CellRendererPixbuf, str, _status_pixbuf.get_status_pixbuf),
        'Name' : (gtk.CellRendererText, str, lambda i, s: s.name),
        'ID': (gtk.CellRendererText, str, lambda i, s: s.id),
        'Description': (gtk.CellRendererText, str, lambda i, s: s.description),
        'Type'  : (gtk.CellRendererText, str, lambda i, s: s.type),
        'Author' : (gtk.CellRendererText, str, lambda i, s: s.author),
        'License' : (gtk.CellRendererText, str, lambda i, s: s.license),
        'Categories' : (gtk.CellRendererText, str, lambda i, s: ",".join(s.categories)),
        'Rule' : (gtk.CellRendererText, str, lambda i, s: s.rule),
        'Version' : (gtk.CellRendererText, str, lambda i, s: "%d.%d.%d" % s.version),
        'Path' : (gtk.CellRendererText, str, lambda i, s: s.path),
        'URL' : (gtk.CellRendererText, str, lambda i, s: s.url),
        'Size' : (gtk.CellRendererText, int, lambda i, s: s.size),
        'MD5' : (gtk.CellRendererText, str, lambda i, s: s.md5),
        'SHA1' : (gtk.CellRendererText, str, lambda i, s: s.sha1),
        'GPG' : (gtk.CellRendererText, str, lambda i, s: s.gpg)
        }
    
    def __init__(self):
        ScriptWindow.__init__(self)

	print 'ScriptManager: load preferences'
        self.preferences = NSEManagerConfig()
        # update to full column list
        columns_order = self.preferences.columns_order
        columns_order.extend(set(self.columns_dict.keys()) - set(columns_order))
        self.preferences.columns_order = columns_order

        self.config = ScriptConfig()
        self.config.load()
        self.base = ScriptBase(self.config)
        self.base.load()
        self.search_filter = None
        
        self.set_title(_("Script Manager"))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_size_request(600, 400)
        self.create_widgets()
        self.update_model(0)

    def create_widgets(self):
        # ui_manager
        actions = [
            ('Script', None, _('_Script'), None),

            ('New', gtk.STOCK_NEW,
             _('New'), "<Ctrl>N",
             _('Create new script file'), self._new_file_cb),

            ('New Wizard', gtk.STOCK_NEW,
             _('_New Wizard...'), "",
             _('Create new script file with wizard'), self._new_wizard_file_cb),

            ('Install', gtk.STOCK_CONVERT,
             _('_Install'), "<Control>I",
             _('Install script from site'), self._install_cb),

            ('Upgrade', gtk.STOCK_EXECUTE,
             _('_Upgrade'), "<Control>U",
             _('Upgrade script to newest version'), self._upgrade_cb),

            ('Remove', gtk.STOCK_DELETE,
             _('_Remove'), "<Control>R",
             _('Remove script from computer'), self._remove_cb),

            ('Install All', gtk.STOCK_CONVERT,
             _('Install All'), None,
             _('Install all new scripts from site'), self._install_all_cb),

            ('Upgrade All', gtk.STOCK_EXECUTE,
             _('Upgrade All'), None,
             _('Upgrade all script to newest versions'), self._upgrade_all_cb),

            ('Tools', None, _('_Tools'), None),

            ('Add Source', gtk.STOCK_ADD,
             _('_Add Source...'), "<Control>A",
             _('Add new source to configuration'), self._add_source_cb),

            ('Quit', gtk.STOCK_QUIT,
             _('_Quit'), "<Ctrl>Q",
             _('Quit from Script Manager'), self._quit_cb),
	    
	    ('Edit Templates', gtk.STOCK_PREFERENCES,
             _('_Edit Templates'), None,
             _('Edit User Templates'), self._templates_cb),

            ('View', None, _('_View'), None),

            ('Settings', None, _('Se_ttings'), None),

            ('Reload', gtk.STOCK_REFRESH,
             _('_Reload'), "<Ctrl>R",
             _('Reload scripts list'), self._reload_cb),

            ('Search', gtk.STOCK_FIND,
             _('_Search'), "<Ctrl>S",
             _('Search necessory scripts'), self._search_cb),

            ('Edit', gtk.STOCK_EDIT,
             _('_Edit'), "<Ctrl>E",
             _('Edit selected script'), self._edit_cb),

            ('Preferences', gtk.STOCK_PREFERENCES,
             _('_Preferences'), "<Ctrl>P",
             _('Script Manager settings'), self._preferences_cb),
            
            ('Help', None, _('_Help'), None),

            ('Report a bug', gtk.STOCK_DIALOG_INFO,
             _('_Report a bug'), "<Ctrl>b",
             _('Report a bug'), self._show_bug_report_cb),

            ('Show Help', gtk.STOCK_HELP,
             _('_Help'), None,
             _('Show the application help'), self._show_help_cb)
            
        ]

        toggle_actions = [
            ('Toolbar', None,
             _('Toolbar'), None,
             _('Show/hide toolbar'), self._toolbar_cb, True),

            ('Statusbar', None,
             _('Statusbar'), None,
             _('Show/hide statusbar'), self._statusbar_cb, True),

            ('Categories', None,
             _('Categories'), None,
             _('Show/hide Categories sidebar'), self._categories_cb, True),

            ('Description', None,
             _('Description'), None,
             _('Show/hide Description sidebar'), self._description_cb, True)
        ]

        ui = """<menubar>
        <menu action='Script'>
            <menuitem action='Install'/>
            <menuitem action='Upgrade'/>
            <menuitem action='Remove'/>
            <separator/>
            <menuitem action='New'/>
            <menuitem action='New Wizard'/>
            <menuitem action='Edit'/>
            <separator/>
            <menuitem action='Quit'/>
        </menu>
        <menu action='Tools'>
            <menuitem action='Reload'/>
            <menuitem action='Install All'/>
            <menuitem action='Upgrade All'/>
            <separator/>
            <menuitem action='Search'/>
            <separator/>
            <menuitem action='Add Source'/>
	    <separator/>
	    <menuitem action='Edit Templates'/>
        </menu>
        <menu action='View'>
            <menuitem action='Categories'/>
            <menuitem action='Description'/>
            <menuitem action='Toolbar'/>
            <menuitem action='Statusbar'/>
        </menu>
        <menu action='Settings'>
            <menuitem action='Preferences'/>
        </menu>
        <menu action='Help'>
            <menuitem action='Show Help'/>
            <menuitem action='Report a bug'/>
        </menu>
        </menubar>

        <toolbar>
            <toolitem action='Reload'/>
            <toolitem action='Install All'/>
            <toolitem action='Upgrade All'/>
            <separator/>
            <toolitem action='Search'/>
            <toolitem action='Edit'/>
            <separator/>
            <toolitem action='Preferences'/>
        </toolbar>
        """

        self.create_layout(actions, toggle_actions, ui)

        self.action_group.get_action('Categories').set_active(self.preferences.view_categories)
        self.action_group.get_action('Description').set_active(self.preferences.view_description)
        self.action_group.get_action('Toolbar').set_active(self.preferences.view_toolbar)
        self.action_group.get_action('Statusbar').set_active(self.preferences.view_statusbar)

        # popup menu
        self.popup_menu = gtk.Menu()
        install_item = gtk.ImageMenuItem(_("Install"))
        install_item.set_image(gtk.image_new_from_stock(gtk.STOCK_CONVERT, gtk.ICON_SIZE_MENU))
        install_item.connect("activate", self._install_cb)
        self.popup_menu.append(install_item)
        upgrade_item = gtk.ImageMenuItem(_("Upgrade"))
        upgrade_item.set_image(gtk.image_new_from_stock(gtk.STOCK_EXECUTE, gtk.ICON_SIZE_MENU))
        upgrade_item.connect("activate", self._upgrade_cb)
        self.popup_menu.append(upgrade_item)
        remove_item = gtk.ImageMenuItem(_("Remove"))
        remove_item.set_image(gtk.image_new_from_stock(gtk.STOCK_DELETE, gtk.ICON_SIZE_MENU))
        remove_item.connect("activate", self._remove_cb)
        self.popup_menu.append(remove_item)
        # TODO: Properties dialog
        #self.popup_menu.append(gtk.SeparatorMenuItem())
        #properties_item = gtk.ImageMenuItem(_("Properties"))
        #properties_item.set_image(gtk.image_new_from_stock(gtk.STOCK_PROPERTIES, gtk.ICON_SIZE_MENU))
        #self.popup_menu.append(properties_item)
        self.popup_menu.show_all()

    def show_all(self):
        ScriptWindow.show_all(self)
        (self.categories_scroll.hide,
         self.categories_scroll.show)[self.preferences.view_categories]()
        (self.desc_scroll.hide,
         self.desc_scroll.show)[self.preferences.view_description]()
        (self.toolbar.hide,
         self.toolbar.show)[self.preferences.view_toolbar]()
        (self.statusbar.hide,
         self.statusbar.show)[self.preferences.view_statusbar]()
        
    def create_categories(self):
        self.categories_model = gtk.ListStore(object, str, int)
        self.categories_view = gtk.TreeView(self.categories_model)
        self.categories_model.set_sort_column_id(2, gtk.SORT_ASCENDING)
        self.categories_view.set_headers_visible(False)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Category', cell, markup=1)
        self.categories_view.append_column(col)
        self.categories_view.set_search_column(1)
        self.categories_view.connect('cursor-changed', self._select_category_cb)
        self.categories_view.set_size_request(100, -1)
        self.categories_scroll = scroll_wrap(self.categories_view)
        return self.categories_scroll

    def create_list(self):
        self.list_model = gtk.ListStore(object)
        self.list_view = gtk.TreeView(self.list_model)
        #self.list_view.get_selection().set_mode(gtk.SELECTION_MULTIPLE)
        self.list_view.set_property('rules-hint', True)
        self.list_columns = []
        self.list_view.connect('cursor-changed', self._select_script_cb)
        self.list_view.connect('button-press-event', self._button_press_script_cb)
        return scroll_wrap(self.list_view)

    def create_desc(self):
        self.desc_buffer = gtk.TextBuffer()
        desc_view = gtk.TextView(self.desc_buffer)
        desc_view.set_editable(False)
        desc_view.set_wrap_mode(gtk.WRAP_WORD)
        desc_view.set_size_request(-1, 100);
        self.desc_scroll = scroll_wrap(desc_view)
        return self.desc_scroll
    
    def create_main(self):
        hpaned = gtk.HPaned()
        hpaned.pack1(self.create_categories(), False)
        vpaned = gtk.VPaned()
        vpaned.pack1(self.create_list(), True)
        vpaned.pack2(self.create_desc(), False)
        hpaned.pack2(vpaned, True)
        return hpaned

    def update_model(self, category = -1):
        self.update_categories(category)
        self.update_columns()
        self.update_list(self.get_selected_filter())

    def update_columns(self):
        for col in self.list_columns:
            self.list_view.remove_column(col)
        self.list_columns = []
        model_list = [object]
        i = 1
        pixbuf_id = None
        search_id = None
        for col in self.preferences.columns_order:
            if col in self.preferences.columns_visible:
                col_data = self.columns_dict[col]
                cell = col_data[0]()
                if col_data[0] == gtk.CellRendererToggle:
                    column = gtk.TreeViewColumn(col, cell, active=i)
                elif col_data[0] == gtk.CellRendererPixbuf:
                    column = gtk.TreeViewColumn(col, cell, icon_name=i)
                    pixbuf_id = i
                else:
                    if not search_id:
                        search_id = i
                    column = gtk.TreeViewColumn(col, cell, text=i)
                column.set_sort_column_id(i)
                self.list_view.append_column(column)
                self.list_columns.append(column)
                i += 1
                model_list.append(col_data[1])
        self.list_model = gtk.ListStore(*tuple(model_list))
        self.list_view.set_model(self.list_model)
        self.list_view.set_headers_visible(True)
        self.list_model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        if search_id:
            self.list_view.set_search_column(search_id)
        if pixbuf_id:
            self.list_model.set_sort_func(pixbuf_id, _status_pixbuf.compare, pixbuf_id)

    def append_filter(self, i, filter_):
        self.categories_model.append((filter_, filter_.get_name(), i))
        
    def update_categories(self, selected = -1):
        self.categories_model.clear()
        self.append_filter(0, AllFilter())
        shift = 1
        if self.search_filter:
            self.append_filter(1, self.search_filter)
            shift += 1
        for i, name in enumerate(sorted(self.base.categories)):
            self.append_filter(i + shift, CategoryFilter(name))
        if selected == -1:
            self.update_list(NoneFilter())
        else:
            self.categories_view.get_selection().select_path((selected,))

    def update_list(self, filter_):
        self.list_model.clear()
        for item in self.base.get_script_items():
	    s = item.get_last_installed()
            if s is None:
                s = item.get_last_version()
            if filter_(s):
                model_list = [(item, s)]
                for col in self.preferences.columns_order:
                    if col in self.preferences.columns_visible:
                        col_data = self.columns_dict[col]
                        model_list.append(col_data[2](item, s))
                self.list_model.append(tuple(model_list))
        self.update_desc(None)
        self.update_statusbar()

    def update_statusbar(self):
        context = self.statusbar.get_context_id("statusbar")
        self.statusbar.pop(context)
        self.statusbar.push(context, _("%d scripts listened") % len(self.list_model))

    _state_choose = {
        #state -> (Installable, Upgradable, Removable)
        ScriptItem.STATE_NOT_INSTALLED: (True, False, False),
        ScriptItem.STATE_UPGRADABLE: (False, True, True),
        ScriptItem.STATE_INSTALLED: (False, False, True)
        }
    
    def update_avaliables(self):
        item = self.get_selected_item()
        if not item:
            res = (False, False, False)
        else:
            res = self._state_choose[item.get_state()]
        self.action_group.get_action('Install').set_sensitive(res[0])
        self.action_group.get_action('Upgrade').set_sensitive(res[1])
        self.action_group.get_action('Remove').set_sensitive(res[2])

    def update_desc(self, script):
        self.action_group.get_action('Edit').set_sensitive(bool(script))
        self.update_avaliables()
        if script:
            self.desc_buffer.set_text(script.description)
        else:
            self.desc_buffer.set_text("")

    def get_selected_item(self):
        (model, it) = self.list_view.get_selection().get_selected()
        if not it:
            return None
        return self.list_model[it][0][0]
        
    def get_selected_script(self):
        (model, it) = self.list_view.get_selection().get_selected()
        if not it:
            return None
        return self.list_model[it][0][1]

    def get_selected_filter(self):
        (model, it) = self.categories_view.get_selection().get_selected()
        if not it:
            return NoneFilter()
        return self.categories_model[it][0]

    def _new_wizard_file_cb(self, p):
        editor = ScriptEditorWindow()
        editor.new_file_wizard()
        editor.show_all()

    def _new_file_cb(self, p):
        editor = ScriptEditorWindow()
        editor.open_file()
        editor.show_all()

    def _install_cb(self, p):
        script = self.get_selected_script()
        if script:
            self.base.install(script.name)
            self.update_list(self.get_selected_filter())
            self.base.save()
            
    def _upgrade_cb(self, p):
        script = self.get_selected_script()
        if script:
            self.base.upgrade(script.name)
            self.update_list(self.get_selected_filter())
            self.base.save()

    def _remove_cb(self, p):
        script = self.get_selected_script()
        if script:
            self.base.remove(script.name)
            self.update_list(self.get_selected_filter())
            self.base.save()
    
    def _install_all_cb(self, p):
        self.base.install_all()
        self.update_list(self.get_selected_filter())
        self.base.save()

    def _upgrade_all_cb(self, p):
        self.base.upgrade_all()
        self.update_list(self.get_selected_filter())
        self.base.save()
    
    def _add_source_cb(self, p):
        dialog = AddSourceDialog()
        result = dialog.run()
        dialog.destroy()
        if result == gtk.RESPONSE_OK:
            result = dialog.get_result()
            if result:
                (type_, path) = result
                self.config.add_item(type_, path)
                self.config.save()

    def _toolbar_cb(self, toggle):
        (self.toolbar.hide, self.toolbar.show)[toggle.get_active()]()
        self.preferences.view_toolbar = toggle.get_active()

    def _statusbar_cb(self, toggle):
        (self.statusbar.hide, self.statusbar.show)[toggle.get_active()]()
        self.preferences.view_statusbar = toggle.get_active()

    def _categories_cb(self, toggle):
        if toggle.get_active():
            self.update_list(self.get_selected_filter())
            self.categories_scroll.show()
            self.preferences.view_categories = True
        else:
            self.update_list(AllFilter())
            self.categories_scroll.hide()
            self.preferences.view_categories = False

    def _description_cb(self, toggle):
        if toggle.get_active():
            self.update_desc(self.get_selected_script())
            self.desc_scroll.show()
            self.preferences.view_description = True
        else:
            self.desc_scroll.hide()
            self.preferences.view_description = False

    def _reload_cb(self, p):
        self.base.reload()
        self.base.save()
        self.update_model(0)
        # TODO: testing and bugfixing
        #progress = ScriptManagerProgressWindow(self)
        #progress.show_all()

    def _search_cb(self, p):
        dialog = SearchFilterDialog(self)
        if dialog.run() == gtk.RESPONSE_OK:
            self.search_filter = SearchFilter(dialog.get_pattern())
            self.update_model(1)
        dialog.destroy()
    
    def _edit_cb(self, p):
        script = self.get_selected_script()
        if script and script.path:
            if self.preferences.use_internal_editor:
                editor = ScriptEditorWindow()
                editor.open_file(script.path)
                editor.show_all()
            else:
                # XXX : find better way to run shell command from Python
                if not os.fork():
                    os.system(self.preferences.external_command % script.path)
                    sys.exit(0)

    def _preferences_cb(self, p):
        dialog = ScriptManagerPreferencesDialog(self)
        dialog.run()
        dialog.destroy()
        #self.preferences.save_changes()
        self.config.save()
        self.update_columns()
        self.update_list(self.get_selected_filter())

    def _show_bug_report_cb(self, p):
        BugReport().show_all()

    def _show_help_cb(self, p):
        import webbrowser
        webbrowser.open("file://%s" % os.path.join(Path.docs_dir, "nse_facilitator.html#script_manager"), new=2)

    def _select_category_cb(self, categories_view):
        self.update_list(self.get_selected_filter())

    def _button_press_script_cb(self, list_view, e):
        if e.type != gtk.gdk.BUTTON_PRESS or e.button != 3:
            return
        path = self.list_view.get_path_at_pos(int(e.x), int(e.y))[0]
        item = self.list_model[path][0][0]
        state = self._state_choose[item.get_state()]
        for menu_item, sensitive in zip(self.popup_menu.get_children(), state):
            menu_item.set_sensitive(sensitive)
        self.popup_menu.popup(None, None, None, e.button, e.get_time())
        
    def _select_script_cb(self, list_view):
        self.update_desc(self.get_selected_script())
    
    def _quit_cb(self, p):
        self.destroy()
	
    def _templates_cb(self, p):
	template_manager = ScriptManagerTemplates(self)
        template_manager.show_all()

class ScriptManagerReloadThread(threading.Thread):
    def __init__(self, base):
        gtk.gdk.threads_init()
        self.event = threading.Event()
        threading.Thread.__init__(self)
        self.base = base
        self.status = (None, None, None)

    def run(self):
        self.base.reload(callback=self.callback_impl)
        #gtk.gdk.threads_enter()
        #for i in range(100):
        #    print i
        #gtk.gdk.threads_leave()

    def callback_impl(self, src, all, current):
        self.status = (src, all, current)
        print "cb_impl:", self.status
        return not self.event.isSet()
        
    def join(self, timeout=None):
        self.event.set()
        threading.Thread.join(self, timeout)

def reload_thread(base, progress, lock):
    def callback_impl(src, all, current):
        progress.status = (src, all, current)
        print "cb_impl:", progress.status
        return not lock.locked()
    base.reload(callback_impl)
    
class ScriptManagerProgressWindow(HIGWindow):
    def __init__(self, parent):
        HIGWindow.__init__(self)
        self.set_title(_("Script Manager Progress"))
        self.set_position(gtk.WIN_POS_CENTER)
        self.set_size_request(300, 200)
        self.vbox = HIGVBox()
        self.label = gtk.Label()
        self.vbox.pack_start(self.label)
        self.progress_all = HIGLabeledProgressBar(_("Overall progress"))
        self.vbox.pack_start(self.progress_all)
        self.progress_current = HIGLabeledProgressBar(_("Current source"))
        self.vbox.pack_start(self.progress_current)
        self.btn_cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.btn_cancel.connect("clicked", self._cancel_cb)
        self.vbox.pack_start(self.btn_cancel)
        self.add(self.vbox)
        self.show_all()
        self.timeout_id = gobject.timeout_add(100, self.callback)
        self.status = (None, None, None)
        import thread
        self.lock = thread.allocate_lock()
        reload_thread(parent.base, self, self.lock)
        #thread.start_new_thread(reload_thread, (parent.base, self, self.lock))
        #self.thread = ScriptManagerReloadThread(parent.base)
        #self.thread.start()

    def _cancel_cb(self, widget):
        if self.timeout_id:
            gobject.source_remove(self.timeout_id)
        self.lock.acquire()
        self.destroy()
        
    def callback(self):
        src, all, current = self.status
        print "cb:", self.status
        if src:
            self.label.set_text(src.path)
        if all:
            if all[0] == all[1]:
                gobject.source_remove(self.timeout_id)
                self.timeout_id = None
            self.progress_all.progress_bar.set_fraction(float(all[0])/all[1])
            self.progress_all.label.set_text("%d/%d" % all)
        else:
            self.progress_all.progress_bar.set_fraction(0)
            self.progress_all.label.set_text("")
        if current:
            self.progress_current.progress_bar.set_fraction(float(current[0])/current[1])
            self.progress_current.label.set_text("%d/%d" % current)
        else:
            self.progress_current.progress_bar.set_fraction(0)
            self.progress_current.label.set_text("")

class SearchFilterDialog(HIGDialog):
    def __init__(self, parent = None):
        HIGDialog.__init__(self, _("Find"), parent,
                           gtk.DIALOG_MODAL | gtk.DIALOG_NO_SEPARATOR,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_FIND, gtk.RESPONSE_OK))
        self.set_default_response(gtk.RESPONSE_OK)
        hbox = HIGHBox()
        hbox.pack_start(gtk.Label(_("Search:")))
        self.entry = HIGTextEntry()
        self.entry.set_activates_default(True)
        hbox.pack_start(self.entry)
        self.vbox.add(hbox)
        self.show_all()

    def get_pattern(self):
        return self.entry.get_text()

class AddSourceDialog(HIGDialog):
    def __init__(self, type_ = None, path = None):
        if type_ and path:
            title = _("Edit Source")
        else:
            type_ = "FILE"
            path = ""
            title = _("Add Source")
        HIGDialog.__init__(self, title, None,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))
        hbox = HIGHBox()
        self.combo = gtk.combo_box_new_text()
        types = sorted(self.types.keys())
        for t in types:
            self.combo.append_text(t)
        self.combo.set_active(types.index(type_))
        self.combo.connect("changed", self._changed_cb)
        hbox.pack_start(self.combo, False, False)
        self.entry = HIGTextEntry()
        self.entry.set_text(path)
        hbox.pack_start(self.entry)
        self.btn = HIGButton(_("Browse..."), stock=gtk.STOCK_OPEN)
        self.btn.connect("clicked", self._clicked_cb)
        hbox.pack_start(self.btn, False, False)
        self.vbox.add(hbox)
        self.show_all()
        self.update()

    def update(self):
         callback, = self.types[self.combo.get_active_text()]
         self.btn.set_sensitive(not callback is None)

    def _browse_file(self, p):
        file_chooser = AllFilesFileChooserDialog(_("Select Script"))
        response = file_chooser.run()
        filename = file_chooser.get_filename()
        file_chooser.destroy()
        if not response == gtk.RESPONSE_OK:
            return
        self.entry.set_text(filename)

    def _browse_folder(self, p):
        file_chooser = DirectoryChooserDialog(_("Select Scripts Directory"))
        response = file_chooser.run()
        dirname = file_chooser.get_filename()
        file_chooser.destroy()
        if not response == gtk.RESPONSE_OK:
            return False
        self.entry.set_text(dirname)

    types = {
        "FILE" : (_browse_file, ),
        "DIR" : (_browse_folder, ),
        "URL" : (None, ), 
        "URLBASE" : (None, ),
        "INSTALLDIR" : (_browse_folder, )
    }

    def _clicked_cb(self, p):
         callback, = self.types[self.combo.get_active_text()]
         if callback:
             callback(self, p)

    def _changed_cb(self, p):
        self.update()

    def get_result(self):
        (type_, path) = (self.combo.get_active_text(), self.entry.get_text())
        if type_ not in ('FILE', 'DIR'):
            return (type_, path)
        # test existence
        if os.path.exists(path):
            return (type_, path)
        else:
            message = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                                        buttons=gtk.BUTTONS_YES_NO,
                                        message_format=_("The path don't exists. Append it?"))
            message.set_title(_("No such path"))
            response = message.run()
            message.destroy()
            if response == gtk.RESPONSE_YES:
                return (type_, path)
        return None
        
class ScriptManagerPreferencesDialog(HIGDialog):
    def __init__(self, parent):
        HIGDialog.__init__(self, _("Script Manager Preferences"), parent,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE,
                            gtk.STOCK_HELP, gtk.RESPONSE_HELP))
        self.config = parent.config
        self.preferences = parent.preferences
        self.set_size_request(450, 400)
	self.tab_catalog = self.create_tab_catalog()
	self.tab_editor = self.create_tab_editor()
	self.tab_columns = self.create_tab_columns()
	self.tab_network = self.create_tab_network()
        self.create_widgets()
        self.connect("destroy", self.update_preferences)
    
    def create_tab_catalog(self):
        return NSEPreferencesCatalog(self.config)

    def create_tab_editor(self):
        return NSEPreferencesEditor(self.preferences)
    
    def create_tab_columns(self):
	return NSEPreferencesColumns(self.preferences)
        
    def create_tab_network(self):
        return NSEPreferencesNetwork(self.preferences, self.config)
    
    def create_widgets(self):
        notebook = HIGNotebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.append_page(self.tab_catalog, gtk.Label(_("Sources")))
        notebook.append_page(self.tab_editor, gtk.Label(_("Editor")))
        notebook.append_page(self.tab_columns, gtk.Label(_("Columns")))
        notebook.append_page(self.tab_network, gtk.Label(_("Network")))
        self.vbox.add(notebook)
        self.connect("response", self._response_cb)
        self.show_all()

    def update_preferences(self, config):
        self.tab_columns.save()
	self.tab_editor.save()
	self.tab_network.save()

    def _response_cb(self, dialog, response_id):
        if response_id != gtk.RESPONSE_HELP:
            return
        import webbrowser
        webbrowser.open("file://%s" %
                        os.path.join(Path.docs_dir, "nse_facilitator.html#preferences"), new=2)
        self.stop_emission("response")
	
	
# Tabs page classes
class NSEPreferencesCatalog(HIGVBox):

    def __init__(self, config, show_label=True):
	HIGVBox.__init__(self)
        self.set_border_width(8)
	if show_label:
	    self.pack_start(HIGSectionLabel(_("Script Sources")), False, False)
	self.config = config
	self.create_widgets()
	self.update_model()
        
    def create_widgets(self):
        hbox = HIGHBox()
        hbox.pack_start(self.create_src_list(), True, True)
        
        # buttons
        vbox = HIGVBox()

        btn = HIGButton(_("Add Source..."), gtk.STOCK_ADD)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._add_source_cb)

        btn = HIGButton(_("Edit..."), gtk.STOCK_EDIT)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._edit_source_cb)
        
        btn = HIGButton(_("Remove"), gtk.STOCK_REMOVE)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._remove_cb)

        hbox.pack_start(vbox, False, False)

        self.pack_start(hbox)
	
    def create_src_list(self):
        # list
        self.config_model = gtk.ListStore(str, str)
        self.config_view = gtk.TreeView(self.config_model)
        self.config_view.set_headers_visible(True)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Type'), cell, text=0)
        self.config_view.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Path'), cell, text=1)
        self.config_view.append_column(col)
        
        self.config_view.set_search_column(1)
        return scroll_wrap(self.config_view)
    
    def _add_source_cb(self, p):
        dialog = AddSourceDialog()
        result = dialog.run()
        dialog.destroy()
        if result == gtk.RESPONSE_OK:
            result = dialog.get_result()
            if result:
                (type_, path) = result
                self.config_model.append((type_, path))
                self.config.add_item(type_, path)
                self.config.save()

    def _edit_source_cb(self, p):
        (model, it) = self.config_view.get_selection().get_selected()
        type_, path = model[it]
        dialog = AddSourceDialog(type_, path)
        result = dialog.run()
        dialog.destroy()
        if result == gtk.RESPONSE_OK:
            result = dialog.get_result()
            if result:
                self.config.remove_item(type_, path)
                (type_, path) = result
                model[it] = (type_, path)
                self.config.add_item(type_, path)
                self.config.save()
		
    def _remove_cb(self, p):
        (model, it) = self.config_view.get_selection().get_selected()
        type_, path = model[it]
        model.remove(it)
        self.config.remove_item(type_, path)
        self.config.save()
	
    def update_model(self):
        self.config_model.clear()
        for src in self.config.get_sources():
            self.config_model.append((src.type, src.path))


class NSEPreferencesEditor(HIGVBox):

    def __init__(self, preferences, show_label=True):
	HIGVBox.__init__(self)
        self.set_border_width(8)
	if show_label:
	    self.pack_start(HIGSectionLabel(_("Text Editor")), False, False)
	self.preferences = preferences
	self.create_widgets()

    def create_widgets(self):
        vbox = HIGVBox()

        self.btn_internal = gtk.RadioButton(None, _("Internal Editor"))
        vbox.pack_start(self.btn_internal, False, False)

        self.btn_external = gtk.RadioButton(self.btn_internal, _("External Editor"))
        vbox.pack_start(self.btn_external, False, False)

        self.external_cmd = gtk.Entry()
        self.external_cmd.set_text(self.preferences.external_command)
        vbox.pack_start(HIGSpacer(self.external_cmd), False, False)

        self.btn_external.connect("toggled",
                                  lambda b: self._update_use_editor())
	
	self.external_cmd.connect("focus-out-event",
                                       self._update_external_command)

        if self.preferences.use_internal_editor:
            self.btn_internal.set_active(True)
            self.external_cmd.set_sensitive(False)
        else:
            self.btn_external.set_active(True)
            self.external_cmd.set_sensitive(True)
        
        self.pack_start(HIGSpacer(vbox), False, False)
	
    def _update_use_editor(self):
	self.external_cmd.set_sensitive(self.btn_external.get_active())
	self.preferences.use_internal_editor = self.btn_internal.get_active()	    
	
    def _update_external_command(self, a=None, b=None):
	self.preferences.external_command = self.external_cmd.get_text()
        
    def save(self):
	self._update_external_command()
	self._update_use_editor()

class NSEPreferencesNetwork(HIGVBox):
    
    def __init__(self, preferences, config, show_label=True):
	HIGVBox.__init__(self)
	self.set_border_width(8)
	if show_label:
	    self.pack_start(HIGSectionLabel(_("Proxy Server")), False, False)
	self.preferences = preferences
	self.config = config
	self.create_widgets()
	    
    def create_widgets(self):
	proxies = self.config.get_proxies()

        vbox = HIGVBox()
        
        self.no_proxy_radio = gtk.RadioButton(None, _("Direct connection to the Internet"))
        vbox.pack_start(self.no_proxy_radio, False, False)
        self.proxy_radio = gtk.RadioButton(self.no_proxy_radio, _("Manual proxy configuration"))
        vbox.pack_start(self.proxy_radio, False, False)
        if proxies:
            http_proxy = proxies.get('http', ":3128")
            ftp_proxy = proxies.get('ftp', ":3128") 
        else:
            http_proxy = self.preferences.http_proxy
            ftp_proxy = self.preferences.ftp_proxy

        self.proxy_table = HIGTable(2, 4)
        self.http_host, self.http_port = self.create_proxy_row(self.proxy_table, 0, "HTTP", http_proxy)
        self.ftp_host, self.ftp_port = self.create_proxy_row(self.proxy_table, 1, "FTP", ftp_proxy)
        vbox.pack_start(HIGSpacer(self.proxy_table), False, False)

        if proxies:
            self.proxy_radio.set_active(True)
            self.proxy_table.set_sensitive(True)
        else:
            self.no_proxy_radio.set_active(True)
            self.proxy_table.set_sensitive(False)

        self.proxy_radio.connect("toggled",
                                 lambda b: self._update_use_proxy())
	
	self.http_host.connect("focus-out-event",
                                       self._update_http_proxy)
	
	self.ftp_host.connect("focus-out-event",
                                       self._update_ftp_proxy)
	
	self.http_port.connect("focus-out-event",
                                       self._update_http_proxy)
	
	self.ftp_port.connect("focus-out-event",
                                       self._update_ftp_proxy)	
        
        self.pack_start(HIGSpacer(vbox), False, False)
	
    def parse_proxy(self, s):
	return (s + ":").split(":")[0:2]
        
    def create_proxy_row(self, table, level, name, default = ""):
	host, port = self.parse_proxy(default)
	try:
	    port = float(port)
	except ValueError:
	    port = 3128

	lbl = HIGEntryLabel(name + " " + _("proxy") + ":")
	lbl.set_justify(gtk.JUSTIFY_LEFT)
	host_entry = HIGTextEntry()
	host_entry.set_text(host)
	lbl.set_mnemonic_widget(host_entry)
	table.attach(lbl, 0, 1, level, level + 1, 0, 0)
	table.attach(host_entry, 1, 2, level, level + 1)
	
	lbl = HIGEntryLabel(_("Port") + ":")
	lbl.set_justify(gtk.JUSTIFY_LEFT)
	port_entry = gtk.SpinButton(gtk.Adjustment(port, 0, 65536, 1, 100), 1.0, 0)
	lbl.set_mnemonic_widget(port_entry)
	table.attach(lbl, 2, 3, level, level + 1, 0, 0)
	table.attach(port_entry, 3, 4, level, level + 1, 0, 0)
	return host_entry, port_entry
    
    def _update_use_proxy(self):
	self.proxy_table.set_sensitive(self.proxy_radio.get_active())
	if self.proxy_radio.get_active():
            proxies = {'http' : self.preferences.http_proxy,
                       'ftp'  : self.preferences.ftp_proxy}
            self.config.set_proxies(proxies)
	else:
            self.config.set_proxies(dict())
	    
    def _update_http_proxy(self, a=None, b=None):
	self.preferences.http_proxy = self.http_host.get_text() + ":" + self.http_port.get_text()
	
    def _update_ftp_proxy(self, a=None, b=None):
	self.preferences.ftp_proxy = self.ftp_host.get_text() + ":" + self.ftp_port.get_text()
    
    def save(self):
	self._update_ftp_proxy()
	self._update_http_proxy()
	self._update_use_proxy()


class NSEPreferencesColumns(HIGVBox):
    
    def __init__(self, preferences, show_label=True):
	HIGVBox.__init__(self)
	self.set_border_width(8)
	if show_label:
	    self.pack_start(HIGSectionLabel(_("Columns")), False, False)
	self.preferences = preferences
	self.create_widgets()
	self.update_model()
	    
    def create_widgets(self):
	hbox = HIGHBox()
	hbox.pack_start(self.create_columns_list(), True, True)
	
	# buttons
	vbox = HIGVBox()
    
	btn = HIGButton(_("Move Up"), gtk.STOCK_GO_UP)
	vbox.pack_start(btn, False, False)
	btn.connect("clicked", self._move_up_down, -1)
    
	btn = HIGButton(_("Move Down"), gtk.STOCK_GO_DOWN)
	vbox.pack_start(btn, False, False)
	btn.connect("clicked", self._move_up_down, 1)
    
	hbox.pack_start(vbox, False, False)
	
	self.pack_start(hbox)
	
    def create_columns_list(self):
        self.columns_model = gtk.ListStore(bool, str)
        self.columns_view = gtk.TreeView(self.columns_model)
        self.columns_view.set_headers_visible(True)

        cell = gtk.CellRendererToggle()
        col = gtk.TreeViewColumn(_('Visible'), cell, active=0)
        cell.connect('toggled', self._toggled_cb, self.columns_model)
        self.columns_view.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn(_('Name'), cell, text=1)
        self.columns_view.append_column(col)
        
        self.columns_view.set_search_column(1)
        return scroll_wrap(self.columns_view)
    
    def _move_up_down(self, p, direction):
        (model, it) = self.columns_view.get_selection().get_selected()
        if not it:
            return None
        path = self.columns_model.get_path(it)
        path2 = (path[0] + direction, )
        if path2[0] >= 0 and path2[0] < len(self.columns_model):
            it2 = self.columns_model.get_iter((path[0] + direction,))
            self.columns_model.swap(it, it2)
	self.save()
	    
    def _toggled_cb(self, cell, path, model):
        model[path][0] = not model[path][0]
	self.save()
	
    def update_model(self):
	self.columns_model.clear()
        for col in self.preferences.columns_order:
            self.columns_model.append((col in self.preferences.columns_visible, col))
	    
    def save(self):
	order = []
        visible = []
        for raw in self.columns_model:
            order.append(raw[1])
            if raw[0]:
                visible.append(raw[1])
        
        self.preferences.columns_order = order
        self.preferences.columns_visible = visible

	
class ScriptManagerTemplates(HIGWindow):
    def __init__(self, parent):
	HIGWindow.__init__(self)
	self.set_title(_("Script Manager User Templates"))
	self.set_position(gtk.WIN_POS_CENTER)
        self.set_size_request(450, 400)
        self.create_widgets()
	
    def create_widgets(self):
	vboxmain = gtk.VBox()
	sw = gtk.ScrolledWindow()
        sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
	
	self.store = gtk.ListStore(str)	
        self.update_model()
	self.treeView = gtk.TreeView(self.store)
	#treeView.connect("row-activated", self.on_activated)
	#treeView.set_rules_hint(True)
	self.create_columns(self.treeView)
	sw.add(self.treeView)
		
	# buttons
        vbox = HIGVBox()

        btn = HIGButton(_("Edit..."), gtk.STOCK_EDIT)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._edit_template)
        
        btn = HIGButton(_("Remove"), gtk.STOCK_REMOVE)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._remove_template)
	
	hbox = HIGHBox()
	hbox.pack_start(sw, True, True)
	hbox.pack_start(vbox, False, False)
	vboxmain.pack_start(hbox, True, True, 0)
	self.add(vboxmain)
        self.show_all()	
	
    def update_model(self):
	self.store.clear()
	for template in get_templates():
	    self.store.append([template])
    
    def create_columns(self, treeView):    
        rendererText = gtk.CellRendererText()
        column = gtk.TreeViewColumn("Template Name", rendererText, text=0)
        column.set_sort_column_id(0)    
        treeView.append_column(column)
	
    def get_selected_template(self):
        (model, it) = self.treeView.get_selection().get_selected()
        if not it:
            return None
        return self.store[it][0]
	
    def _edit_template(self, p):
	template = self.get_selected_template()
        if template:
	    template_path = DEFAULT_TEMPLATE_PATH + '/' + template
	    editor = ScriptEditorWindow()
	    editor.open_file(template_path)
	    editor.show_all()
	
    def _remove_template(self, p):
	template = self.get_selected_template()
        if template:
	    template_path = DEFAULT_TEMPLATE_PATH + '/' + template
	    os.remove(template_path)
	    self.update_model()
    

if __name__ == "__main__":
    #sm = ScriptManagerWindow()
    #sm.show_all()
    #sm.connect("destroy", gtk.main_quit)
    conf = ScriptConfig()
    conf.load()
    base = ScriptBase(conf)
    thread = ScriptManagerReloadThread(base)
    thread.start()
    gtk.main()

