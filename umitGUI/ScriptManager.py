# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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
import re
import sys
#from gtksourceview import SourceView, SourceLanguagesManager, SourceBuffer

from umitCore.Paths import check_access
from umitCore.I18N import _

import gtk
from umitGUI.FileChoosers import DirectoryChooserDialog, AllFilesFileChooserDialog
from higwidgets.higwindows import HIGWindow, HIGMainWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer, hig_box_space_holder
from higwidgets.higexpanders import HIGExpander
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel, HIGDialogLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog, HIGDialog
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higframe import HIGFrame

# aux alert function
def _alert(header, text):
    alert = HIGAlertDialog(
        message_format='<b>%s</b>' % header,
        secondary_text=text
        )
    alert.run()
    alert.destroy()

def get_file_list(path):
        result = []
        try:
            for filename in os.listdir(path):
                fullpath = os.path.join(path, filename)
                if os.path.isfile(fullpath) and check_access(fullpath, os.R_OK):
                    result.append(fullpath)
        except OSError:
            pass
        return result

def scroll_wrap(widget):
    scroll = HIGScrolledWindow()
    scroll.set_shadow_type(gtk.SHADOW_IN)
    scroll.add(widget)
    return scroll
    
# aux nmap_fetchfile functions
# XXX: will be moved into Paths.Search or/and into Python/Nmap wrapper
class NmapFetch(object):
    def __init__(self):
        self.dirs = self.__fetchdirs()

    def fetchdirs(self):
        return self.dirs

    def fetchfile(self, filename):
        for path in self.fetchdirs():
            fullpath = os.path.join(path, filename)
            if check_access(fullpath, os.R_OK):
                return fullpath
        return None

    def get_file_list(self):
        result = []
        for path in self.fetchdirs():
            result.extend(get_file_list(path))
        return result

    def nmap_path(self, path):
        fullpath = os.path.abspath(path)
        for p in self.fetchdirs():
            if fullpath.startswith(p):
                return fullpath[len(p)+1:] # XXX: check +1 (removing last slash) on Windows
        return fullpath

    def __fetchdirs(self):
        # standart Nmap searching directories (see nmap.cc:nmap_fetchfile function)
        def varpath():
            return os.path.expandvars("${NMAPDIR}")
        def uidpath():
            return os.path.join(pwd.getpwuid(os.getuid()).pw_dir, ".nmap")
        def euidpath():
            return os.path.join(pwd.getpwuid(os.geteuid()).pw_dir, ".nmap")
        def userpath():
            return os.path.expanduser("~")
        def datadirpath_win():
            return "c:\\nmap"
        def datadirpath():
            return "/usr/share/nmap/"
        def datadirpath2():
            return "/usr/local/share/nmap/"
        def currentpath():
            return "."

        if sys.platform != 'win32':
            import pwd
            checklist = [varpath, uidpath, euidpath, datadirpath, datadirpath2, currentpath]
        else:
            checklist = [varpath, userpath, datadirpath_win, currentpath]

        paths = [os.path.abspath(f()) for f in checklist]
        # XXX: not stable
        return list(set(paths))

class NmapFetchScripts(NmapFetch):
    def __init__(self):
        NmapFetch.__init__(self)
        self.dirs = [os.path.join(d, "scripts") for d in self.dirs]

    def get_file_list(self):
        return [f for f in NmapFetch.get_file_list(self) if f.endswith(".nse")]

# Model classes
# XXX: will be moved to umitCore/
class ScriptParseException(Exception):
    pass

class Script(object):
    def __init__(self, path):
        f = file(path, 'r')
        self.data = f.read()
        f.close()

        self.path = NmapFetchScripts().nmap_path(path)
        self.name, self.type = os.path.splitext(os.path.basename(path))
        self.id = self._get_attr('id') # XXX: raise exception if no id in script
        self.desc = self._get_attr('description', _("No descriptions"))
        self.author = self._get_attr("author", _("unnamed"))

        self.categories = set([_("untagged")])
        self.categories.update(set(self._get_attr_list("categories", set())))
        self.categories.update(set(self._get_attr_list("tags", set())))
        if len(self.categories) > 1:
            self.categories.remove(_("untagged"))

    def _normilize(self, string):
        string = string.replace('\n', ' ')
        string = string.replace('\\', ' ')
        string = string.replace('   ', ' ')
        string = string.replace('   ', '\n')
        return " ".join(string.split(" ")).strip()
        # more script-related breaks
        #return "\n".join([" ".join(s.split(" ")).strip()
        #                  for s in string.replace('\\', '\n').split("\n")])
        
    def _get_attr_list(self, attr, default = None):
        r = re.findall(attr + '\s*=\s*{([^\}]*)}', self.data)
        if not r:
            if default is not None:
                return default
            raise ScriptParseException("Can't parse attr %s in file %s" % (attr, self.path))
        return [self._normilize(tag) for tag in re.findall('"([^\"]+)"', r[0])]
        
    def _get_attr(self, attr, default = None):
        r = re.findall(attr + '\s*=\s*"([^\"]+)"', self.data)
        if not r:
            if default is not None:
                return default
            raise ScriptParseException("Can't parse attr %s in file %s" % (attr, self.path))
        return self._normilize(r[0])

    # for set-element support
    def __eq__(self, other):
        return self.path.__eq__(other.path)

    def __hash__(self):
        return self.path.__hash__()

class ScriptSelection(object):
    def __init__(self, selected = ""):
        self.d = dict([(s, False) for s in script_manager])
        self.set_selected(selected)

    def set_selected(self, selected):
        for filename in selected.split(";"):
            script = script_manager.find_by_path(filename)
            if self.d.has_key(script):
                self.d[script] = True

    def get_selected(self):
        return ";".join([script.path for script in self.d.keys() if self.d[script]])

    def is_selected(self, script):
        return self.d.get(script, False)

    def select(self, script):
        self.d[script] = True

    def unselect(self, script):
        self.d[script] = False

class ScriptManager(set):
    def __init__(self):
        self.categories = set([])
        for dirname in NmapFetchScripts().fetchdirs():
            self.add_dir(dirname)

    def add_file(self, filename):
        script = Script(filename) # may raise ScriptParseException
        self.add(script)
        self.categories.update(script.categories)

    def add_dir(self, dirname):
        res = False
        for name in get_file_list(dirname):
            if name.endswith('.nse'):
                try:
                    self.add_file(os.path.join(dirname, name))
                    res = True
                except ScriptParseException:
                    pass
        return res

    def find_by_path(self, filename):
        for s in self:
            if s.path == filename:
                return s
        return None

    def update_categories(self):
        self.categories = set([])
        for s in self:
            self.categories.update(s.categories)

class ScriptManagerConfig(object):
    def __init__(self, internal_editor = False, external_cmd = "gedit %s"):
        self.internal_editor = internal_editor
        self.external_cmd = external_cmd

# Singletone
script_manager = ScriptManager()
# Global 
script_manager_config = ScriptManagerConfig()

# GUI classes
class ScriptManagerUI(object):
    def __init__(self, manager):
        self.manager = manager

    def add_file(self):
        file_chooser = AllFilesFileChooserDialog(_("Select Script"))
        response = file_chooser.run()
        name = file_chooser.get_filename()
        file_chooser.destroy()
        if not response == gtk.RESPONSE_OK:
            return 
        if not check_access(name, os.R_OK):
            _alert(
                _('Can not open selected file'),
                _("Umit can not open selected file. Please, select another."))
            return
        # actual adding
        try:
            return self.manager.add_file(name)
        except:
            _alert(
                _('File is not a NSE script file'),
                _("Selected file is not a NSE script file. Umit can not \
parse this file. Please, select another."))

    def add_dir(self):
        file_chooser = DirectoryChooserDialog(_("Select Scripts Directory"))
        response = file_chooser.run()
        dirname = file_chooser.get_filename()
        file_chooser.destroy()
        if not response == gtk.RESPONSE_OK:
            return False
        if self.manager.add_dir(dirname):
            return True
        else:
            _alert(
                _('Can not find any NSE script files in the directory'),
                _("Umit can not find any NSE script files in the selected \
directory. Please, select another."))
        return False

        
class ScriptManagerWindow(HIGMainWindow):
    def __init__(self):
        HIGMainWindow.__init__(self)
        self.set_title(_("Script Manager"))
        self.set_position(gtk.WIN_POS_CENTER)
        self.create_widgets()
        self.update_model()

    def create_ui_manager(self):
        actions = [
            ('File', None, _('_File'), None),

            ('Add File', gtk.STOCK_OPEN,
             _('Add File...'), "<Control>O",
             _('Add single script file'), self._add_file_cb),

            ('Add Directory', gtk.STOCK_DIRECTORY,
             _('Add Directory...'), "<Control>D",
             _('Add directory with script files'), self._add_dir_cb),

            ('Add URL File', gtk.STOCK_OPEN,
             _('Add URL File...'), "<Control>U",
             _('Add single script file from Web'), self._add_url_file_cb),

            ('Add URL Base', gtk.STOCK_DIRECTORY,
             _('Add URL Base...'), "<Control>B",
             _('Add base with script files from Web'), self._add_url_base_cb),

            ('Quit', gtk.STOCK_QUIT,
             _('Quit'), None,
             _('Quit from Script Manager'), self._quit_cb),

            ('View', None, _('_View'), None),
            
            ('Settings', None, _('_Settings'), None),
            
            ('Refresh', gtk.STOCK_REFRESH,
             _('Refresh'), None,
             _('Refresh scripts list'), self._refresh_cb),

            ('Find', gtk.STOCK_FIND,
             _('Search'), None,
             _('Search necessory scripts'), self._search_cb),

            ('Edit', gtk.STOCK_EDIT,
             _('Edit'), None,
             _('Edit selected script'), self._edit_cb),

            ('Preferences', gtk.STOCK_PREFERENCES,
             _('Preferences'), None,
             _('Script Manager settings'), self._preferences_cb)

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
        <menu action='File'>
            <menuitem action='Add File'/>
            <menuitem action='Add Directory'/>
            <menuitem action='Add URL File'/>
            <menuitem action='Add URL Base'/>
            <separator/>
            <menuitem action='Quit'/>
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
        </menubar>

        <toolbar>
            <toolitem action='Refresh'/>
            <toolitem action='Find'/>
            <toolitem action='Edit'/>
            <toolitem action='Preferences'/>
        </toolbar>
        """

        self.accel_group = gtk.AccelGroup()
        self.add_accel_group(self.accel_group)

        self.action_group = gtk.ActionGroup('ScriptManagerActionGroup')
        self.action_group.add_actions(actions)
        self.action_group.add_toggle_actions(toggle_actions)

        for action in self.action_group.list_actions():
            action.set_accel_group(self.accel_group)
            action.connect_accelerator()
            
        self.ui_manager = gtk.UIManager()
        self.ui_manager.insert_action_group(self.action_group, 0)
        self.ui_manager.add_ui_from_string(ui)
        
    def create_menu(self):
        menu_bar = self.ui_manager.get_widget('/menubar')
        return menu_bar

    def create_toolbar(self):
        self.toolbar = self.ui_manager.get_widget('/toolbar')
        self.btn_edit = self.ui_manager.get_widget('/toolbar/Edit')
        return self.toolbar

    def create_categories(self):
        self.categories_model = gtk.ListStore(object, str)
        self.categories_view = gtk.TreeView(self.categories_model)
        self.categories_model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.categories_view.set_headers_visible(False)
        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn('Category', cell, text=1)
        self.categories_view.append_column(col)
        self.categories_view.set_search_column(1)
        self.categories_view.connect('cursor-changed', self._select_category_cb)
        self.categories_view.set_size_request(100, -1)
        self.categories_scroll = scroll_wrap(self.categories_view)
        return self.categories_scroll

    def create_list(self):
        self.list_model = gtk.ListStore(object, str, str, str)
        self.list_view = gtk.TreeView(self.list_model)
        #self.list_model.set_sort_column_id(1, gtk.SORT_ASCENDING)
        self.list_view.set_headers_visible(True)
        cell = gtk.CellRendererText()

        col = gtk.TreeViewColumn('Script', cell, text=1)
        col.set_sort_column_id(1)
        self.list_view.append_column(col)

        col = gtk.TreeViewColumn('Type', cell, text=2)
        col.set_sort_column_id(2)
        self.list_view.append_column(col)

        col = gtk.TreeViewColumn('Description', cell, text=3)
        col.set_sort_column_id(3)
        self.list_view.append_column(col)
        
        self.list_view.set_search_column(1)
        self.list_view.connect('cursor-changed', self._select_script_cb)
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

    def create_statusbar(self):
        self.statusbar = gtk.Statusbar()
        return self.statusbar
    
    def create_widgets(self):
        self.set_size_request(600, 400)
        vbox = gtk.VBox()
        self.create_ui_manager()
        vbox.pack_start(self.create_menu(), False, False)
        vbox.pack_start(self.create_toolbar(), False, False)
        vbox.pack_start(self.create_main(), True, True)
        vbox.pack_start(self.create_statusbar(), False, False)
        self.add(vbox)

    def update_model(self):
        self.update_categories()
        self.update_list(self.get_selected_categories())

    def update_categories(self):
        self.categories_model.clear()
        self.categories_model.append((script_manager.categories, _("All")))
        for name in script_manager.categories:
            self.categories_model.append((set([name]), name))
        self.update_list(set())

    def update_list(self, categories):
        self.list_model.clear()
        for s in script_manager:
            if s.categories.intersection(categories):
                self.list_model.append((s, s.name, s.type, s.id))
        self.update_desc(None)

    def update_desc(self, script):
        if not script:
            self.btn_edit.set_sensitive(False)
            self.desc_buffer.set_text("")
            return
        self.btn_edit.set_sensitive(True)
        self.desc_buffer.set_text(script.desc)

    def get_selected_script(self):
        (model, it) = self.list_view.get_selection().get_selected()
        if not it:
            return None
        return self.list_model[it][0]

    def get_selected_categories(self):
        (model, it) = self.categories_view.get_selection().get_selected()
        if not it:
            return set([])
        return self.categories_model[it][0]

    def _add_file_cb(self, p):
        if ScriptManagerUI(script_manager).add_file():
            self.update_model()

    def _add_dir_cb(self, p):
        if ScriptManagerUI(script_manager).add_dir():
            self.update_model()

    def _add_url_file_cb(self, p):
        pass

    def _add_url_base_cb(self, p):
        pass

    def _toolbar_cb(self, toggle):
        (self.toolbar.hide, self.toolbar.show)[toggle.get_active()]()

    def _statusbar_cb(self, toggle):
        (self.statusbar.hide, self.statusbar.show)[toggle.get_active()]()

    def _categories_cb(self, toggle):
        if toggle.get_active():
            self.update_list(self.get_selected_categories())
            self.categories_scroll.show()
        else:
            self.update_list(script_manager.categories)
            self.categories_scroll.hide()

    def _description_cb(self, toggle):
        if toggle.get_active():
            self.update_desc(self.get_selected_script())
            self.desc_scroll.show()
        else:
            self.desc_scroll.hide()

    def _refresh_cb(self, p):
        pass

    def _search_cb(self, p):
        pass
    
    def _edit_cb(self, p):
        script = self.get_selected_script()
        if script:
            if script_manager_config.internal_editor:
                _alert('Internal Editor', 'No Internal Editor yet implemented')
            else:
                # XXX : find better way to run shell command from Python
                if not os.fork():
                    os.system(script_manager_config.external_cmd %
                              NmapFetchScripts().fetchfile(script.path))
                    sys.exit(0)

    def _preferences_cb(self, p):
        dialog = ScriptManagerPreferencesDialog()
        if dialog.run() == gtk.RESPONSE_OK:
            global script_manager_config
            script_manager_config = dialog.get_config()
        dialog.destroy()

    def _select_category_cb(self, categories_view):
        categories = self.get_selected_categories()
        self.update_list(categories)

    def _select_script_cb(self, list_view):
        self.update_desc(self.get_selected_script())
    
    def _quit_cb(self, p):
        self.destroy()

class ScriptManagerPreferencesDialog(HIGDialog):
    def __init__(self):
        HIGDialog.__init__(self, _("Script Manager Preferences"), None,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))
        self.set_size_request(450, 400)
        self.create_widgets()
        self.update_model()

    def create_src_list(self):
        return HIGVBox()
    
    def create_tab1(self):
        frame = HIGFrame(_("Scripts Catalog"))
        hbox = HIGHBox()
        hbox.pack_start(self.create_src_list(), True, True)

        vbox = HIGVBox()

        btn = gtk.Button(_("Add File..."), gtk.STOCK_ADD)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._add_file_cb)

        btn = gtk.Button(_("Add Directory..."), gtk.STOCK_ADD)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._add_dir_cb)

        btn = gtk.Button(_("Add URL File..."), gtk.STOCK_ADD)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._add_url_file_cb)

        btn = gtk.Button(_("Add URL Base..."), gtk.STOCK_ADD)
        vbox.pack_start(btn, False, False)
        btn.connect("clicked", self._add_url_base_cb)

        btn = gtk.Button(_("Remove..."), gtk.STOCK_REMOVE)
        vbox.pack_end(btn, False, False)
        btn.connect("clicked", self._remove_cb)

        hbox.pack_start(vbox, False, False)

        frame.add(hbox)
        return frame

    def create_tab2(self):
        frame = HIGFrame(_("Text Editor"))
        vbox = HIGVBox()

        self.btn_internal = gtk.RadioButton(None, _("Internal Editor"))
        vbox.pack_start(self.btn_internal, False, False)

        self.btn_external = gtk.RadioButton(self.btn_internal, _("External Editor"))
        vbox.pack_start(self.btn_external, False, False)

        (self.btn_external,
         self.btn_internal)[script_manager_config.internal_editor].set_active(True)
        
        self.external_cmd = gtk.Entry()
        self.external_cmd.set_text(script_manager_config.external_cmd)
        vbox.pack_start(self.external_cmd, False, False)
        
        frame.add(vbox)
        return frame
    
    def create_widgets(self):
        notebook = HIGNotebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.append_page(self.create_tab1(), gtk.Label(_("Catalog")))
        notebook.append_page(self.create_tab2(), gtk.Label(_("Editor")))
        self.vbox.add(notebook)
        self.show_all()

    def update_model(self):
        pass

    def get_config(self):
        return ScriptManagerConfig(internal_editor = self.btn_internal.get_active(),
                                   external_cmd = self.external_cmd.get_text())

    def _add_file_cb(self, p):
        if ScriptManagerUI(ScriptManager()).add_dir():
            self.update_model()

    def _add_dir_cb(self, p):
        if ScriptManagerUI(ScriptManager()).add_dir():
            self.update_model()

    def _add_url_file_cb(self, p):
        pass

    def _add_url_base_cb(self, p):
        pass

    def _remove_cb(self, p):
        pass

class ScriptChooserDialog(HIGDialog):
    def __init__(self, selected = ""):
        HIGDialog.__init__(self, _("Select Necessory Scripts"), None,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                            gtk.STOCK_OK, gtk.RESPONSE_OK))
        self.selection = ScriptSelection(selected)
        self.set_size_request(400, 400)
        self.create_widgets()
        self.update_model()

    def create_list(self):
        self.model = gtk.ListStore(object, bool, str)
        self.list_view = gtk.TreeView(self.model)

        self.model.set_sort_column_id(2, gtk.SORT_ASCENDING)
        self.list_view.set_headers_visible(False)
        self.list_view.set_search_column(2)

        cell = gtk.CellRendererToggle()
        cell.connect('toggled', self.toggled_cb, self.model)
        col = gtk.TreeViewColumn('b', cell, active=1)
        self.list_view.append_column(col)

        cell = gtk.CellRendererText()
        col = gtk.TreeViewColumn('id', cell, text=2)
        self.list_view.append_column(col)

        self.list_view.connect('cursor-changed', self.id_select_cb)
        return scroll_wrap(self.list_view)

    def create_text(self):
        text_view = HIGTextView()
        text_view.set_editable(False)
        self.text_buffer = text_view.get_buffer()
        return scroll_wrap(text_view)

    def create_widgets(self):
        vpane = gtk.VPaned()
        vpane.pack1(self.create_list(), True)
        vpane.pack2(self.create_text(), False)
        self.vbox.add(vpane)
        self.show_all()

    def update_model(self):
        self.model.clear()
        for script in script_manager:
            self.model.append((
                script,
                self.selection.is_selected(script),
                script.id))

    def id_select_cb(self, list_view):
        (model, it) = list_view.get_selection().get_selected()
        if it:
            script = model[it][0]
            self.text_buffer.set_text(script.desc)

    def toggled_cb(self, cell, path, model):
        model[path][1] = not model[path][1]
        if model[path][1]:
            self.selection.select(model[path][0])
        else:
            self.selection.unselect(model[path][0])

    def get_scripts(self):
        return self.selection.get_selected()

if __name__ == "__main__":
    sm = ScriptManagerWindow()
    sm.show_all()
    sm.connect("destroy", gtk.main_quit)
    gtk.main()

    #sd = ScriptChooserDialog("")
    #if sd.run() == gtk.RESPONSE_OK:
    #    print "OK:", sd.get_scripts()
    #else:
    #    print "Cancel"
    #sd.destroy()
