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

import gobject
import gtk
import gtk.gdk
import pango
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer
from higwidgets.hignotebooks import HIGNotebook, HIGAnimatedTabLabel
from higwidgets.higdialogs import HIGDialog, HIGAlertDialog
from higwidgets.higframe import HIGFrame
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGEntryLabel, HIGSectionLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higtextviewers import HIGTextView

from umit.gui.FileChoosers import NSEFileChooserDialog, SaveNSEFileChooserDialog
from umit.core.UmitConf import EditorConfig
from umit.core.Paths import Path, check_access
from umit.gui.BugReport import BugReport
from umit.core.Paths import Path
from luaParser import LuaParser

# try to use gtksourceview if available
try:
    raise ImportError # for debbuging purpose

    from gtksourceview import SourceView, SourceBuffer, SourceLanguagesManager
    # known errors:
    # - no indents by Tab/Shift-Tab
    # - after filling buffer Undo are available
    def get_lua_language():
        manager = SourceLanguagesManager()
        return manager.get_language_from_mime_type('text/x-lua')
    def create_source_buffer(script):
        # TODO: find way to disable Undo after first insertion
        buf = SourceBuffer()
        buf.set_text(script)
        return buf
except ImportError:
    from pySourceView import SourceView, SourceBuffer, SourceLanguagesManager, SourceStyleScheme
    def get_lua_language():
        manager = SourceLanguagesManager()
        manager.set_search_path([Path.languages_dir])
        return manager.get_language_by_id(u'Lua')
    
    def create_source_buffer(script):
        buf = SourceBuffer(script)
        style = SourceStyleScheme.new_from_file(os.path.join(Path.styles_dir, "gvim.xml"))
        buf.set_style_scheme(style)
        return buf
    
from NmapFetch import NmapFetchScripts

from ScriptWindow import ScriptWindow
from Utils import *

DEFAULT_EDITOR_FONT = "Monospace 12"
DEFAULT_SYSTEM_FONT = "Monospace 10"
DEFAULT_BACKGROUND_COLOR = gtk.gdk.color_parse("#ffffffffffff")
DEFAULT_TEXT_COLOR = gtk.gdk.color_parse("#000000000000")
DEFAULT_SELECTED_TEXT_COLOR = gtk.gdk.color_parse("#ffffffffffff")
DEFAULT_SELECTION_COLOR = gtk.gdk.color_parse("#000000009c9c")
DEFAULT_TEMPLATE_PATH = os.path.join(Path.config_dir, 'nsetemplates')

def get_templates():
    """
    Return the list of user templates in nsetemplates folder.
    """
    templates = []
    for template in os.listdir(DEFAULT_TEMPLATE_PATH):
        ext = template.split(".")[-1]
        if ext == 'nse':
            templates.append(template)
    templates.sort()
    return templates

class ScriptEditorPageManager(object):
    def __init__(self, editor):
        self.config = EditorConfig()
        self.editor = editor

    #def save_changes(self):
    #    self.config.save_changes()

    def init_page(self, page):
        text_view = page.get_text_view()
        text_view.set_auto_indent(self.config.auto_indent)
        text_view.set_insert_spaces_instead_of_tabs(self.config.insert_spaces_instead_of_tabs)
        text_view.set_smart_home_end(self.config.smart_home_end)
        text_view.set_highlight_current_line(self.config.highlight_current_line)
        text_view.set_show_line_numbers(self.config.show_line_numbers)
        text_view.set_show_margin(self.config.show_margin)
        text_view.set_tabs_width(self.config.tabs_width)
        text_view.set_margin(self.config.margin)
        if self.config.use_system_font:
            text_view.modify_font(pango.FontDescription(DEFAULT_SYSTEM_FONT))
        else:
            text_view.modify_font(pango.FontDescription(self.config.font))
        if self.config.use_default_theme:
            text_view.modify_text(gtk.STATE_NORMAL, DEFAULT_TEXT_COLOR)
            text_view.modify_base(gtk.STATE_NORMAL, DEFAULT_BACKGROUND_COLOR)
            text_view.modify_text(gtk.STATE_SELECTED, DEFAULT_SELECTED_TEXT_COLOR)
            text_view.modify_text(gtk.STATE_ACTIVE, DEFAULT_SELECTED_TEXT_COLOR)
            text_view.modify_base(gtk.STATE_SELECTED, DEFAULT_SELECTION_COLOR)
            text_view.modify_base(gtk.STATE_ACTIVE, DEFAULT_SELECTION_COLOR)
        else:
            text_view.modify_text(gtk.STATE_NORMAL, self.config.text_color)
            text_view.modify_base(gtk.STATE_NORMAL, self.config.background_color)
            text_view.modify_text(gtk.STATE_SELECTED, self.config.selected_color)
            text_view.modify_text(gtk.STATE_ACTIVE, self.config.selected_color)
            text_view.modify_base(gtk.STATE_SELECTED, self.config.selection_color)
            text_view.modify_base(gtk.STATE_ACTIVE, self.config.selection_color)
        text_buffer = text_view.get_buffer()
        text_buffer.set_check_brackets(self.config.check_brackets)
        text_buffer.set_language(get_lua_language())
        text_buffer.set_highlight(self.config.enable_highlight)

    def get_pages(self):
        return self.editor.get_pages()
    
    def set_show_line_numbers(self, param):
        for page in self.get_pages():
            page.get_text_view().set_show_line_numbers(param)
        self.config.show_line_numbers = param

    def get_show_line_numbers(self):
        return self.config.show_line_numbers

    def set_use_system_font(self, use):
        for page in self.get_pages():
            if use:
                page.get_text_view().modify_font(pango.FontDescription(DEFAULT_SYSTEM_FONT))
            else:
                page.get_text_view().modify_font(pango.FontDescription(self.config.font))
        self.use_system_font = use
        
    def get_use_system_font(self):
        return self.config.use_system_font
    
    def set_font(self, param):
        for page in self.get_pages():
            page.get_text_view().modify_font(pango.FontDescription(param))
        self.config.font = param

    def get_font(self):
        return self.config.font

    def set_auto_indent(self, param):
        for page in self.get_pages():
            page.get_text_view().set_auto_indent(param)
        self.config.auto_indent = param

    def get_auto_indent(self):
        return self.config.auto_indent

    def set_check_brackets(self, param):
        for page in self.get_pages():
            page.get_text_view().get_buffer().set_check_brackets(param)
        self.config.check_brackets = param

    def get_check_brackets(self):
        return self.config.check_brackets

    def set_tabs_width(self, param):
        for page in self.get_pages():
            page.get_text_view().set_tabs_width(param)
        self.config.tabs_width = param

    def get_tabs_width(self):
        return self.config.tabs_width

    def set_insert_spaces_instead_of_tabs(self, param):
        for page in self.get_pages():
            page.get_text_view().set_insert_spaces_instead_of_tabs(param)
        self.config.insert_spaces_instead_of_tabs = param

    def get_insert_spaces_instead_of_tabs(self):
        return self.config.insert_spaces_instead_of_tabs
    
    def set_highlight_current_line(self, param):
        for page in self.get_pages():
            page.get_text_view().set_highlight_current_line(param)
        self.highlight_current_line = param

    def get_highlight_current_line(self):
        return self.config.highlight_current_line

    def set_wrap_mode(self, mode):
        for page in self.get_pages():
            page.get_text_view().set_wrap_mode(mode)
        self.config.wrap_mode = mode

    def get_wrap_mode(self):
        return self.config.wrap_mode

    def set_show_margin(self, show):
        for page in self.get_pages():
            page.get_text_view().set_show_margin(show)
        self.config.show_margin = show

    def get_show_margin(self):
        return self.config.show_margin

    def set_margin(self, margin):
        for page in self.get_pages():
            page.get_text_view().set_margin(margin)
        self.config.margin = margin

    def get_margin(self):
        return self.config.margin
    
    def set_smart_home_end(self, smart):
        for page in self.get_pages():
            page.get_text_view().set_smart_home_end(smart)
        self.config.smart_home_end = smart

    def get_smart_home_end(self):
        return self.config.smart_home_end

    def set_use_default_theme(self, use):
        for page in self.get_pages():
            tv = page.get_text_view()
            if use:
                tv.modify_text(gtk.STATE_NORMAL, DEFAULT_TEXT_COLOR)
                tv.modify_base(gtk.STATE_NORMAL, DEFAULT_BACKGROUND_COLOR)
                tv.modify_text(gtk.STATE_SELECTED, DEFAULT_SELECTED_TEXT_COLOR)
                tv.modify_text(gtk.STATE_ACTIVE, DEFAULT_SELECTED_TEXT_COLOR)
                tv.modify_base(gtk.STATE_SELECTED, DEFAULT_SELECTION_COLOR)
                tv.modify_base(gtk.STATE_ACTIVE, DEFAULT_SELECTION_COLOR)
            else:
                tv.modify_text(gtk.STATE_NORMAL, self.config.text_color)
                tv.modify_base(gtk.STATE_NORMAL, self.config.background_color)
                tv.modify_text(gtk.STATE_SELECTED, self.config.selected_color)
                tv.modify_text(gtk.STATE_ACTIVE, self.config.selected_color)
                tv.modify_base(gtk.STATE_SELECTED, self.config.selection_color)
                tv.modify_base(gtk.STATE_ACTIVE, self.config.selection_color)
        self.config.use_default_theme = use
                
    def get_use_default_theme(self):
        return self.config.use_default_theme
    
    def set_text_color(self, color):
        for page in self.get_pages():
            page.get_text_view().modify_text(gtk.STATE_NORMAL, color)
        self.config.text_color = color

    def get_text_color(self):
        return self.config.text_color

    def set_background_color(self, color):
        for page in self.get_pages():
            page.get_text_view().modify_base(gtk.STATE_NORMAL, color)
        self.config.background_color = color

    def get_background_color(self):
        return self.config.background_color

    def set_selected_color(self, color):
        for page in self.get_pages():
            page.get_text_view().modify_text(gtk.STATE_SELECTED, color)
            page.get_text_view().modify_text(gtk.STATE_ACTIVE, color)
        self.config.selected_color = color

    def get_selected_color(self):
        return self.config.selected_color

    def set_selection_color(self, color):
        for page in self.get_pages():
            page.get_text_view().modify_base(gtk.STATE_SELECTED, color)
            page.get_text_view().modify_base(gtk.STATE_ACTIVE, color)
        self.config.selection_color = color

    def get_selection_color(self):
        return self.config.selection_color

    def set_highlight(self, enable):
        for page in self.get_pages():
            page.get_text_view().get_buffer().set_highlight(enable)
        self.config.enable_highlight = enable

    def get_highlight(self):
        return self.config.enable_highlight
    
    def set_view_toolbar(self, view):
        (self.editor.toolbar.hide, self.editor.toolbar.show)[view]()
        self.config.view_toolbar = view

    def get_view_toolbar(self):
        return self.config.view_toolbar

    def set_view_statusbar(self, view):
        (self.editor.statusbar.hide, self.editor.statusbar.show)[view]()
        self.config.view_statusbar = view

    def get_view_statusbar(self):
        return self.config.view_statusbar

    def get_wizard_author(self):
        return self.config.wizard_author

    def set_wizard_author(self, author):
        self.config.wizard_author = author

    def get_wizard_version(self):
        return self.config.wizard_version

    def set_wizard_version(self, version):
        self.config.wizard_version = version

    def get_wizard_license(self):
        return self.config.wizard_license

    def set_wizard_license(self, license):
        self.config.wizard_license = license

class ScriptEditorPage(gtk.HBox):
    def __init__(self, window, scriptname = None, scriptdata = None):
        gtk.HBox.__init__(self)
        self.notebook = window

        self.untitled_name = None
        self.scriptname = scriptname
        self.readonly = False
        if scriptname is None:
            self.untitled_name = self.notebook.get_untitled_name()
        else:
            self.untitled_name = None
            self.readonly = not check_access(scriptname, os.W_OK)

        if not scriptdata and scriptname:
            f = file(scriptname, "r")
            scriptdata = f.read()
            f.close()

        if not scriptdata:
            scriptdata = ""
            
        self.text_buffer = create_source_buffer(scriptdata)
        
        self.text_buffer.set_modified(False)
        self.text_view = SourceView(self.text_buffer)
        self.text_view.connect("notify::overwrite", self._overwrite_cb)
        self.text_buffer.connect("mark-set", self._mark_set_cb)
        self.text_buffer.connect("modified-changed", self._modified_changed_cb)
        self.text_buffer.connect("can-undo", window._can_undo_cb)
        self.text_buffer.connect("can-redo", window._can_redo_cb)
        self.text_buffer.connect("notify::has-selection", window._has_selection_cb)

        self.pack_start(scroll_wrap(self.text_view, False), True, True)
        self.tab_label = HIGAnimatedTabLabel(self.get_title())
        self.menu_label = gtk.Label(self.get_title())

    def _overwrite_cb(self, widget, value):
        self.update_statusbar()

    def _mark_set_cb(self, widget, it, textmark):
        if textmark == self.text_buffer.get_insert():
            self.update_statusbar()
        
    def _modified_changed_cb(self, widget):
        self.update_title()
        
    def can_redo(self):
        return self.text_buffer.can_redo()

    def can_undo(self):
        return self.text_buffer.can_undo()

    def is_untitled(self):
        return self.untitled_name != None

    def is_modified(self):
        return self.text_buffer.get_modified()
    
    def set_name(self, scriptname):
        self.scriptname = scriptname
        self.untitled_name = None
        self.update_title()

    def update_statusbar(self):
        mark = self.text_buffer.get_insert()
        it = self.text_buffer.get_iter_at_mark(mark)
        
        row = it.get_line() + 1
        col = 1
        start = it.copy()
        start.set_line_offset(0)
        tab_size = self.text_view.get_tabs_width()
        while not start.equal(it):
            if start.get_char() == '\t':
                col += tab_size
            else:
                col += 1
            start.forward_char()
            
        statusbar = self.notebook.statusbar
        context = statusbar.get_context_id("statusbar")
        statusbar.pop(context)
        statusbar.push(context, _("Ln %d, Col %d") % (row, col))
            
    def update_title(self):
        self.tab_label.set_text(self.get_title())
        self.menu_label.set_text(self.get_title())
        
    def get_title(self):
        if self.scriptname:
            title = NmapFetchScripts().nmap_path(self.scriptname)
        else:
            title = self.untitled_name
        if self.text_buffer.get_modified():
            title = "*" + title
        if self.readonly:
            title = title + " " + _("[Read Only]")
        return title

    def get_tab_label(self):
        return self.tab_label

    def get_menu_label(self):
        return self.menu_label

    def get_text_buffer(self):
        return self.text_buffer

    def get_text_view(self):
        return self.text_view
    
    def close(self):
        result = True
        if self.text_buffer.get_modified():
            message = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                        buttons=gtk.BUTTONS_YES_NO,
                        message_format=_("File have been modified."
                                    "Would you like to close it anywere?"))
            message.set_title(_("File have been modified"))
            response = message.run()
            message.destroy()
            result = response == gtk.RESPONSE_YES
        return result
            

    def save_as(self):
        file_chooser = SaveNSEFileChooserDialog(_("Save As..."))
        if not self.is_untitled():
            file_chooser.set_filename(self.scriptname)
        else:
            file_chooser.set_current_name(self.untitled_name)
        response = file_chooser.run()
        
        filename = None
        
        if not response == gtk.RESPONSE_OK:
            return
        
        filename = file_chooser.get_filename()
        # add .nse to filename if there is no other extension
        if filename.find('.') == -1:
                    filename += ".nse"

        file_chooser.destroy()
        
        self.set_name(filename)
        self.save(True)
        
    def save(self, show_alert_on_fail = False):
        if not self.is_modified():
            return
        if self.is_untitled():
            self.save_as()
            return
        
        if os.path.exists(self.scriptname):
            self.readonly = not check_access(self.scriptname, os.W_OK)
        else:
            path = os.path.dirname(self.scriptname)
            self.readonly = not check_access(path, os.W_OK)
        self.update_title()
        if self.readonly:
            if not show_alert_on_fail:
                return
            alert = HIGAlertDialog(
                message_format='<b>%s</b>' %_("File is Read Only"),
                secondary_text=_("Script Editor can't save file, because it's in read only mode."
                                 "You can use 'Save As...' option for save it in another place")
                )
            alert.run()
            alert.destroy()
        else:
            f = file(self.scriptname, "w")
            text = self.text_buffer.get_text(self.text_buffer.get_start_iter(),
                                         self.text_buffer.get_end_iter())
            f.write(text)
            f.close()
            self.text_buffer.set_modified(False)
            
    def save_as_template(self):
        """
        Save a script as a template.
        """
        file_chooser = SaveNSEFileChooserDialog(_("Save As Template..."))
        file_chooser.set_current_folder(DEFAULT_TEMPLATE_PATH)
        if not self.is_untitled():
            name = os.path.basename(self.scriptname)
            file_chooser.set_current_name(name)
        else:
            file_chooser.set_current_name(self.untitled_name)
        response = file_chooser.run()
        
        filename = None
        
        if not response == gtk.RESPONSE_OK:
            return
        
        filename = file_chooser.get_filename()
        # add .nse to filename if there is no other extension
        if filename.find('.') == -1:
                    filename += ".nse"

        file_chooser.destroy()
        
        self.set_name(filename)
        self.save(True)
        
class ScriptEditorWindow(ScriptWindow):
    _instance = None
    def __new__(cls, *args, **kwargs):
        # provide single editor with notepads
        if not cls._instance:
            cls._instance = ScriptWindow.__new__(cls, *args, **kwargs)
        return cls._instance

    _initialized = False
    def __init__(self):
        if not self._initialized:
            ScriptWindow.__init__(self)
            self.manager = ScriptEditorPageManager(self)
            self.num_untitled = 0 # untitled numeration are dependenced from editor instance
            self.clipboard = gtk.Clipboard()
            self.set_position(gtk.WIN_POS_CENTER)
            self.set_size_request(640, 480)
            self.create_widgets()
            self.update_title()
            self._initialized = True
        self.show_all()

    def get_current_page(self):
        page_num = self.notebook.get_current_page()
        if page_num == -1:
            return None
        return self.notebook.get_nth_page(page_num)
        
    def update_title(self, page_num = -1):
        if page_num == -1:
            page = self.get_current_page()
        else:
            page = self.notebook.get_nth_page(page_num)
        if not page:
            return
        page.update_title()
        title = _("Script Editor")
        title = page.get_title() + " - " + title
        self.set_title(title)

    def get_untitled_name(self):
        self.num_untitled += 1
        return "Untitled Document " + str(self.num_untitled)
    
    def create_widgets(self):
        actions = [
            ('File', None, _('_File'), None),

            ('New', gtk.STOCK_NEW,
             _('New'), "<Ctrl>N",
             _('Create a new script file'), self._new_cb),

            ('New Wizard', gtk.STOCK_NEW,
             _('_New Wizard...'), "",
             _('Create a new script file with wizard'), self._new_wizard_cb),

            ('Open', gtk.STOCK_OPEN,
             _('_Open...'), "<Control>O",
             _('Open a script files'), self._open_cb),

            ('Save', gtk.STOCK_SAVE,
             _('_Save'), "<Control>S",
             _('Save the current script file'), self._save_cb),

            ('Save As', gtk.STOCK_SAVE_AS,
             _('Save _As...'), "<Shift><Control>S",
             _('Save the current script file with the different name'), self._save_as_cb),
            
            ('Save As Template', gtk.STOCK_SAVE_AS,
             _('Save As Template...'), None,
             _('Save the current script file as template'), self._save_as_template_cb),

            ('Close', gtk.STOCK_CLOSE,
             _('_Close'), "<Ctrl>W",
             _('Close the current file'), self._close_page_cb),

            ('Quit', gtk.STOCK_QUIT,
             _('_Quit'), "<Ctrl>Q",
             _('Quit from Script Editor'), self._quit_cb),

            ('Edit', None, _('_Edit'), None),

            ('Cut', gtk.STOCK_CUT,
             _('Cu_t'), "<Ctrl>X",
             _('Cut the selection'), self._cut_cb),

            ('Copy', gtk.STOCK_COPY,
             _('_Copy'), "<Ctrl>C",
             _('Copy the selection'), self._copy_cb),

            ('Paste', gtk.STOCK_PASTE,
             _('_Paste'), "<Ctrl>V",
             _('Paste the clipboard'), self._paste_cb),

            ('Undo', gtk.STOCK_UNDO,
             _('_Undo'), "<Ctrl>Z",
             _('Undo'), self._undo_cb),

            ('Redo', gtk.STOCK_REDO,
             _('_Redo'), "<Ctrl>R",
             _('Redo'), self._redo_cb),

            ('Delete', gtk.STOCK_DELETE,
             _('_Delete'), None,
             _('Delete the selected text'), self._delete_cb),
            
            ('Select All', None,
             _('Select _All'), "<Ctrl>A",
             _('Select the entire document'), self._select_all_cb),

            ('Indent', gtk.STOCK_INDENT,
             _('_Indent'), "Tab",
             _('Indent selected lines'), self._indent_cb),

            ('Unindent', gtk.STOCK_UNINDENT,
             _('U_nindent'), "<Shift>Tab",
             _('Unindent selected lines'), self._unindent_cb),

            ('Preferences', gtk.STOCK_PREFERENCES,
             _('Preferences'), None,
             _('Script Manager settings'), self._preferences_cb),

            ('View', None, _('_View'), None),

            ('Documents', None, _('_Documents'), None),

            ('Save All', gtk.STOCK_SAVE,
             _('_Save All'), "<Shift><Ctrl>L",
             _('Save all open files'), self._save_all_cb),
            
            ('Close All', gtk.STOCK_CLOSE,
             _('_Close All'), "<Shift><Ctrl>W",
             _('Close all open files'), self._close_all_cb),

            ('Previous Document', None,
             _('Previous Document'), "<Shift><Ctrl>Page_Up",
             _('Activate previous document'), self._prev_document_cb),

            ('Next Document', None,
             _('Next Document'), "<Shift><Ctrl>Page_Down",
             _('Activate next document'), self._next_document_cb),

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
             _('Show/hide statusbar'), self._statusbar_cb, True)
        ]
        
        ui = """<menubar>
        <menu action='File'>
            <menuitem action='New'/>
            <menuitem action='New Wizard'/>
            <separator/>
            <menuitem action='Open'/>
            <menuitem action='Save'/>
            <menuitem action='Save As'/>
            <menuitem action='Save As Template'/>
            <separator/>
            <menuitem action='Close'/>
            <menuitem action='Quit'/>
        </menu>
        <menu action='Edit'>
            <menuitem action='Undo'/>
            <menuitem action='Redo'/>
            <separator/>
            <menuitem action='Cut'/>
            <menuitem action='Copy'/>
            <menuitem action='Paste'/>
            <menuitem action='Delete'/>
            <separator/>
            <menuitem action='Select All'/>
            <separator/>
            <menuitem action='Indent'/>
            <menuitem action='Unindent'/>
            <separator/>
            <menuitem action='Preferences'/>
        </menu>
        <menu action='View'>
            <menuitem action='Toolbar'/>
            <menuitem action='Statusbar'/>
        </menu>
        <menu action='Documents'>
            <menuitem action='Save All'/>
            <menuitem action='Close All'/>
            <separator/>
            <menuitem action='Previous Document'/>
            <menuitem action='Next Document'/>
            <placeholder name='DocumentsList'>
                <separator/>
            </placeholder>
        </menu>
        <menu action='Help'>
            <menuitem action='Show Help'/>
            <menuitem action='Report a bug'/>
        </menu>
        </menubar>

        <toolbar>
            <toolitem action='New'/>
            <toolitem action='Open'/>
            <toolitem action='Save'/>
            <separator/>
            <toolitem action='Cut'/>
            <toolitem action='Copy'/>
            <toolitem action='Paste'/>
            <separator/>
            <toolitem action='Undo'/>
            <toolitem action='Redo'/>
        </toolbar>
        """

        self.create_layout(actions, toggle_actions, ui)
        self.action_group.get_action('Toolbar').set_active(self.manager.get_view_toolbar())
        self.action_group.get_action('Statusbar').set_active(self.manager.get_view_statusbar())
        #self.connect("destroy-event", self._destroy_cb)
        self.connect("delete-event", self._delete_event_cb)
        self.clipboard.connect("owner-change", self._owner_change_cb)

    def show_all(self):
        ScriptWindow.show_all(self)
        (self.toolbar.hide, self.toolbar.show)[self.manager.get_view_toolbar()]()
        (self.statusbar.hide, self.statusbar.show)[self.manager.get_view_statusbar()]()
        
    def create_main(self):
        self.notebook = HIGNotebook()
        self.notebook.set_tab_pos(gtk.POS_TOP)
        self.notebook.set_scrollable(True)
        self.notebook.connect("switch-page", self._switch_page_cb)
        return self.notebook

    def get_pages(self):
        res = []
        for num in range(self.notebook.get_n_pages()):
            res.append(self.notebook.get_nth_page(num))
        return res

    def new_file_wizard(self):
        dialog = ScriptEditorWizardDialog(self)
        if dialog.run() == gtk.RESPONSE_OK:
            script = dialog.get_script()
            self.open_file(scriptdata=script)
        dialog.destroy()
        
    def open_file(self, scriptname = None, scriptdata = None, new = True):
        # test if already opened
        if scriptname:
            for num, name in enumerate([p.scriptname for p in self.get_pages()]):
                if name == scriptname:
                    self.notebook.set_current_page(num)
                    return
                
        page = ScriptEditorPage(self, scriptname, scriptdata)
        # if its new file, set to modified
        if new:
            page.text_buffer.set_modified(True)
        self.manager.init_page(page)
        tab_label = page.get_tab_label()
        tab_label.connect("close-clicked", self._close_page_cb, page)
        menu_label = page.get_menu_label()
        self.notebook.append_page_menu(page, tab_label, menu_label)
        self.notebook.show_all()
        self.notebook.set_current_page(self.notebook.page_num(page))
        page.get_text_view().grab_focus()

    def _delete_event_cb(self, widget, event):
        # remove singletone on delete event
        result = self.close_all()
        if result:
            self.__class__._instance = None
            self._initialized = False
        return not result 

    def _received_clipboard_contents(self, clipboard, selection_data, data = None):
        page = self.get_current_page()
        if page:
            sens = selection_data.targets_include_text()
        else:
            sens = False
        action = self.action_group.get_action("Paste")
        action.set_sensitive(sens)
        
    def _owner_change_cb(self, widget, param = None):
        display = self.clipboard.get_display()
        if display.supports_selection_notification():
            self.clipboard.request_contents(gtk.gdk.atom_intern("TARGETS", False),
                                            self._received_clipboard_contents)
        else:
            action = self.action_group.get_action("Paste")
            action.set_sensitive(True)
        
    def _new_cb(self, p):
        self.open_file()

    def _new_wizard_cb(self, p):
        self.new_file_wizard()
        
    def _open_cb(self, p):
        file_chooser = NSEFileChooserDialog(_("Open files..."))
        file_chooser.set_select_multiple(True)
        response = file_chooser.run()
        filenames = file_chooser.get_filenames()
        file_chooser.destroy()
        if not response == gtk.RESPONSE_OK:
            return
        for name in filenames:
            self.open_file(scriptname = name, new = False)
       
    def _save_cb(self, p):
        page = self.get_current_page()
        if page.is_untitled():
            page.save_as()
        else:
            page.save(True)
        self.update_title()

    def _save_as_cb(self, p):
        page = self.get_current_page()
        if not page:
            return
        page.save_as()
        self.update_title()
        
    def _save_as_template_cb(self, p):
        page = self.get_current_page()
        if not page:
            return
        page.save_as_template()
        self.update_title()

    def _quit_cb(self, p):
        if self.close_all():
            self.destroy()
            self.__class__._instance = None
            self._initialized = False

    def _cut_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_buffer().cut_clipboard(self.clipboard,
                                               page.get_text_view().get_editable())

    def _copy_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_buffer().copy_clipboard(self.clipboard)

    def _paste_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_buffer().paste_clipboard(self.clipboard, None,
                                                 page.get_text_view().get_editable())

    def _can_undo_cb(self, p, value):
        action = self.action_group.get_action('Undo')
        action.set_sensitive(value)

    def _can_redo_cb(self, p, value):
        action = self.action_group.get_action('Redo')
        action.set_sensitive(value)

    def _has_selection_cb(self, p, value):
        page = self.get_current_page()
        if page:
            res = page.get_text_buffer().get_has_selection()
        else:
            res = False
        action = self.action_group.get_action("Cut")
        action.set_sensitive(res)
        action = self.action_group.get_action("Copy")
        action.set_sensitive(res)
        action = self.action_group.get_action("Delete")
        action.set_sensitive(res)
        
    def _undo_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_buffer().undo()

    def _redo_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_buffer().redo()

    def _delete_cb(self, p):
        page = self.get_current_page()
        if page:
            buf = page.get_text_buffer()
            buf.delete_selection(True, page.get_text_view().get_editable())

    def _select_all_cb(self, p):
        page = self.get_current_page()
        if page:
            buffer = page.get_text_buffer()
            buffer.select_range(buffer.get_start_iter(), buffer.get_end_iter())

    def _indent_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_view().indent_lines()

    def _unindent_cb(self, p):
        page = self.get_current_page()
        if page:
            page.get_text_view().unindent_lines()
            
    def _preferences_cb(self, p):
        dialog = ScriptEditorPreferencesDialog(self)
        dialog.run()
        dialog.destroy()
        #self.manager.save_changes()

    def _toolbar_cb(self, toggle):
        (self.toolbar.hide, self.toolbar.show)[toggle.get_active()]()
        self.manager.set_view_toolbar(toggle.get_active())
    
    def _statusbar_cb(self, toggle):
        (self.statusbar.hide, self.statusbar.show)[toggle.get_active()]()
        self.manager.set_view_statusbar(toggle.get_active())

    def _close_page_cb(self, widget, page = None):
        if not page:
            page = self.get_current_page()
        if not page or not page.close():
            return 
        num = self.notebook.page_num(page)
        if num != -1:
            self.notebook.remove_page(num)
            self.update_title()
            self._update_prev_next_cb()

    def _save_all_cb(self, widget):
        for page in self.get_pages():
            page.save(False)

    def close_all(self):
        modified = 0
        for page in self.get_pages():
            if page.is_modified():
                modified += 1
        result = True
        if modified > 0: 
            message = gtk.MessageDialog(type=gtk.MESSAGE_QUESTION,
                        buttons=gtk.BUTTONS_YES_NO,
                        message_format=_("%d files are modified."
                                    "Would you like to close all documents anywere?") % modified)
            message.set_title(_("%d files are modified") % modified)
            response = message.run()
            message.destroy()
            result = response == gtk.RESPONSE_YES
        if result:
            while self.notebook.get_n_pages() > 0:
                self.notebook.remove_page(-1)
        return result
        
    def _close_all_cb(self, widget):
        return not self.close_all()
    
    def _prev_document_cb(self, widget):
        self.notebook.prev_page()

    def _next_document_cb(self, widget):
        self.notebook.next_page()

    def _show_bug_report_cb(self, p):
        BugReport().show_all()

    def _show_help_cb(self, p):
        import webbrowser
        webbrowser.open("file://%s" % os.path.join(Path.docs_dir, "script_editor.html"), new=2)

    def _update_prev_next_cb(self, page_num = -1):
        if page_num == -1:
            page_num = self.notebook.get_current_page()
        action = self.action_group.get_action("Previous Document")
        action.set_sensitive(page_num > 0)
        action = self.action_group.get_action("Next Document")
        action.set_sensitive(page_num < self.notebook.get_n_pages() - 1)
        
    def _switch_page_cb(self, widget, page, page_num):
        self.update_title(page_num)
        page = self.notebook.get_nth_page(page_num)
        self._can_undo_cb(self, page.can_undo())
        self._can_redo_cb(self, page.can_redo())
        self._has_selection_cb(self, page.get_text_buffer().get_has_selection())
        self._update_prev_next_cb(page_num)

class ScriptEditorWizardDialog(HIGDialog):
    def __init__(self, editor):
        HIGDialog.__init__(self, _("New Script Wizard"), editor,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE,
                            gtk.STOCK_OK, gtk.RESPONSE_OK,
                            gtk.STOCK_HELP, gtk.RESPONSE_HELP))
        self.manager = editor.manager
        self.set_size_request(400, 500)
        self.create_widgets()

    def create_widgets(self):
        def create_entry(table, level, label, default = ""):
            lbl = HIGEntryLabel(label)
            entry = HIGTextEntry()
            entry.set_text(default)
            lbl.set_mnemonic_widget(entry)
            table.attach(lbl, 0, 1, level, level + 1, 0, 0)
            table.attach(entry, 1, 2, level, level + 1)
            return entry

        def create_checkboxes(table, labels_list):
            boxes = dict()
            for i, label in enumerate(labels_list):
                y, x = divmod(i, 2)
                check = gtk.CheckButton(label)
                table.attach(check, x, x + 1, y, y + 1)
                boxes[label] = check
            return boxes
            
        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_border_width(5)
        scrolled_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.vbox.pack_start(scrolled_window, True, True, 0)
        scrolled_window.show()
        
        self.vbox1 = gtk.VBox()
        self.vbox1.pack_start(HIGSectionLabel(_("General")), False, False)
        table = HIGTable(5, 2)
        self.id_entry = create_entry(table, 0, "<b>ID:</b>")
        self.author_entry = create_entry(table, 1, "Author:", self.manager.get_wizard_author())
        self.version_entry = create_entry(table, 2, "Version:", self.manager.get_wizard_version())
        self.license_entry = create_entry(table, 3, "License:", self.manager.get_wizard_license())
        lbl = HIGEntryLabel("Rule:")
        table.attach(lbl, 0, 1, 4, 5, 0, 0)
        hbox = HIGHBox()
        self.port_rule = gtk.RadioButton(None, "Port")
        hbox.pack_start(self.port_rule)
        self.host_rule = gtk.RadioButton(self.port_rule, "Host")
        hbox.pack_start(self.host_rule)
        table.attach(hbox, 1, 2, 4, 5)
        self.vbox1.pack_start(HIGSpacer(table), False, False)
        self.vbox1.pack_start(HIGSpacer())

        self.vbox1.pack_start(HIGSectionLabel(_("Categories")), False, False)
        table = HIGTable(4, 2)
        self.categories = create_checkboxes(table,
                                            ["backdoor",
                                             "demo",
                                             "discovery",
                                             "intrusive",
                                             "malware",
                                             "safe",
                                             "version",
                                             "vulnerability"])
        self.vbox1.pack_start(HIGSpacer(table), False, False)
        self.vbox1.pack_start(HIGSpacer())

        self.vbox1.pack_start(HIGSectionLabel(_("User Template")), False, False)
        table = HIGTable(1, 2)
        self.templates = gtk.combo_box_new_text()
        self.templates.append_text("")
        for template in get_templates():
            self.templates.append_text(template)
        self.templates.connect('changed', self._template_changed_cb)
        table.attach(self.templates, 0, 1, 0, 1)
        lbl = HIGEntryLabel("")
        table.attach(lbl, 1, 2, 0, 1)
        self.vbox1.pack_start(table, False, False)
        self.vbox1.pack_start(HIGSpacer(table), False, False)

        self.vbox1.pack_start(HIGSectionLabel(_("Description")), False, False)
        self.desc_view = HIGTextView()
        self.vbox1.pack_start(HIGSpacer(scroll_wrap(self.desc_view)))
        
        scrolled_window.add_with_viewport(self.vbox1)
        self.vbox1.show()
        
        self.connect("response", self._response_cb)        
        self.show_all()

    stub = '''\
id = "%(id)s"

author = "%(author)s"

version = "%(version)s"

license = "%(license)s"

categories = {%(categories)s}

description = "%(desc)s"

%(rule)s

%(content)s

'''
    
    default_content = '''\
action = function(host, port)
\t-- main testing actions here
\treturn
end
'''

    def get_script(self):
        id = self.id_entry.get_text()
        author = self.author_entry.get_text()
        version = self.version_entry.get_text()
        license = self.license_entry.get_text()
        template = self.templates.get_active_text()
        
        if template == "" or template==None:
            content = self.default_content
            if self.port_rule.get_active():
                rule = '''portrule = function(host, port)
    \tdecision = true
    \t-- port choosing here
    \treturn decision
    end'''
            else:
                rule = '''hostrule = function(host, port)
    \tdecision = true
    \t-- host choosing here
    \treturn decision
    end'''
        else:
            rule = ''
            content = self.content
            pass
            
        categories = []
        for name, check in self.categories.items():
            if check.get_active():
                categories.append('"' + name + '"')
        categories = ", ".join(categories)

        buf = self.desc_view.get_buffer()
        desc = "\\\n".join(buf.get_text(buf.get_start_iter(), buf.get_end_iter()).splitlines())

        result = self.stub % locals()
        
        if self.manager.get_insert_spaces_instead_of_tabs():
             result = result.replace('\t', ' ' * self.manager.get_tabs_width())
        # save some values
        self.manager.set_wizard_author(author)
        self.manager.set_wizard_version(version)
        self.manager.set_wizard_license(license)
        
        return result

    def _response_cb(self, dialog, response_id):
        if response_id != gtk.RESPONSE_HELP:
            return
        import webbrowser
        webbrowser.open("file://%s" %
                        os.path.join(Path.docs_dir, "script_editor.html#wizard"), new=2)
        self.stop_emission("response")
        
    def _template_changed_cb(self, combobox):
        """
        Update fields with template content
        """
        if combobox.get_active_text()!='':
            template = DEFAULT_TEMPLATE_PATH + '/' + combobox.get_active_text()
            parser = LuaParser(template)
            d = {}
            d.update(parser.attr)
            
            id = d.get('id', '')
            author = d.get('author', '')
            version = d.get('version_', '')
            license = d.get('license', '')
            description = d.get('description', '')
            categories = d.get('categories', '')
            self.content = d.get('content', '')
            categories = categories.split(',')
            
            for name, check in self.categories.items():
                check.set_active(name in categories)
                
            # update entries
            self.id_entry.set_text(id)
            self.author_entry.set_text(author)
            self.version_entry.set_text(version)
            self.license_entry.set_text(license)
            self.desc_view.get_buffer().set_text(description)
        else:
            self._clear_all()
            
    def _clear_all(self):
        """
        Clear all text fields.
        """
        self.id_entry.set_text('')
        self.author_entry.set_text('')
        self.version_entry.set_text('')
        self.license_entry.set_text('')
        self.desc_view.get_buffer().set_text('')
        self.content = ''
        
        for name, check in self.categories.items():
            check.set_active(False)
        
    
class ScriptEditorPreferencesDialog(HIGDialog):
    def __init__(self, editor):
        HIGDialog.__init__(self, _("Script Manager Preferences"), editor,
                           gtk.DIALOG_MODAL,
                           (gtk.STOCK_CLOSE, gtk.RESPONSE_CLOSE,
                            gtk.STOCK_HELP,  gtk.RESPONSE_HELP))
        self.manager = editor.manager
        self.set_resizable(False)
        self.create_widgets()

    def _toggled_cb(self, widget, func):
        func(widget.get_active())

    def _spin_cb(self, widget, func):
        func(int(widget.get_value()))

    def _wrap_cb(self, widget, w1, w2):
        w2.set_sensitive(w1.get_active())
        if w1.get_active():
            mode = (gtk.WRAP_CHAR, gtk.WRAP_WORD)[int(w2.get_active())]
        else:
            mode = gtk.WRAP_NONE
        self.manager.set_wrap_mode(mode)

    def _font_cb(self, widget, buttons):
        buttons.set_sensitive(not widget.get_active())
        self.manager.set_use_system_font(widget.get_active())

    def _font_set_cb(self, widget):
        self.manager.set_font(widget.get_font_name())

    def _color_cb(self, widget, buttons):
        buttons.set_sensitive(not widget.get_active())
        self.manager.set_use_default_theme(widget.get_active())
    
    def _color_set_cb(self, widget, func):
        func(widget.get_color())
    
    def create_tab_view(self):
        mainvbox = HIGVBox()
        mainvbox.set_border_width(8)
        mainvbox.pack_start(HIGSectionLabel(_("Text Wrapping")), False, False)
        vbox = HIGVBox()
        w1 = gtk.CheckButton(_("Enable text _wrapping"))
        b1 = self.manager.get_wrap_mode() != gtk.WRAP_NONE
        w1.set_active(b1)
        vbox.pack_start(w1)
        w2 = gtk.CheckButton(_("Do not _split words over two lines"))
        w2.set_sensitive(b1)
        if b1:
            w2.set_active(self.manager.get_wrap_mode() == gtk.WRAP_WORD)
        w1.connect("toggled", self._wrap_cb, w1, w2)
        w2.connect("toggled", self._wrap_cb, w1, w2)
        vbox.pack_start(w2)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        mainvbox.pack_start(HIGSectionLabel(_("Line Numbers")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("_Display line numbers"))
        widget.set_active(self.manager.get_show_line_numbers())
        widget.connect("toggled", self._toggled_cb, self.manager.set_show_line_numbers)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        mainvbox.pack_start(HIGSectionLabel(_("Current Line")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("Hi_ghlight current line"))
        widget.set_active(self.manager.get_highlight_current_line())
        widget.connect("toggled", self._toggled_cb, self.manager.set_highlight_current_line)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        mainvbox.pack_start(HIGSectionLabel(_("Right Margin")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("Display right _margin"))
        widget.set_active(self.manager.get_show_margin())
        widget.connect("toggled", self._toggled_cb, self.manager.set_show_margin)
        vbox.pack_start(widget)
        hbox = HIGHBox()
        lbl = gtk.Label(_("_Right margin at column:"))
        lbl.set_use_underline(True)
        hbox.pack_start(lbl, False, False)
        widget = gtk.SpinButton(gtk.Adjustment(self.manager.get_margin(), 1, 160), 1.0)
        widget.connect("value-changed", self._spin_cb, self.manager.set_margin)
        widget.set_increments(1, 10)
        lbl.set_mnemonic_widget(widget)
        hbox.pack_start(widget, False, False)
        vbox.pack_start(hbox)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        mainvbox.pack_start(HIGSectionLabel(_("Bracket Matching")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("Highlight matching _bracket"))
        widget.set_active(self.manager.get_check_brackets())
        widget.connect("toggled", self._toggled_cb, self.manager.set_check_brackets)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        return mainvbox

    def create_tab_editor(self):
        mainvbox = HIGVBox()
        mainvbox.set_border_width(8)
        mainvbox.pack_start(HIGSectionLabel(_("Tab Stops")), False, False)
        vbox = HIGVBox()
        hbox = HIGHBox()
        lbl = gtk.Label(_("_Tab width:"))
        lbl.set_use_underline(True)
        hbox.pack_start(lbl, False, False)
        widget = gtk.SpinButton(gtk.Adjustment(self.manager.get_tabs_width(), 1, 24), 0.0)
        widget.connect("value-changed", self._spin_cb, self.manager.set_tabs_width)
        widget.set_increments(1, 4)
        lbl.set_mnemonic_widget(widget)
        hbox.pack_start(widget, False, False)
        vbox.pack_start(hbox)
        widget = gtk.CheckButton(_("Insert _spaces instead of tabs"))
        widget.set_active(self.manager.get_insert_spaces_instead_of_tabs())
        widget.connect("toggled", self._toggled_cb, self.manager.set_insert_spaces_instead_of_tabs)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)

        mainvbox.pack_start(HIGSectionLabel(_("Automatic Indentation")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("_Enable automatic indentation"))
        widget.set_active(self.manager.get_auto_indent())
        widget.connect("toggled", self._toggled_cb, self.manager.set_auto_indent)
        vbox.pack_start(widget)
        widget = gtk.CheckButton(_("Smart _Home/End"))
        widget.set_active(self.manager.get_smart_home_end())
        widget.connect("toggled", self._toggled_cb, self.manager.set_smart_home_end)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)
        
        mainvbox.pack_start(HIGSectionLabel(_("Syntax Highlight")), False, False)
        vbox = HIGVBox()
        widget = gtk.CheckButton(_("Enable syntax _highlight"))
        widget.set_active(self.manager.get_highlight())
        widget.connect("toggled", self._toggled_cb, self.manager.set_highlight)
        vbox.pack_start(widget)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)
        
        return mainvbox
        
    def create_tab_font(self):
        def create_color_widget(level, table, label, color, func):
            lbl = gtk.Label(label)
            lbl.set_use_underline(True)
            widget = gtk.ColorButton(color)
            widget.connect("color-set", self._color_set_cb, func)
            lbl.set_mnemonic_widget(widget)
            table.attach(lbl, 0, 1, level, level + 1, gtk.FILL, 0)
            table.attach(widget, 1, 2, level, level + 1)
            
        mainvbox = HIGVBox()
        mainvbox.set_border_width(8)

        mainvbox.pack_start(HIGSectionLabel(_("Font")), False, False)
        vbox = HIGVBox()
        check = gtk.CheckButton(_("_Use the system fixed width font (%s)") % DEFAULT_SYSTEM_FONT)
        vbox.pack_start(check)
        hbox = HIGHBox()
        lbl = gtk.Label(_("Editor _font:"))
        lbl.set_use_underline(True)
        hbox.pack_start(lbl, False, False)
        widget = gtk.FontButton(self.manager.get_font())
        widget.connect("font-set", self._font_set_cb)
        lbl.set_mnemonic_widget(widget)
        hbox.pack_start(widget, True, True)
        vbox.pack_start(hbox)
        check.connect("toggled", self._font_cb, hbox)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)
        check.set_active(self.manager.get_use_system_font())
        hbox.set_sensitive(not self.manager.get_use_system_font())

        mainvbox.pack_start(HIGSectionLabel(_("Colors")), False, False)
        vbox = HIGVBox()
        check = gtk.CheckButton(_("U_se default theme colors"))
        vbox.pack_start(check)
        table = HIGTable(4, 2)
        create_color_widget(0, table, _("Normal _text color:"),
                            self.manager.get_text_color(),
                            self.manager.set_text_color)
        create_color_widget(1, table, _("_Background color:"),
                            self.manager.get_background_color(),
                            self.manager.set_background_color)
        create_color_widget(2, table, _("Selecte_d text color:"),
                            self.manager.get_selected_color(),
                            self.manager.set_selected_color)
        create_color_widget(3, table, _("Se_lection color:"),
                            self.manager.get_selection_color(),
                            self.manager.set_selection_color)
        vbox.pack_start(table)
        check.connect("toggled", self._color_cb, table)
        mainvbox.pack_start(HIGSpacer(vbox), False, False)
        check.set_active(self.manager.get_use_default_theme())
        table.set_sensitive(not self.manager.get_use_default_theme())
        return mainvbox
        
    def create_widgets(self):
        notebook = HIGNotebook()
        notebook.set_tab_pos(gtk.POS_TOP)
        notebook.append_page(self.create_tab_view(), gtk.Label(_("View")))
        notebook.append_page(self.create_tab_editor(), gtk.Label(_("Editor")))
        notebook.append_page(self.create_tab_font(), gtk.Label(_("Font & Colors")))
        self.vbox.add(notebook)
        self.connect("response", self._response_cb)
        self.show_all()

    def _response_cb(self, dialog, response_id):
        if response_id != gtk.RESPONSE_HELP:
            return
        import webbrowser
        webbrowser.open("file://%s" %
                        os.path.join(Path.docs_dir, "script_editor.html#preferences"), new=2)
        self.stop_emission("response")
        
if __name__ == "__main__":
    editor = ScriptEditorWindow()
    editor.open_file()
    editor.show_all()
    editor.connect("destroy", gtk.main_quit)
    gtk.main()

