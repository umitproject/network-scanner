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
#import pygtk
#pygtk.require('2.0')

import gettext
gettext.install('pysourceview')

import os, os.path
import re

import gtk
from gtk import TextView, TextBuffer, TextIter, Style
from gtk import gdk
import pango
import gobject
import pango

from umit.core.Paths import Path
from xml.dom import minidom

# defines
GUTTER_PIXMAP = 16

TARGET_COLOR = 200 # DnD color 

MAX_CHARS_BEFORE_FINDING_A_MATCH = 2000
MIN_NUMBER_WINDOW_WIDTH = 20

DEFAULT_TAB_WIDTH = 8
MAX_TAB_WIDTH = 32

DEFAULT_MARGIN = 80
MAX_MARGIN = 200

DEFAULT_MAX_UNDO_LEVELS = -1

SOURCEVIEW_DIR = "pysourceview-2.0"
#RGN_SCHEMA_FILE = "language2.rgn"
LANG_FILE_SUFFIX = ".lang"
DEFAULT_SECTION = _("Others")
GTK_SOURCE_LANGUAGE_VERSION_1_0 = 100
GTK_SOURCE_LANGUAGE_VERSION_2_0 = 200

# aux

def get_default_dirs(basename, compat):
    # TODO: dirs parsing
    return [os.path.join("umit", "nsefacilitator", basename)]

def get_file_list(dirs, suffix):
    result = []
    try:
        for path in dirs:
            for filename in os.listdir(path):
                fullpath = os.path.join(path, filename)
                if fullpath.endswith(suffix) and os.path.isfile(fullpath):
                    result.append(fullpath)
    except OSError:
        pass
    return result

# XML parsing aux
def get_string(node):
    return "".join([x.data for x in node.childNodes if x.nodeType == x.TEXT_NODE])

def string_to_bool(string):
    if string:
        return string.lower() in ("yes", "true", "1")
    return False
        
def get_attr(node, name, default = None):
    if node.hasAttribute(name):
        return node.getAttribute(name)
    return default

def get_bool(node, name, default = False):
    if node.hasAttribute(name):
        return string_to_bool(node.getAttribute(name))
    return default

# SourceStyle
class SourceStyle(Style):
    __gproperties__ = {
        "background" : (gobject.TYPE_STRING,
                        _("Background"),
                        _("Background color"),
                        None,
                        gobject.PARAM_READWRITE),

        "foreground" : (gobject.TYPE_STRING,
                        _("Foreground"),
                        _("Foreground color"),
                        None,
                        gobject.PARAM_READWRITE),
        
        "bold" : (gobject.TYPE_BOOLEAN,
                  _("Bold"),
                  _("Bold"),
                  False,
                  gobject.PARAM_READWRITE),
        
        "italic" : (gobject.TYPE_BOOLEAN,
                    _("Italic"),
                    _("Italic"),
                    False,
                    gobject.PARAM_READWRITE),
        
        "underline" : (gobject.TYPE_BOOLEAN,
                       _("Underline"),
                       _("Underline"),
                       False,
                       gobject.PARAM_READWRITE),
        
        "strikethrough" : (gobject.TYPE_BOOLEAN,
                           _("Strikethrough"),
                           _("Striketrhough"),
                           False,
                           gobject.PARAM_READWRITE),
        
        "foreground-set" : (gobject.TYPE_BOOLEAN,
                            _("Foreground set"),
                            _("Whether foreground color is set"),
                            False,
                            gobject.PARAM_READWRITE),
        
        "background-set" : (gobject.TYPE_BOOLEAN,
                            _("Background set"),
                            _("Whether background color is set"),
                            False,
                            gobject.PARAM_READWRITE),
        
        "bold-set" : (gobject.TYPE_BOOLEAN,
                      _("Bold set"),
                      _("Whether bold attribute is set"),
                      False,
                      gobject.PARAM_READWRITE),
        
        "italic-set" : (gobject.TYPE_BOOLEAN,
                        _("Italic set"),
                        _("Whether italic attribute is set"),
                        False,
                        gobject.PARAM_READWRITE),
        
        "underline-set" : (gobject.TYPE_BOOLEAN,
                           _("Underline set"),
                           _("Whether underline attribute is set"),
                           False,
                           gobject.PARAM_READWRITE),
        
        "striketrhough-set" : (gobject.TYPE_BOOLEAN,
                               _("Strikethrough set"),
                               _("Whether strikethrough attribute is set"),
                               False,
                               gobject.PARAM_READWRITE)
        }
    
    def __init__(self):
        Style.__init__(self)
        self.use_foreground = False
        self.foreground = None
        self.use_background = False
        self.background = None
        self.use_italic = False
        self.italic = False
        self.use_bold = False
        self.bold = False
        self.use_underline = False
        self.underline = False
        self.use_strikethrough = False
        self.strikethrough = False

    def set_foreground(self, value):
        self.foreground = value

    def get_foreground(self):
        return self.foreground

    def set_background(self, value):
        self.background = value

    def get_background(self):
        return self.background

    def set_bold(self, value):
        self.bold = value

    def get_bold(self):
        return self.bold

    def set_italic(self, value):
        self.italic = value

    def get_italic(self):
        return self.italic

    def set_underline(self, value):
        self.underline = value

    def get_underline(self):
        return self.underline

    def set_strikethrough(self, value):
        self.strikethrough = value

    def get_strikethrough(self):
        return self.strikethrough

    def set_foreground_set(self, value):
        self.use_foreground = value

    def get_foreground_set(self):
        return self.use_foreground

    def set_background_set(self, value):
        self.use_background = value
        
    def get_background_set(self):
        return self.use_background

    def set_bold_set(self, value):
        self.use_bold = value
        
    def get_bold_set(self):
        return self.use_bold

    def set_italic_set(self, value):
        self.use_italic = value

    def get_italic_set(self):
        return self.use_italic

    def set_underline_set(self, value):
        self.use_underline = value

    def get_underline_set(self):
        return self.use_underline

    def set_strikethrough_set(self, value):
        self.use_strikethrough = value

    def get_strikethrough_set(self):
        return self.use_strikethrough
    
    _property_map = {
        'foreground': (set_foreground, get_foreground),
        'background': (set_background, get_background),
        'bold'      : (set_bold, get_bold),
        'italic'    : (set_italic, get_italic),
        'underline' : (set_underline, get_underline),
        'strikethrough' : (set_strikethrough, get_strikethrough),
        'foreground-set': (set_foreground_set, get_foreground_set),
        'background-set': (set_background_set, get_background_set),
        'bold-set'  : (set_bold_set, get_bold_set),
        'italic-set': (set_italic_set, get_italic_set),
        'underline-set': (set_underline_set, get_underline_set),
        'strikethrough-set': (set_strikethrough_set, get_strikethrough_set)
    }
    
    def get_property(self, property):
        if property.name in self._property_map:
            f = self._property_map[property.name][1]
            if f:
                return f()
        raise AttributeError, 'unknown property %s' % property.name
        
    def set_property(self, property, value):
        if property.name in self._property_map:
            f = self._property_map[property.name][0]
            if f:
                return f(value)
        raise AttributeError, 'unknown property %s' % property.name

    def apply(self, tag):
        tag.freeze_notify()
        if self.use_background:
            tag.set_property('background', self.background)
        if self.use_foreground:
            tag.set_property('foreground', self.foreground)
        if self.use_italic:
            tag.set_property('style', (pango.STYLE_NORMAL, pango.STYLE_ITALIC)[self.italic])
        if self.use_bold:
            tag.set_property('weight', (pango.WEIGHT_NORMAL, pango.WEIGHT_BOLD)[self.bold])
        if self.use_underline:
            tag.set_property('underline', (pango.UNDERLINE_NONE, pango.UNDERLINE_SINGLE)[self.underline])
        if self.use_strikethrough:
            tag.set_property('strikethrough', self.strikethrough)
        tag.thaw_notify()
                            

# SourceStyleScheme
class SourceStyleScheme(gobject.GObject):
    def __init__(self):
        self.styles = dict()

    def get_style(self, name):
        return self.styles.get(name, SourceStyle())

    def set_style(self, name, style):
        self.styles[name] = style

    def apply(self, widget):
        # TODO: currently work around style scheme throw modify_base for view widget
        pass

    def get_matching_brackets_style(self):
        return self.get_style("bracket-match")

    def get_current_line_color(self):
        style = self.get_style("current-line")
        if style.get_foreground_set():
            return gdk.color_parse(style.get_foreground())
        elif style.get_background_set():
            return gdk.color_parse(style.get_background())
        else:
            return None
        
    @staticmethod
    def get_default():
        return SourceStyleScheme.new_from_file(os.path.join(Path.styles_dir, "gvim.xml"))
    
    @staticmethod
    def new_from_file(filename):
        try:
            xml = minidom.parse(filename)
        except Exception, e:
            return None
        scheme = SourceStyleScheme()
        # parse element
        node = xml.documentElement
        if node.tagName != "style-scheme":
            return None
        scheme.id = get_attr(node, "id")
        if not scheme.id:
            return None
        scheme.name = get_attr(node, "_name")
        if not scheme.name:
            scheme.name = get_attr(node, "name")
            if not scheme.name:
                return None
        scheme.parent_id = get_attr(node, "parent-scheme")
        for child in node.childNodes:
            if child.nodeType != child.ELEMENT_NODE:
                continue
            if child.tagName == "style":
                style_name = get_attr(child, "name")
                if not style_name:
                    continue
                use_style = get_attr(child, "use-style")
                if use_style:
                    style = scheme.get_style(use_style)
                else:
                    style = SourceStyle()
                    fg = get_attr(child, "foreground")
                    if fg:
                        style.set_foreground_set(True)
                        style.set_foreground(fg)
                    bg = get_attr(child, "background")
                    if bg:
                        style.set_background_set(True)
                        style.set_background(bg)
                    if get_bool(child, "italic"):
                        style.set_italic_set(True)
                        style.set_italic(True)
                    if get_bool(child, "bold"):
                        style.set_bold_set(True)
                        style.set_bold(True)
                    if get_bool(child, "underline"):
                        style.set_underline_set(True)
                        style.set_underline(True)
                    if get_bool(child, "strikethrough"):
                        style.set_strikethrough_set(True)
                        style.set_strikethrough(True)
                if style:
                    scheme.set_style(style_name, style)
            elif child.tagName == "author":
                scheme.author = get_string(child)
            elif child.tagName in ("description", "_description"):
                scheme.description = get_string(child)
            else:
                print "unknown tag:", child.tagName
        return scheme

# SourceContextData
class SourceContextData(gobject.GObject):
    EXTEND_PARENT   = 1 << 0
    END_PARENT      = 1 << 1
    END_AT_LINE_END = 1 << 2
    FIRST_LINE_ONLY = 1 << 3
    ONCE_ONLY       = 1 << 4
    STYLE_INSIDE    = 1 << 5
    
    def __init__(self, lang):
        gobject.GObject.__init__(self)
        self.simple = []

    def set_escape_char(self, escape):
        self.escape = escape

    def define_simple_context(self, id, regex, style):
        self.simple.append((id, (re.compile(regex), style)))

    def get_simple(self):
        return reversed(self.simple)
    
    def define_context(self, id, match_regex, start_regex, end_regex, style, flags):
        pass
    

# SourceContextEngine
class SourceContextEngine(gobject.GObject):
    def __init__(self, ctx_data):
        gobject.GObject.__init__(self)
        self.ctx = ctx_data
        self.highlight = False
        self.buffer = None
        self.highlight_cb_id = None
        self.style_scheme = None
        self.tags = {}
        self.old_text = ""
        # not yet fully supported members
        self.refresh_region = None
        
    def enable_highlight(self, enable):
        if enable == self.highlight:
            return
        self.highlight = enable
        (start, end) = self.buffer.get_bounds()
        if enable:
            self.refresh_range(start, end, True)
        else:
            self.unhighlight_region(start, end)
            self.old_text = ""

    def refresh_range(self, start, end, modify_refresh_region):
        return
##         if start.equal(end):
##             return
##         if modify_refresh_region:
##             self.refresh_region.add(start, end)
##         real_end = end.copy()
##         if real_end.starts_line():
##             real_end.backward_char()
##         self.buffer.emit("highlight_updated", start, real_end)

    def unhighlight_region(self, start, end):
        if start.equal(end):
            return
        for tag in self.tags.values():
            self.buffer.remove_tag(tag, start, end)
        
    def update_highlight(self, start, end, synchronous):
        if not self.highlight:
            return
        start = self.buffer.get_start_iter()
        end = self.buffer.get_end_iter()
        text = self.buffer.get_text(start, end, True)

        # simple caching
        if text == self.old_text:
            return
        self.old_text = text

        applied_tags = []
        self.unhighlight_region(start, end)
        for id, (regex, style) in self.ctx.get_simple():
            tag = self.tags.get(style)
            if not tag:
                continue
            for m in regex.finditer(text):
                start = self.buffer.get_iter_at_offset(m.start())
                end = self.buffer.get_iter_at_offset(m.end())
                for old in applied_tags:
                    self.buffer.remove_tag(old, start, end)
                self.buffer.apply_tag(tag, start, end)
                applied_tags.append(tag)

    def attach_buffer(self, buffer):
        if self.buffer == buffer:
            return
        if self.buffer:
            self.buffer.disconnect(self.highlight_cb_id)
        self.buffer = buffer
        if buffer:
            self.enable_highlight(buffer.get_highlight())
            buffer.connect("notify::highlight", self._highlight_cb)

    def set_style_scheme(self, style_scheme):
        self.style_scheme = style_scheme
        self.tags = {}
        for name, style in self.style_scheme.styles.items():
            self.tags[name] = self.buffer.create_tag(name)
            style.apply(self.tags[name])
            
    def text_inserted(self, start, end):
        pass

    def _highlight_cb(self, buffer, value):
        self.enable_highlight(buffer.get_highlight())
        
# SourceLanguage
class SourceLanguage(gobject.GObject):
    @staticmethod
    def new_from_file(filename, lm):
        try:
            xml = minidom.parse(filename)
        except Exception, e:
            print filename, ':', e
            return None
        
        reader = xml.documentElement
        # process_language_node
        lang = SourceLanguage()
        lang.lang_file_name = filename
        lang.translation_domain = get_attr(reader, "translation-domain")
        lang.hidden = string_to_bool(get_attr(reader, "hidden"))
        tmp = get_attr(reader, "mimetypes")
        if tmp:
            lang.properties["mimetypes"] = tmp
        tmp = get_attr(reader, "globs")
        if tmp:
            lang.properties["globs"] = tmp
        tmp = get_attr(reader, "_name")
        if not tmp:
            tmp = get_attr(reader, "name")
            if not tmp:
                print "Impossible to get language name from file '%s'" % filename
                return None
            lang.name = tmp
            untranslated_name = tmp
        else:
            lang.name = tmp #TODO: translation
            untranslated_name = tmp
        lang.id = get_attr(reader, "id", untranslated_name)
        tmp = get_attr(reader, "_section")
        if not tmp:
            lang.section = get_attr(reader, "section", DEFAULT_SECTION)
        else:
            lang.section = tmp # TODO: translation
        version = get_attr(reader, "version")
        if not version:
            print "Impossible to get version number from file '%s'" % filename
            return None
        if version == "1.0":
            lang.version = GTK_SOURCE_LANGUAGE_VERSION_1_0
        elif version == "2.0":
            lang.version = GTK_SOURCE_LANGUAGE_VERSION_2_0
        else:
            print "Unsupported lang spec version '%s' in filename '%s'" % (version, filename)
            return None

        if lang.version == GTK_SOURCE_LANGUAGE_VERSION_2_0:
            # process_properties
            meta_node = None
            for node in reader.childNodes:
                if node.nodeType == node.ELEMENT_NODE and node.tagName == "metadata":
                    meta_node = node
                    break
            if meta_node:
                for child in meta_node.childNodes:
                    if child.nodeType == child.ELEMENT_NODE and child.tagName == "property":
                        name = get_attr(child, "name")
                        content = "".join([node.data for node in child.childNodes
                                           if node.nodeType == node.TEXT_NODE])
                        if name and content:
                            lang.properties[name] = content
        lang.language_manager = lm #weakref.ref(lm)
        return lang
    
    def __init__(self):
        gobject.GObject.__init__(self)
        self.properties = dict()
        self.ctx_data = None

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_section(self):
        return self.section

    def get_metadata(self, name):
        return self.properties.get(name, None)

    def get_mime_types(self):
        mimetypes = self.get_metadata("mimetypes")
        if mimetypes is None:
            return None
        return mimetypes.split(";")

    def get_globs(self):
        globs = self.get_metadata("globs")
        if globs is None:
            return None
        return globs.split(";")

    def get_language_manager(self):
        return self.language_manager

    styles = {
        u"Base-N Integer": u"def:base-n-integer",
        u"Character"     : u"def:character",
        u"Comment"       : u"def:comment",
        u"Function"      : u"def:function",
        u"Decimal"       : u"def:decimal",
        u"Floating Point": u"def:floating-point",
        u"Keyword"       : u"def:keyword",
        u"Preprocessor"  : u"def:preprocessor",
        u"String"        : u"def:string",
        u"Specials"      : u"def:specials",
        u"Data Type"     : u"def:data-type"
    }

    def create_engine(self):
        if not self.ctx_data:
            success = False
            if self.language_manager:
                ctx_data = SourceContextData(self)
                if self.version == GTK_SOURCE_LANGUAGE_VERSION_1_0:
                    success = self._file_parse_version1(ctx_data)
                elif self.version == GTK_SOURCE_LANGUAGE_VERSION_2_0:
                    success = self._file_parse_version2(ctx_data)
                if success:
                    self.ctx_data = ctx_data
        ce = None
        if self.ctx_data:
            ce = SourceContextEngine(self.ctx_data)
        return ce

    def _parseTag(self, tag, ctx_data):
        def fix_pattern(pattern):
            return pattern.replace('\\n', '\n')

        def add_syntax_pattern(pattern_start, pattern_end, end_at_line_end):
            if end_at_line_end:
                add_simple_pattern(pattern_start + ".*" + pattern_end)
            else:
                add_simple_pattern("(?s)" + pattern_start + ".*" + pattern_end)

        def add_simple_pattern(regex):
            fixed = fix_pattern(regex)
            ctx_data.define_simple_context(name, fixed, self.styles.get(style, style))
        
        def lineComment():
            children = tag.getElementsByTagName("start-regex")
            if len(children) == 1:
                add_simple_pattern(get_string(children[0]) + ".*")
            else:
                print "No start-regex or more than one in line-comment"
                
        def blockComment():
            start_children = tag.getElementsByTagName("start-regex")
            end_children = tag.getElementsByTagName("end-regex")
            if len(start_children) == 1 and len(end_children) == 1:
                add_syntax_pattern(get_string(start_children[0]),
                                   get_string(end_children[0]),
                                   False)
            else:
                print "No start-regex(end-regex) or more than one in block-comment"

        def string():
            end_at_line_end = get_bool(tag, "end-at-line-end", True)
            start_children = tag.getElementsByTagName("start-regex")
            end_children = tag.getElementsByTagName("end-regex")
            if len(start_children) == 1 and len(end_children) == 1:
                add_syntax_pattern(get_string(start_children[0]),
                                   get_string(end_children[0]),
                                   end_at_line_end)
            else:
                print "No start-regex(end-regex) or more than one in block-comment"
            
        def keywordList():
            case_sensitive = get_bool(tag, "case-sensitive", True)
            match_empty_string_at_beggining = get_bool(tag, "match-empty-string-at-beggining", True)
            match_empty_string_at_end = get_bool(tag, "match-empty-string-at-end", True)
            beggining_regex = get_attr(tag, "beggining-regex")
            end_regex = get_attr(tag, "end-regex")
            keywords = []
            for child in tag.getElementsByTagName("keyword"):
                keywords.append(get_string(child))
            # build keyword list
            if not keywords:
                return
            regex = []
            if match_empty_string_at_beggining:
                regex.append("\\b")
            if beggining_regex:
                regex.append(beggining_regex)
            if case_sensitive:
                regex.append("(?:")
            else:
                regex.append("(?i)(?:")
            regex.append("|".join(keywords))
            regex.append(")")
            if end_regex:
                regex.append(end_regex)
            if match_empty_string_at_end:
                regex.append("\\b")
            regex = "".join(regex)
            add_simple_pattern(regex)
            
        def patternItem():
            children = tag.getElementsByTagName("regex")
            if len(children) == 1:
                add_simple_pattern(get_string(children[0]))
            else:
                print "No regex or more than one in pattern-item"
        
        def syntaxItem():
            start_children = tag.getElementsByTagName("start-regex")
            end_children = tag.getElementsByTagName("end-regex")
            if len(start_children) == 1 and len(end_children) == 1:
                add_syntax_pattern(get_string(start_children[0]),
                                   get_string(end_children[0]),
                                   False)
            else:
                print "No start-regex(end-regex) or more than one in syntax-item"
        
        if tag.tagName == "escape-char":
            escape = get_string(tag)
            ctx_data.set_escape_char(escape)
            return
        name = get_attr(tag, "_name")
        if not name:
            name = get_attr(tag, "name")
            id_ = name
        else:
            id_ = name
            name = name #TODO: translation
        if not name:
            return
        style = get_attr(tag, "style")
        d = {
            "line-comment": lineComment,
            "block-comment": blockComment,
            "string" : string,
            "keyword-list": keywordList,
            "pattern-item": patternItem,
            "syntax-item": syntaxItem
        }
        if d.has_key(tag.tagName):
            d[tag.tagName]()
            
    def _file_parse_version1(self, ctx_data):
        try:
            doc = minidom.parse(self.lang_file_name)
        except Exception, e:
            print "Impossible to parse file '%s'" % self.lang_file_name
            return False

        cur = doc.documentElement
        if cur.tagName != "language":
            print "File '%s' is of the wrong type" % self.lang_file_name
            return False
        if not cur.hasAttribute("version"):
            print "Language version missing in file '%s'" % self.lang_file_name
            return False
        else:
            lang_version = cur.getAttribute("version")
            if lang_version != "1.0":
                print "Wrong language version '%s' in file '%s', expected '%s'" % (lang_version, self.lang_version, "1.0")
                return False
        # define_root_context
        ctx_data.define_context(self.id, None, None, None, None,
                                     SourceContextData.EXTEND_PARENT)
        #ctx_data = SourceContextData()
        # XXXXXXXXXXX
        for cur in doc.documentElement.childNodes:
            if cur.nodeType == cur.ELEMENT_NODE:
                self._parseTag(cur, ctx_data)
        return True
    
# SourceLanguagesManager
class SourceLanguagesManager(gobject.GObject):
    __gproperties__ = {
        "search_path" : (gobject.TYPE_OBJECT,
                         _("Language specification directories"),
                         _("List of directories where the "
                           "language specification files (.lang) "
                           "are located"),
                         gobject.PARAM_READWRITE)
        }

    def __init__(self):
        gobject.GObject.__init__(self)
        self.lang_dirs = None
        self.language_ids = {}
        self.available_languages = []

    def get_property(self, property):
        if property.name == "search-path":
            return self.get_search_path()
        raise AttributeError, 'unknown property %s' % property.name
        
    def set_property(self, property, value):
        if property.name == "search-path":
            self.set_search_path(value)
        raise AttributeError, 'unknown property %s' % property.name

    def get_search_path(self):
        if not self.lang_dirs:
            return Path.languages_dir
        return self.lang_dirs

    def set_search_path(self, dirs):
        self.lang_dirs = dirs
        self.notify("search-path")

    def get_avaliable_languages(self):
        self._ensure_languages()
        return self.available_languages

    def get_language_by_id(self, id):
        self._ensure_languages()
        return self.language_ids[id]

    def get_rng_file(self):
        # TODO
        pass

    def _ensure_languages(self):
        if self.language_ids:
            return
        filename = get_file_list(self.get_search_path(), LANG_FILE_SUFFIX)
        for l in filename:
            lang = SourceLanguage.new_from_file(l, self)
            if lang and not self.language_ids.has_key(lang.id):
                self.language_ids[lang.id] = lang
        self.available_languages = self.language_ids.values()

# SourceUndoManager
class SourceUndoAction(object):
    spaces = ' \t'
    def __init__(self, mergeable, modified, order_in_group = -1):
        self.order_in_group = order_in_group
        self.mergeable = mergeable
        self.modified = modified

    def set_order_in_group(self, order_in_group):
        self.order_in_group = order_in_group

    def get_order_in_group(self):
        self.order_in_group

    def delete_text(self, buffer, start, end):
        start_iter = buffer.get_iter_at_offset(start)
        if end < 0:
            end_iter = buffer.get_end_iter()
        else:
            end_iter = buffer.get_iter_at_offset(end)
        buffer.delete(start_iter, end_iter)

    def insert_text(self, buffer, pos, text):
        it = buffer.get_iter_at_offset(pos)
        buffer.insert(it, text)
        
    def set_cursor(self, buffer, cursor):
        it = buffer.get_iter_at_offset(cursor)
        buffer.place_cursor(it)

class SourceInvalidAction(SourceUndoAction):
    pass

class SourceUndoInsertAction(SourceUndoAction):
    def __init__(self, pos, text):
        SourceUndoAction.__init__(self, len(text) == 1 and text != '\n', False)
        self.pos = pos
        self.text = text

    def undo(self, document):
        self.delete_text(document, self.pos, self.pos + len(self.text))
        self.set_cursor(document, self.pos)

    def redo(self, document):
        self.set_cursor(document, self.pos)
        self.insert_text(document, self.pos, self.text)
    
    def merge(self, undo_action):
        if undo_action.pos != self.pos + len(self.text) or \
           (not undo_action.text[0] in self.spaces and
            self.text[-1] in self.spaces):
            self.mergeable = False
            return False
        self.text = self.text + undo_action.text
        return True

    def __repr__(self):
        return "I%d" % self.order_in_group + self.text

class SourceUndoDeleteAction(SourceUndoAction):
    def __init__(self, start, text, forward):
        SourceUndoAction.__init__(self, len(text) == 1 and text != '\n', False)
        self.start = start
        self.text = text
        self.forward = forward

    def undo(self, document):
        self.insert_text(document, self.start, self.text)
        if self.forward:
            self.set_cursor(document, self.start)
        else:
            self.set_cursor(document, self.start + len(self.text))

    def redo(self, document):
        self.delete_text(document, self.start, self.start + len(self.text))
        self.set_cursor(document, self.start)
    
    def merge(self, undo_action):
        if self.forward != undo_action.forward or \
           (self.start != undo_action.start and
            self.start != undo_action.start + len(undo_action.text)):
            self.mergeable = False
            return False
        if self.start == undo_action.start:
            if not undo_action.text[0] in self.spaces and \
               self.text[-1] in self.spaces:
                self.mergeable = False
                return False
            self.text = self.text + undo_action.text
        else:
            if not undo_action.text[0] in self.spaces and \
               self.text[0] in self.spaces:
                self.mergeable = False
                return False
            self.text = undo_action.text + self.text
            self.start = undo_action.start
        return True

    def __repr__(self):
        return "D%d" % self.order_in_group + self.text

class SourceUndoManager(gobject.GObject):
    __gsignals__ = {
        'can_undo' : (gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,
                      (bool,)),
        'can_redo' : (gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,
                      (bool,))
    }

    def __init__(self, buffer):
        gobject.GObject.__init__(self)
        self.document = buffer
        self.actions = []
        self.next_redo = 0
        self.can_undo = False
        self.can_redo = False
        self.actions_in_current_group = 0
        self.running_not_undoable_actions = 0
        self.num_of_groups = 0
        self.max_undo_levels = DEFAULT_MAX_UNDO_LEVELS
        self.modified_action = None
        self.modified_undoing_group = False
        buffer.connect("insert_text", self._insert_text_handler)
        buffer.connect("delete_range", self._delete_range_handler)
        buffer.connect("begin_user_action", self._begin_user_action_handler)
        buffer.connect("modified_changed", self._modified_changed_handler)

    def __repr__(self):
        return str(tuple([self.actions,
                         self.actions_in_current_group,
                         self.num_of_groups,
                         self.next_redo]))

    def _get_action(self, i):
        if i < 0 or i >= len(self.actions):
            return None
        return self.actions[i]
    
    #def can_undo(self):
    #    return self.can_undo

    #def can_redo(self):
    #    return self.can_redo

    def undo(self):
        modified = False
        self.modified_undoing_group = False
        self.begin_not_undoable_action()
        while True:
            undo_action = self._get_action(self.next_redo + 1)
            if not undo_action:
                return
            if not (undo_action.order_in_group <= 1 or
                    (undo_action.order_in_group > 1 and
                     not undo_action.modified)):
                return
            if undo_action.order_in_group <= 1:
                modified = undo_action.modified and not self.modified_undoing_group
            undo_action.undo(self.document)
            self.next_redo += 1
            if not undo_action.order_in_group > 1:
                break
        if modified:
            self.next_redo -= 1
            self.document.set_modified(False)
            self.next_redo += 1
        self._end_not_undoable_action_internal()
        self.modified_undoing_group = False
        if not self.can_redo:
            self.can_redo = True
            self.emit("can-redo", True)
        if self.next_redo >= len(self.actions) - 1:
            self.can_undo = False
            self.emit("can-undo", False)
        #print "undo:", self

    def redo(self):
        modified = False
        undo_action = self._get_action(self.next_redo)
        if not undo_action:
            return
        self.begin_not_undoable_action()
        while True:
            if undo_action.modified:
                if not undo_action.order_in_group <= 1:
                    return
                modified = True
            self.next_redo -= 1
            undo_action.redo(self.document)
            if self.next_redo < 0:
                undo_action = None
            else:
                undo_action = self._get_action(self.next_redo)
            if not undo_action or not undo_action.order_in_group > 1:
                break
        if modified:
            self.next_redo += 1
            self.document.set_modified(False)
            self.next_redo -= 1
        self._end_not_undoable_action_internal()
        if self.next_redo < 0:
            self.can_redo = False
            self.emit("can-redo", False)
        if not self.can_undo:
            self.can_undo = True
            self.emit("can-undo", True)
        #print "redo:", self

    def begin_not_undoable_action(self):
        self.running_not_undoable_actions += 1

    def end_not_undoable_action(self):
        self._end_not_undoable_action_internal()
        if self.running_not_undoable_actions == 0:
            self.actions = []
            self.next_redo = -1
            if self.can_undo:
                self.can_undo = False
                self.emin("can-undo", False)
            if self.can_redo:
                self.can_redo = False
                self.emit("can-redo", False)

    def get_max_undo_levels(self):
        return self.max_undo_levels

    def set_max_undo_levels(self, undo_levels):
        old_levels = self.max_undo_levels
        self.max_undo_levels = max_undo_levels
        if max_undo_levels < 1:
            return
        if old_levels > max_undo_levels:
            while self.next_redo >= 0 and self.num_of_groups > max_undo_levels:
                self._free_first_n_actions(1)
                self.next_redo -= 1
            self._check_list_size()
            if self.next_redo < 0 and self.can_redo:
                self.can_redo = False
                self.emit("can-redo", False)
            if self.can_undo and self.next_redo >= len(self.actions) - 1:
                self.can_undo = False
                self.emit("can-undo", False)
            

    def _add_action(self, undo_action):
        if self.next_redo >= 0:
            #print "YEP"
            self._free_first_n_actions(self.next_redo + 1)
        self.next_redo = -1
        if not self._merge_action(undo_action):
            self.actions_in_current_group += 1
            undo_action.set_order_in_group(self.actions_in_current_group)
            if undo_action.get_order_in_group() == 1:
                self.num_of_groups += 1
            self.actions.insert(0, undo_action)
        self._check_list_size()
        if not self.can_undo:
            self.can_undo = True
            self.emit("can-undo", True)
        if not self.can_redo:
            self.can_redo = False
            self.emit("can-redo", False)
        #print "add_action:", self

    def _free_first_n_actions(self, n):
        if not self.actions:
            return
        for i in range(n):
            action = self.actions[0]
            if action.order_in_group == 1:
                self.num_of_groups -= 1
            if action.modified:
                self.modified_action = SourceInvalidAction
            del self.actions[0] # TODO: think about optimization
            if not self.actions:
                return

    def _check_list_size(self):
        undo_levels = self.get_max_undo_levels()
        if undo_levels < 1:
            return
        if self.num_of_groups > undo_levels:
            undo_action = self.actions[len(self.actions)-1]
            while True:
                if undo_action.order_in_group == 1:
                    self.num_of_groups -= 1
                if undo_action.modified:
                    self.modified_action = SourceInvalidAction
                self.actions.pop()
                if not self.actions:
                    return
                undo_action = self.actions[len(self.actions) - 1]
                if not (undo_action.order_in_group > 1 or
                        self.num_of_groups > undo_levels):
                    break

    def _merge_action(self, undo_action):
        if not self.actions:
            return False
        last_action = self.actions[0]
        if not last_action.mergeable:
            return False
        if not undo_action.mergeable or type(undo_action) != type(last_action):
            last_action.mergeable = False
            return False
        return last_action.merge(undo_action)
    
    def _insert_text_handler(self, buffer, pos, text, length):
        if self.running_not_undoable_actions > 0:
            return
        undo_action = SourceUndoInsertAction(pos.get_offset(), text)
        self._add_action(undo_action)
        
    def _delete_range_handler(self, buffer, start, end):
        if self.running_not_undoable_actions > 0:
            return
        start.order(end)
        text = buffer.get_slice(start, end, True)
        insert_iter = buffer.get_iter_at_mark(buffer.get_insert())
        forward = insert_iter.get_offset() <= start.get_offset()
        undo_action = SourceUndoDeleteAction(start.get_offset(), text, forward)
        self._add_action(undo_action)

    def _begin_user_action_handler(self, buffer):
        if self.running_not_undoable_actions > 0:
            return
        self.actions_in_current_group = 0

    def _modified_changed_handler(self, buffer):
        if not self.actions:
            return
        idx = self.next_redo + 1
        action = self._get_action(idx)
        if not buffer.get_modified():
            if action:
                action.mergeable = False
                if self.modified_action:
                    if self.modified_action != SourceInvalidAction:
                        self.modified_action.modified = False
                    self.modified_action = None
            return
        if not action:
            return
        if self.modified_action:
            #print "Ooops"
            return
        if action.order_in_group > 1:
            self.modified_undoing_group = True
        while action.order_in_group > 1:
            idx += 1
            action = self._get_action(idx)
            if not action:
                return
        action.modified = True
        self.modified_action = action

    def _end_not_undoable_action_internal(self):
        if self.running_not_undoable_actions > 0:
            self.running_not_undoable_actions -= 1

# SourceBuffer
class SourceBuffer(TextBuffer):
    __gproperties__ = {
        "style_scheme" : (gobject.TYPE_OBJECT,
                          _("Style Scheme"),
                          _("Style Scheme used for syntax coloring"),
                          gobject.PARAM_READWRITE),
        
        "check_brackets" : (gobject.TYPE_BOOLEAN,
                            _("Check Brackets"),
                            _("Whether to check and highlight matching brackets"),
                            True,
                            gobject.PARAM_READWRITE),
        
        "highlight" : (gobject.TYPE_BOOLEAN,
                       _("Highlight"),
                       _("Whether to highlight syntax in the buffer"),
                       True,
                       gobject.PARAM_READWRITE),

        "max_undo_levels" : (gobject.TYPE_UINT,
                             _("Maximum Undo LEvels"),
                             _("Number of undo levels for the buffer"),
                             0,
                             200,
                             25,
                             gobject.PARAM_READWRITE),

        "language" : (gobject.TYPE_OBJECT,
                      _("Language"),
                      _("Language obejct to get highlighting patterns from"),
                      gobject.PARAM_READWRITE),

        "can-undo" : (gobject.TYPE_BOOLEAN,
                      _("Can undo"),
                      _("Whether Undo operation is possible"),
                      False,
                      gobject.PARAM_READWRITE),

        "can-redo" : (gobject.TYPE_BOOLEAN,
                      _("Can redo"),
                      _("Whether Redo operation is possible"),
                      False,
                      gobject.PARAM_READWRITE)
    }

    __gsignals__ = {
        'highlight_updated' : (gobject.SIGNAL_RUN_LAST,
                               gobject.TYPE_NONE,
                               (TextIter, TextIter)),
        'marker_updated' : (gobject.SIGNAL_RUN_LAST,
                            gobject.TYPE_NONE,
                            (TextIter,)),
        'can_undo' : (gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,
                      (bool,)),
        'can_redo' : (gobject.SIGNAL_RUN_LAST,
                      gobject.TYPE_NONE,
                      (bool,))
    }

    def __init__(self, text="", table=None):
        TextBuffer.__init__(self, table)

        self.check_brackets = True
        self.bracket_mark = None
        self.bracket_found = False
        self.bracket_match_tag = None
        self.markers = []
        self.highlight = False
        self.highlight_engine = None
        self.language = None
        self.style_scheme = SourceStyleScheme.get_default()
        self.set_text(text)
        self.undo_manager = SourceUndoManager(self)
        self.connect("mark_set", self.move_cursor)
        self.undo_manager.connect("can_undo", self.can_undo_handler)
        self.undo_manager.connect("can_redo", self.can_redo_hadler)
        

    def set_style_scheme(self, scheme):
        if self.style_scheme == scheme:
            return
        self.style_scheme = scheme
        self._update_bracket_match_style()
        if self.highlight_engine:
            self.highlight_engine.set_style_scheme(scheme)
        self.notify("style_scheme")

    def get_style_scheme(self):
        return self.style_scheme
    
    def set_check_brackets(self, check_brackets):
        if check_brackets != self.check_brackets:
            self.check_brackets = check_brackets
            self.notify("check_brackets")

    def get_check_brackets(self):
        return self.check_brackets

    def set_highlight(self, highlight):
        if highlight != self.highlight:
            self.highlight = highlight
            self.notify("highlight")

    def get_highlight(self):
        return self.highlight

    def set_max_undo_levels(self, max_undo_levels):
        if self.undo_manager.get_max_undo_levels() != max_undo_levels:
            self.undo_manager.set_max_undo_levels(max_undo_levels)
            self.notify("max_undo_levels")

    def get_max_undo_levels(self):
        return self.undo_manager.get_max_undo_levels()

    def set_language(self, language):
        if self.language == language:
            return
        if self.highlight_engine:
            self.highlight_engine.attach_buffer(None)
            self.highlight_engine = None
        self.language = language
        if language:
            self.highlight_engine = language.create_engine()
            if self.highlight_engine:
                self.highlight_engine.attach_buffer(self)
                if self.style_scheme:
                    self.highlight_engine.set_style_scheme(self.style_scheme)

    def get_language(self):
        return self.language

    def can_undo(self):
        return self.undo_manager.can_undo

    def can_redo(self):
        return self.undo_manager.can_redo

    def undo(self):
        self.undo_manager.undo()

    def redo(self):
        self.undo_manager.redo()
        
    _property_map = {
        'check-brackets': (set_check_brackets, get_check_brackets),
        'highlight' : (set_highlight, get_highlight),
        'max-undo-levels' : (set_max_undo_levels, get_max_undo_levels),
        'language' : (set_language, get_language),
        'can-undo' : (None, can_undo),
        'can-redo' : (None, can_redo),
        'style-scheme' : (set_style_scheme, get_style_scheme)
    }
    
    def get_property(self, property):
        if property.name in self._property_map:
            f = self._property_map[property.name][1]
            if f:
                return f()
        raise AttributeError, 'unknown property %s' % property.name
        
    def set_property(self, property, value):
        if property.name in self._property_map:
            f = self._property_map[property.name][0]
            if f:
                return f(value)
        raise AttributeError, 'unknown property %s' % property.name

    # methods
    def update_highlight(self, start, end, synchronous):
        if self.highlight_engine:
            self.highlight_engine.update_highlight(start, end, synchronous)

    # handlers
    def do_insert_text(self, it, text, len):
        start_offset = it.get_offset()
        TextBuffer.do_insert_text(self, it, text, len)
        self.move_cursor(self, it, self.get_insert())
        end_offset = it.get_offset()
        if self.highlight_engine:
            self.highlight_engine.text_inserted(start_offset, end_offset)

    def do_delete_range(self, start, end):
        TextBuffer.do_delete_range(self, start, end)
        mark = self.get_insert()
        it = self.get_iter_at_mark(mark)
        self.move_cursor(self, it, mark)
        
    def move_cursor(self, buffer, it, mark):
        if mark != self.get_insert():
            return
        if self.bracket_found:
            it1 = self.get_iter_at_mark(self.bracket_mark)
            it2 = it1.copy()
            it2.forward_char()
            self.remove_tag(self._get_bracket_match_tag(), it1, it2)

        if not self.check_brackets:
            return

        it1 = it.copy()
        res, it1 = self._find_bracket_match_with_limit(it1, MAX_CHARS_BEFORE_FINDING_A_MATCH)
        if res:
            if not self.bracket_mark:
                self.bracket_mark = self.create_mark(None, it1, False)
            else:
                self.move_mark(self.bracket_mark, it1)
            it2 = it1.copy()
            it2.forward_char()
            self.apply_tag(self._get_bracket_match_tag(), it1, it2)
            self.bracket_found = True
        else:
            self.bracket_found = False

    def _find_bracket_match_real(self, orig, max_chars):
        it = orig.copy()
        cur_char = it.get_char()
        base_char = cur_char
        left = '{([<'
        right= '})]>'
        if base_char in left:
            addition = 1
            search_char = right[left.find(base_char)]
        elif base_char in right:
            addition = -1
            search_char = left[right.find(base_char)]
        else:
            return (False, orig)
        counter = 0
        found = False
        char_cont = 0
        while True:
            it.forward_chars(addition)
            cur_char = it.get_char()
            char_cont += 1
            if cur_char == search_char or cur_char == base_char:
                if cur_char == search_char and counter == 0:
                    found = True
                    break
                if cur_char == base_char:
                    counter += 1
                else:
                    counter -= 1
            #print char_cont, cur_char, search_char, counter
            if it.is_end() or it.is_start() or (char_cont >= max_chars and max_chars >= 0):
                break
        if found:
            orig = it.copy()
        return (found, orig)

    def _find_bracket_match_with_limit(self, orig, max_chars):
        res, orig = self._find_bracket_match_real(orig, max_chars)
        if res:
            return (True, orig)

        it = orig.copy()
        if not it.starts_line() and it.backward_char():
            res, it = self._find_bracket_match_real(it, max_chars)
            if res:
                orig = it
                return (True, orig)
        return (False, orig)

    def _get_bracket_match_tag(self):
        if not self.bracket_match_tag:
            tag = self.create_tag(None)
            self.bracket_match_tag = tag
            tag.set_property("weight", pango.WEIGHT_HEAVY)
            self._update_bracket_match_style()
        return self.bracket_match_tag

    def _update_bracket_match_style(self):
        if self.bracket_match_tag:
            style = SourceStyle()
            if self.style_scheme:
                style = self.style_scheme.get_matching_brackets_style()
            style.apply(self.bracket_match_tag)

    def can_undo_handler(self, um, can_undo):
        self.notify("can-undo")
        self.emit("can-undo", can_undo)

    def can_redo_hadler(self, um, can_redo):
        self.notify("can-redo")
        self.emit("can-redo", can_redo)
        
    
# SourceView
class SourceView(TextView):
    __gproperties__ = {
        "show_line_numbers" : (gobject.TYPE_BOOLEAN,
                               _("Show Line Numbers"),
                               _("Whether to display line numbers"),
                               False,
                               gobject.PARAM_READWRITE),
        
        "show_line_markers" : (gobject.TYPE_BOOLEAN,
                               _("Show Line Markers"),
                               _("Whether to display line marker pixbufs"),
                               False,
                               gobject.PARAM_READWRITE),

        "tabs_width" : (gobject.TYPE_UINT,
                        _("Tabs Width"),
                        _("Tabs Width"),
                        1,
                        MAX_TAB_WIDTH,
                        DEFAULT_TAB_WIDTH,
                        gobject.PARAM_READWRITE),
        
        "auto_indent" : (gobject.TYPE_BOOLEAN,
                         _("Auto Indentation"),
                         _("Whether to enable auto indentation"),
                         False,
                         gobject.PARAM_READWRITE),

        "insert_spaces_instead_of_tabs": (gobject.TYPE_BOOLEAN,
                                          _("Insert Spaces Instead of Tabs"),
                                          _("Whether to insert spaces instead of tabs"),
                                          False,
                                          gobject.PARAM_READWRITE),

        "show_margin" : (gobject.TYPE_BOOLEAN,
                         _("Show Right Margin"),
                         _("Whether to display the right margin"),
                         False,
                         gobject.PARAM_READWRITE),

        "margin" : (gobject.TYPE_UINT,
                    _("Margin position"),
                    _("Position of the right margin"),
                    1,
                    MAX_MARGIN,
                    DEFAULT_MARGIN,
                    gobject.PARAM_READWRITE),

        "smart_home_end" : (gobject.TYPE_BOOLEAN,
                            _("Smart Home/End"),
                            _("HOME and END keys move to first/last "
                              "non whitespace chapters on line before going "
                              "to the start/end of the line"),
                            False,
                            gobject.PARAM_READWRITE),

        "highlight_current_line" : (gobject.TYPE_BOOLEAN,
                                    _("Highlight current line"),
                                    _("Whether to highlight the current line"),
                                    False,
                                    gobject.PARAM_READWRITE),

        "indent_on_tab" : (gobject.TYPE_BOOLEAN,
                           _("Indent on tab"),
                           _("Whether to indent the selected text when the tab key is pressed"),
                           True,
                           gobject.PARAM_READWRITE)
    }

    
    def __init__(self, buffer=None):
        TextView.__init__(self, buffer)
        
        self.tabs_width = DEFAULT_TAB_WIDTH
        self.margin = DEFAULT_MARGIN;
        self.cached_margin_width = -1
        self.indent_on_tab = True
        self.smart_home_end = False
        self.set_left_margin(2)
        self.set_right_margin(2)

        # create members
        self.show_line_numbers = False
        self.show_line_markers = False
        self.auto_indent = False
        self.insert_spaces = False
        self.show_margin = False
        self.highlight_current_line = False
        self.source_buffer = None
        self.source_buffer_handler_id = []
        self.old_lines = 0 # number of lines
        self.current_line_gc = None

        # TODO: not yet implemented
        #self.pixmap_cache = dict()
        self.style_scheme_applied = False 
        self.style_scheme = None

        self._set_source_buffer(self.get_buffer())

        # DnD init
        #tl = self.drag_dest_get_target_list()
        #if tl:
        #    tl.append(("application/x-color", 0, TARGET_COLOR))
        #    self.connect("drag_data_received", self.view_dnd_drop)
        #    self.connect("notify::buffer", self.notify_buffer0
        
    def set_show_line_numbers(self, show):
        if show and not self.show_line_numbers:
            if not self.show_line_markers:
                self.set_border_window_size(gtk.TEXT_WINDOW_LEFT, MIN_NUMBER_WINDOW_WIDTH)
            else:
                self.queue_draw()
            self.show_line_numbers = show
            self.notify("show_line_numbers")
        if not show and self.show_line_numbers:
            self.queue_draw()
            self.show_line_numbers = show
            self.notify("show_line_numbers")

    def get_show_line_numbers(self):
        return self.show_line_numbers

    def set_show_line_markers(self, show):
        if show and not self.show_line_markers:
            if not self.show_line_numbers:
                self.set_border_window_size(gtk.TEXT_WINDOW_LEFT, MIN_NUMBER_WINDOW_WIDTH)
            else:
                self.queue_draw()
            self.show_line_markers = show
            self.notify("show_line_markers")
        if not show and self.show_line_markers:
            self.queue_draw()
            self.show_line_markers = show
            self.notify("show_line_markers")

    def get_show_line_markers(self):
        return self.show_line_markers

    def set_tabs_width(self, width):
        if width <= 0 or width > MAX_TAB_WIDTH or self.tabs_width == width:
            return
        save_width = self.tabs_width
        self.tabs_width = width
        if self._set_tab_stops_internal():
            self.notify("tabs_width")
        else:
            self.tabs_width = save_width

    def get_tabs_width(self):
        return self.tabs_width

    def set_auto_indent(self, enable):
        if self.auto_indent != enable:
            self.auto_indent = enable
            self.notify("auto_indent")
            
    def get_auto_indent(self):
        return self.auto_indent

    def set_insert_spaces_instead_of_tabs(self, enable):
        if self.insert_spaces != enable:
            self.insert_spaces = enable
            self.notify("insert_spaces_instead_of_tabs")

    def get_insert_spaces_instead_of_tabs(self):
        return self.insert_spaces

    def set_show_margin(self, show):
        if self.show_margin != show:
            self.show_margin = show
            self.queue_draw()
            self.notify("show_margin")

    def get_show_margin(self):
        return self.show_margin

    def set_margin(self, margin):
        if margin < 1 or margin > MAX_MARGIN or self.margin == margin:
            return
        self.margin = margin
        self.cached_margin_width = -1
        self.queue_draw()
        self.notify("margin")

    def get_margin(self):
        return self.margin

    def set_smart_home_end(self, enable):
        if not self.smart_home_end == enable:
            self.smart_home_end = enable
            self.notify("smart_home_end")

    def get_smart_home_end(self):
        return self.smart_home_end

    def set_highlight_current_line(self, enable):
        if not self.highlight_current_line == enable:
            self.highlight_current_line = enable
            self.queue_draw()
            self.notify("highlight_current_line")
    
    def get_highlight_current_line(self):
        return self.highlight_current_line

    _property_map = {
        'show-line-numbers': (set_show_line_numbers, get_show_line_numbers),
        'show-line-marker': (set_show_line_markers, get_show_line_markers),
        'tabs-width': (set_tabs_width, get_tabs_width),
        'auto-indent': (set_auto_indent, get_auto_indent),
        'insert-spaces-instead-of-tabs': (set_insert_spaces_instead_of_tabs, get_insert_spaces_instead_of_tabs),
        'show-margin': (set_show_margin, get_show_margin),
        'margin': (set_margin, get_margin),
        'smart-home-end': (set_smart_home_end, get_smart_home_end),
        'highlight-current-line': (set_highlight_current_line, get_highlight_current_line)
        }
    
    def get_property(self, property):
        if property.name in self._property_map:
            f = self._property_map[property.name][1]
            if f:
                return f()
        raise AttributeError, 'unknown property %s' % property.name
        
    def set_property(self, property, value):
        if property.name in self._property_map:
            f = self._property_map[property.name][0]
            if f:
                return f(value)
        raise AttributeError, 'unknown property %s' % property.name
        
    # aux
    def _set_tab_stops_internal(self):
        real_tab_width = self._calculate_real_tab_width(self.tabs_width, ' ')
        if real_tab_width < 0:
            return False
        tab_array = pango.TabArray(1, True)
        tab_array.set_tab(0, pango.TAB_LEFT, real_tab_width)
        self.set_tabs(tab_array)
        return True

    def _calculate_real_tab_width(self, tab_size, c):
        if tab_size == 0:
            return -1
        tab_string = c * tab_size
        layout = self.create_pango_layout(tab_string)
        if layout:
            return layout.get_pixel_size()[0]
        return -1

    def _set_source_buffer(self, buffer):
        if self.source_buffer == buffer:
            return
        if self.source_buffer:
            for handler_id in self.source_buffer_handler_id:
                self.source_buffer.disconnect(handler_id)
        if buffer and type(buffer) == SourceBuffer:
            self.source_buffer = buffer
            self.source_buffer_handler_id = [
                buffer.connect("highlight_updated", self._highlight_updated_cb),
                buffer.connect("marker-updated", self._marker_updated_cb),
                buffer.connect("notify::style_scheme", self._buffer_style_scheme_changed_cb),
            ]
        else:
            self.source_buffer = None
            self.source_buffer_handler_id = []

        if buffer:
            self._update_style_scheme()

    def _highlight_updated_cb(self, buffer, start, end):
        visible_rect = self.get_visible_rect()
        (y, height) = self.get_line_yrange(start)
        updated_rect.y = y
        (y, height) = self.get_line_yrange(end)
        updated_rect.height = y + height - updated_rect.y
        updated_rect.x = visible_rect.x
        updated_rect.width = visible_rect.width

        redraw_rect = updated_rect.intersect(visible_rect)
        if not tuple(redraw_rect) == (0, 0, 0, 0):
            (x, y) = self.buffer_to_window_coord(gtk.TEXT_WINDOW_WIDGET, redraw_rect.x, redraw_rect.y)
            widget_rect = gdk.Rectangle(0, 0, redraw_rect.width, redraw_rect.height)
            self.query_draw_area(widget_rect.x, widget_rect.y, widget_rect.width, widget_rect.height)

    def _marker_updated_cb(self, buffer, where):
        if not self.show_line_markers:
            return
        visible_rect = self.get_visible_rect()
        (y, height) = self.get_line_yrange(where)
        updated_rect = gdk.Rectangle(visible_rect.x, y, visible_rect.width, height)
        redraw_rect = updated_rect.intersect(visible_rect)
        if not tuple(redraw_rect) == (0, 0, 0, 0):
            y_win = self.buffer_to_window_coord(gtk.TEXT_WINDOW_WIDGET, 0, redraw_rect.y)[1]
            width = self.get_border_window_size(gtk.TEXT_WINDOW_LEFT)
            self.query_draw_area(0, y_win, width, height)
        
    def _buffer_style_scheme_changed_cb(self, buffer, pspec):
        self._update_style_scheme()

    def _update_style_scheme(self):
        buffer = self.get_buffer()
        if type(buffer) == SourceBuffer:
            new_scheme = buffer.get_style_scheme()
        else:
            new_scheme = None
        if self.style_scheme != new_scheme:
            self.style_scheme = new_scheme
            # HACK: WIDGET_REALIZED
            if 'GTK_REALIZED' in self.flags().value_names:
                new_scheme.apply(self)
                color = new_scheme.get_current_line_color()
                if color:
                    self.current_line_gc = gdk.GC(self.get_window(gtk.TEXT_WINDOW_WIDGET), color)
                self.style_scheme_applied = True
            else:
                self.style_scheme_applied = False

    def do_style_set(self, previous_style):
        if previous_style:
            TextView.do_style_set(self, previous_style)
            self._set_tab_stops_internal()
            self.cached_margin_width = -1
            
    def do_realize(self):
        TextView.do_realize(self)
        if self.style_scheme and not self.style_scheme_applied:
            self.style_scheme.apply(self)
            self.style_scheme_applied = True
            color = self.style_scheme.get_current_line_color()
            if color:
                self.current_line_gc = gdk.GC(self.get_window(gtk.TEXT_WINDOW_WIDGET), color)
            
    def do_key_press_event(self, event):
        buf = self.get_buffer()
        modifiers = gtk.accelerator_get_default_mod_mask()
        key = event.keyval
        mark = buf.get_insert()
        cur = buf.get_iter_at_mark(mark)
        key_mask = [gdk.keyval_from_name(name) for name in ['Enter', 'Return']] 
        if key in key_mask and \
           not event.state & gdk.SHIFT_MASK and \
           self.auto_indent:
            indent = self._compute_indentation(cur)
            if indent:
                # TODO: find im_context
                #if self.im_context.filter_keypress(event):
                #    return True
                cur = buf.get_iter_at_mark(mark)
                buf.begin_user_action()
                buf.insert(cur, "\n")
                buf.insert(cur, indent)
                buf.end_user_action()
                self.scroll_mark_onscreen(mark)
                return True

        key_mask = [gdk.keyval_from_name(name)
                    for name in ['Tab', 'KP_Tab', 'ISO_Left_Tab']]
        if key in key_mask and \
           (event.state & modifiers) in (0, gdk.SHIFT_MASK):
            selection = buf.get_selection_bounds()
            has_section = bool(selection)
            if not selection:
                it = buf.get_iter_at_mark(buf.get_insert())
                selection = (it, it.copy())
                
            if self.indent_on_tab:
                if event.state & gdk.SHIFT_MASK:
                    self.unindent_lines(selection)
                    return True

                if has_section and \
                    ((selection[0].starts_line() and selection[1].ends_line()) or \
                    (selection[0].get_line() != selection[1].get_line())):
                    self.indent_lines(selection)
                    return True
            self._insert_tab_or_spaces(selection)
            return True
        return TextView.do_key_press_event(self, event)

    def unindent_lines(self, selection = None):
        buf = self.get_buffer()
        if not selection:
            selection = buf.get_selection_bounds()
        if selection:
            (start, end) = selection
        else:
            start = buf.get_iter_at_mark(buf.get_insert())
            end = start.copy()
            
        start_line = start.get_line()
        end_line = end.get_line()

        if end.get_visible_line_offset() == 0 and end_line > start_line:
            end_line -= 1

        buf.begin_user_action()
        for i in range(start_line, end_line + 1):
            it = buf.get_iter_at_line(i)
            if it.get_char == '\t':
                it2 = it.copy()
                it2.forward_char()
                buf.delete(it, it2)
            elif it.get_char() == ' ':
                spaces = 0
                it2 = it.copy()
                while not it2.ends_line():
                    if it2.get_char() == ' ':
                        spaces += 1
                    else:
                        break
                    it2.forward_char()
                if spaces > 0:
                    spaces = spaces % self.tabs_width
                    if spaces == 0:
                        spaces = self.tabs_width
                    it2 = it.copy()
                    it2.forward_chars(spaces)
                    buf.delete(it, it2)
        buf.end_user_action()
        self.scroll_mark_onscreen(buf.get_insert())


    def _compute_indentation(self, cur):
        line = cur.get_line()
        buf = self.get_buffer()
        start = buf.get_iter_at_line(line)
        end = start.copy()
        ch = end.get_char()

        while ch.isspace() and not ch in ('\n', '\r') and end.compare(cur) < 0:
            if not end.forward_char():
                break
            ch = end.get_char()

        if start.equal(end):
            return None

        res = start.get_slice(end)
        return res

    def indent_lines(self, selection = None):
        buf = self.get_buffer()
        if not selection:
            selection = buf.get_selection_bounds()
        if selection:
            (start, end) = selection
        else:
            start = buf.get_iter_at_mark(buf.get_insert())
            end = start.copy()

        start_line = start.get_line()
        end_line = end.get_line()

        if end.get_visible_line_offset() == 0 and end_line > start_line:
            end_line -= 1

        if self.get_insert_spaces_instead_of_tabs():
            tabs_size = self.tabs_width
            tab_buffer = ' ' * tabs_size
        else:
            tab_buffer = "\t"

        buf.begin_user_action()
        for i in xrange(start_line, end_line + 1):
            cur = buf.get_iter_at_line(i)
            if cur.ends_line():
                continue
            buf.insert(cur, tab_buffer, -1)
        buf.end_user_action()

        self.scroll_mark_onscreen(buf.get_insert())
        
    def _insert_tab_or_spaces(self, (start, end)):
        if self.insert_spaces:
            tabs_size = self.tabs_width
            it = start.copy()
            cur_pos = it.get_line_offset()
            tab_pos = cur_pos
            while tab_pos > 0:
                it.backward_char()
                if it.get_char() == '\t':
                    break
                tab_pos -= 1
            num_of_equivalent_spaces = tabs_size - (cur_pos - tab_pos) % tabs_size
            tab_buf = ' ' * num_of_equivalent_spaces
        else:
            tab_buf = '\t'

        buf = self.get_buffer()
        buf.begin_user_action()
        buf.delete(start, end)
        buf.insert(start, tab_buf)
        buf.end_user_action()

    def do_move_cursor(self, step, count, extend_selection):
        buffer = self.get_buffer()
        mark = buffer.get_insert()
        cur = buffer.get_iter_at_mark(mark)
        it = cur.copy()

        if self.smart_home_end and step == gtk.MOVEMENT_DISPLAY_LINE_ENDS and count == -1:
            #move_to_first_char
            it.set_line_offset(0)
            while not it.ends_line():
                if it.get_char().isspace():
                    it.forward_char()
                else:
                    break
            self._do_cursor_move(cur, it, extend_selection)
            return
        elif self.smart_home_end and step == gtk.MOVEMENT_DISPLAY_LINE_ENDS and count == 1:
            #move_to_last_char
            if not it.ends_line():
                it.forward_to_line_end()
            while not it.starts_line():
                it.backward_char()
                if not it.get_char().isspace():
                    it.forward_char()
                    break
            self._do_cursor_move(cur, it, extend_selection)
            return
        TextView.do_move_cursor(self, step, count, extend_selection)
                
    def _do_cursor_move(self, cur, it, extend_selection):
        buffer = self.get_buffer()
        if not cur.equal(it) or not extend_selection:
            # move_cursor
            if extend_selection:
                buffer.move_mark_by_name("insert", it)
            else:
                buffer.place_cursor(it)
            self.scroll_mark_onscreen(buffer.get_insert())

    def do_expose_event(self, event):
        event_handled = False
        # update highlight
        if event.window == self.get_window(gtk.TEXT_WINDOW_TEXT) and not self.source_buffer is None:
            visible_rect = self.get_visible_rect()
            iter1 = self.get_line_at_y(visible_rect.y)[0]
            iter1.backward_line()
            iter2 = self.get_line_at_y(visible_rect.y + visible_rect.height)[0]
            iter2.forward_line()
            self.source_buffer.update_highlight(iter1, iter2, False)

        if event.window == self.get_window(gtk.TEXT_WINDOW_LEFT):
            self._paint_margin(event)
            event_handled = True
        else:
            buffer =self.get_buffer()
            lines = buffer.get_line_count()
            if self.old_lines != lines:
                self.old_lines = lines
                w = self.get_window(gtk.TEXT_WINDOW_LEFT)
                if not w is None:
                    w.invalidate_rect(None, False)

            if self.highlight_current_line and event.window == self.get_window(gtk.TEXT_WINDOW_TEXT):
                cur = buffer.get_iter_at_mark(buffer.get_insert())
                (y, height) = self.get_line_yrange(cur)
                visible_rect = self.get_visible_rect()
                (redraw_x, redraw_y) = self.buffer_to_window_coords(gtk.TEXT_WINDOW_TEXT,
                                                                              visible_rect.x, visible_rect.y)
                (win_x, win_y) = self.buffer_to_window_coords(gtk.TEXT_WINDOW_TEXT, 0, y)
                redraw_rect = gdk.Rectangle(redraw_x, redraw_y, visible_rect.width, visible_rect.height)

                if self.current_line_gc:
                    gc = self.current_line_gc
                else:
                    gc = self.style.bg_gc[self.state]

                if self.get_focus_hadjustment():
                    margin = self.get_left_margin() - int(self.get_focus_hadjustment())
                else:
                    margin = self.get_left_margin()

                event.window.draw_rectangle(gc, True, redraw_rect.x + max(0, margin - 1),
                                   win_y, redraw_rect.width, height)

            event_handled = TextView.do_expose_event(self, event)

            if self.show_margin and event.window == self.get_window(gtk.TEXT_WINDOW_TEXT):
                if self.cached_margin_width < 0:
                    self.cached_margin_width = self._calculate_real_tab_width(self.margin, '_')
                visible_rect = self.get_visible_rect()
                redraw_x, redraw_y = self.buffer_to_window_coords(gtk.TEXT_WINDOW_TEXT,
                                                                  visible_rect.x, visible_rect.y)
                redraw_rect = gdk.Rectangle(redraw_x, redraw_y,
                                            visible_rect.width, visible_rect.height)
                x = self.cached_margin_width - \
                    visible_rect.x + redraw_rect.x + 0.5 + \
                    self.get_left_margin()
                toggle = False
                
                text_window = self.get_window(gtk.TEXT_WINDOW_TEXT)
                line_color = gtk.gdk.Color()
                if not line_color:
                    line_color = self.style.text[gtk.STATE_NORMAL]
                try:
                    cr = text_window.cairo_create()
                except AttributeError:
                    cr = None

                if cr: # PyGTK >= 2.8
                    cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
                    cr.clip()
                    cr.set_line_width(1.0)
                    cr.move_to(x, redraw_rect.y)
                    cr.line_to(x, redraw_rect.y + redraw_rect.height)
                    # TODO: get style properties
                    alpha = 40
                    cr.set_source_rgba(line_color.red / 65535.,
                                       line_color.green / 65535.,
                                       line_color.blue / 65535.,
                                       alpha / 255.)
                    cr.stroke()
                else: # old PyGTK
                    gc = text_window.new_gc()
                    gc.set_clip_rectangle(event.area)
                    gc.set_foreground(line_color)
                    gc.set_line_attributes(1, gtk.gdk.LINE_ON_OFF_DASH, gtk.gdk.CAP_NOT_LAST, gtk.gdk.JOIN_MITER)
                    x = int(x) # no float arguments for old painting
                    text_window.draw_line(gc, x, redraw_rect.y, x, redraw_rect.y + redraw_rect.height)
                    
                if toggle:
                    # TODO: overlay draw
                    pass
        return event_handled

    def do_button_press_event(self, event):
        buf = self.get_buffer()
        if self.show_line_numbers and event.window == self.get_window(gtk.TEXT_WINDOW_LEFT):
            (x_buf, y_buf) = self.window_to_buffer_coord(gtk.TEXT_WINDOW_LEFT, event.x, event.y)
            line_start = self.get_line_at_y(y_buf)[0]
            if event.type == gdk.BUTTON_PRESS and event.button == 1:
                if event.state & gdk.CONTROL_MASK:
                    self._select_line(buf, line_start)
                elif event.state & gdk.SHIFT_MASK:
                    self._extend_selection_to_line(buf, line_start)
                else:
                    buf.place_cursor(line_start)
            elif event.type == gdk._2BUTTON_PRESS and event.button == 1:
                self._select_line(buf, line_start)
            return True
        return TextView.do_button_press_event(self, event)

    def _select_line(self, buf, line_start):
        # TODO: to implement
        pass

    def _extend_selection_to_line(self, buf, line_start):
        # TODO: to implement
        pass
    
    def _paint_margin(self, event):
        if not self.show_line_numbers and not self.show_line_markers:
            self.set_border_window_size(gtk.TEXT_WINDOW_LEFT, 0)
            return
        win = self.get_window(gtk.TEXT_WINDOW_LEFT)
        buf = self.get_buffer()
        y1 = event.area.y
        y2 = y1 + event.area.height
        (x1, y1) = self.window_to_buffer_coords(gtk.TEXT_WINDOW_LEFT, 0, y1)
        (x2, y2) = self.window_to_buffer_coords(gtk.TEXT_WINDOW_LEFT, 0, y2)

        (numbers, pixels) = self._get_lines(y1, y2)

        if len(numbers) == 0:
            numbers.append(0)
            pixels.append(0)

        tmp = str(max(99, buf.get_line_count()))
        layout = self.create_pango_layout(tmp)
        text_width = layout.get_pixel_size()[0]
        layout.set_width(text_width)
        layout.set_alignment(pango.ALIGN_RIGHT)

        if self.show_line_numbers:
            margin_width = text_width + 4
        else:
            margin_width = 0
        x_pixmap = margin_width
        if self.show_line_markers:
            margin_width += GUTTER_PIXMAP
        if margin_width == 0:
            return

        self.set_border_window_size(gtk.TEXT_WINDOW_LEFT, margin_width)
        markers = None
        if self.source_buffer and self.show_line_markers:
            # TODO: not yet implemented
            pass

        #current_marker = markers
        #if current_marker:
        #    marker_line = current_marker.data.get_line()

        cur = buf.get_iter_at_mark(buf.get_insert())
        cur_line = cur.get_line() + 1
        for number, pixel in zip(numbers, pixels):
            pos = self.buffer_to_window_coords(gtk.TEXT_WINDOW_LEFT, 0, pixel)[1]
            if self.show_line_numbers:
                line_to_paint = number + 1
                if line_to_paint == cur_line:
                    layout.set_markup("<b>%d</b>" % line_to_paint)
                else:
                    layout.set_markup("%d" % line_to_paint)
                self.style.paint_layout(win, self.state, False, None, self, None, text_width + 2, pos, layout)

            if self.show_line_markers and current_marker and marker_line == number:
                # TODO: _draw_line_markers
                pass
        

    def _get_lines(self, first_y, last_y):
        buffer_coords = []
        numbers = []
        last_line_num = -1
        it = self.get_line_at_y(first_y)[0]

        while not it.is_end():
            (y, height) = self.get_line_yrange(it)
            buffer_coords.append(y)
            last_line_num = it.get_line()
            numbers.append(last_line_num)
            if y + height >= last_y:
                break
            it.forward_line()

        if it.is_end():
            (y, height) = self.get_line_yrange(it)
            line_num = it.get_line()
            if line_num != last_line_num:
                buffer_coords.append(y)
                numbers.append(line_num)

        return (numbers, buffer_coords)
            

gobject.type_register(SourceBuffer)
gobject.type_register(SourceView)
gobject.type_register(SourceLanguagesManager)
gobject.type_register(SourceUndoManager)
gobject.type_register(SourceLanguage)
gobject.type_register(SourceContextEngine)
gobject.type_register(SourceContextData)
gobject.type_register(SourceStyle)
gobject.type_register(SourceStyleScheme)

if __name__ == "__main__":
    import gtk
    class TestApp:
        def destroy(self, widget, data=None):
            gtk.main_quit()

        def __init__(self):
            self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
            self.window.set_size_request(400, 400)
            self.window.connect("destroy", self.destroy)
            
            self.mng = SourceLanguagesManager()
            lang = self.mng.get_language_by_id(u'Lua')
            self.textbuf = SourceBuffer()
            self.textbuf.set_check_brackets(True)
            self.textbuf.set_language(lang)
            self.textbuf.set_highlight(True)
            self.textview = SourceView(self.textbuf)
            self.textview.set_tabs_width(10)
            self.textview.set_auto_indent(True)
            self.textview.set_insert_spaces_instead_of_tabs(True)
            self.textview.set_smart_home_end(True)
            self.textview.set_highlight_current_line(True)
            self.textview.set_show_line_numbers(True)
            self.textview.set_margin(80)
            self.textview.set_show_margin(True)
            self.window.add(self.textview)
            self.window.show_all()
    app = TestApp()
    gtk.main()

