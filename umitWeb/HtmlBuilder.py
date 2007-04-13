# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Rodolfo da Silva Carvalho <rodolfo.ueg@gmail.com>
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
"""Html code generation module
"""

import re

from types import StringTypes

__revision__ = "299"

__all__ = ["BaseTag", "HtmlTag", "BodyTag", "HeadTag", "StyleTag", \
           "LinkTag", "ATag", "TextareaTag", "SelectTag", "OptionTag", \
           "DivTag", "FormTag", "InputTag", "TextTag", "PasswordTag", \
           "CheckboxTag", "RadioTag", "TableTag", "TdTag", "ThTag", "TrTag", \
           "UlTag", "LiTag"]

class BaseTag:
    """Base for all HTML tags
    some properties are defined here:
     -properties: a list of properties of a HTML tag, like class, style,
                 name, etc.
     -name: the tag's identifier, i.e. input, font, div, style
     -long_tag: a boolean attribute that indicates when the tag are short 
                (ended with '/>') if False, or long (in format:
                <element></element>) if True
     -childs: the childs of an object. (text on a 'div' tag, an option object
              inside a select object, etc.

    Note: the __repr__ method is used to represent the instance. Not more 
              natural than denotates the object by it's HTML representation.
    """

    def __init__(self, **args):
        """Constructor
        """
        self.properties = {}
        if args:
            for i in args.keys():
                if i != "childs":
                    self.properties[i] = args[i]
        self.name = ""
        self.long_tag = False

        self.childs = []
        if args.has_key("childs"):
            for i in args["childs"]:
                self.childs.append(i)

    def __repr__(self):
        return self.build_tag()

    def build_tag(self):
        """Builds the HTML Structure of the object, and returns it
        """
        html = ["<%s" % self.name]
        for key in self.properties.keys():
            html.append("%s='%s'"% (key, self.properties[key]))
        if self.long_tag:
            html.append(">")
            for element in self.childs:
                html.append("%s\n"%element)
            html.append("</%s>"%self.name)
        else:
            html.append("/>")
        return " ".join(html)

    def add_child(self, child):
        """Adds a child node, or plain text
        """
        if child not in self.childs:
            self.childs.append(child)
            return True
        else:
            return False

    def remove_child(self, child):
        """Removes a child
        """
        if child in self.childs:
            self.childs.remove(child)
            return True
        else:
            return False

    def set_property(self, prop, value):
        """Sets an Html property
        """
        self.properties[prop] = value

    def get_property(self, prop):
        """Gets an Html property
        """
        if self.properties.has_key(prop):
            return self.properties[prop]
        else:
            return ""

    def set_style(self, style):
        """Sets Html property 'style'
        """
        self.set_property("style", style)

    def set_class(self, s_class):
        """Sets Html property 'class'
        """
        self.set_property("class", s_class)

    def add_event(self, event_name, action):
        """Adds an Html event
        """
        self.set_property(event_name, action)

    def remove_event(self, event_name):
        """Removes an Html event
        """
        self.set_property(event_name, "")

    def get_child(self, child_of):
        """Gets a child, based in a nested element inside its
        """
        for child in self.childs:
            if type(child) not in StringTypes:
                if child_of in child.childs:
                    return child


class HtmlTag(BaseTag):
    """A 'html' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "html"
        self.long_tag = True


class BodyTag(BaseTag):
    """A 'body' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "body"
        self.long_tag = True


class HeadTag(BaseTag):
    """A 'head' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "head"
        self.long_tag = True


class StyleTag(BaseTag):
    """A 'style' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True
        self.name = "style"


class LinkTag(BaseTag):
    """A 'link' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "link"

    def set_rel(self, rel):
        """Sets Html property 'rel'
        """
        self.set_property("rel", rel)

    def set_href(self, href):
        """Sets Html property 'href'
        """
        self.set_property("href", href)


class ATag(BaseTag):
    """An 'a' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True
        self.name = "a"

    def set_href(self,  href):
        """Sets Html property 'href'
        """
        self.set_property("href", href)


class TextareaTag(BaseTag):
    """A 'a' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True

    def set_rows(self, rows):
        """Sets Html property 'rows'
        """
        self.set_property("rows", rows)

    def set_cols(self, cols):
        """Sets Html property 'cols'
        """
        self.set_property("cols", cols)


class SelectTag(BaseTag):
    """A 'select' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True
        self.name = "select"

    def add_option(self, value, display, selected=False):
        """Adds an Option object as its child
        """
        option = OptionTag(value=value, childs=[display])
        option.add_child(display)
        option.set_selected(selected)
        self.add_child(option)
        return option

    def set_name(self, name):
        """Sets Html property 'name'
        """
        self.set_property("name", name)


class OptionTag(BaseTag):
    """An 'option' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True
        self.name = "option"

    def set_selected(self, selected):
        """Sets Html property 'selected'
        """
        self.set_property("selected", selected and "selected" or "")


class DivTag(BaseTag):
    """A 'div' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True
        self.name = "div"


class FormTag(BaseTag):
    """A 'form' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.long_tag = True

    def set_action(self, action):
        """Sets Html property 'action'
        """
        self.set_property("action", action)

    def set_method(self, method):
        """Sets Html property 'method'
        """
        self.set_property("method", method)


class InputTag(BaseTag):
    """An 'input' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "input"

    def set_value(self, value):
        """Sets Html property 'value'
        """
        self.set_property("value", value)

    def set_name(self, name):
        """Sets Html property 'value'
        """
        self.set_property("name", name)


class TextTag(InputTag):
    """An text input tag
    """

    def __init__(self,**args):
        InputTag.__init__(self,**args)
        self.set_property("type", "text")

    def set_size(self, size):
        """Sets Html property 'size'
        """
        self.set_property("size", size)

    def set_max_length(self, max_length):
        """Sets Html property 'maxlength'
        """
        self.set_property("maxlength", max_length)


class PasswordTag(InputTag):
    """A password input tag
    """

    def __init__(self,**args):
        InputTag.__init__(self,**args)
        self.set_property("type", "password")


class CheckboxTag(InputTag):
    """A checkbox input tag
    """

    def __init__(self,**args):
        InputTag.__init__(self,**args)
        self.set_property("type", "checkbox")

    def set_checked(self, checked):
        """Sets Html property 'checked'
        """
        self.set_property("checked", checked and "checked" or "")


class RadioTag(CheckboxTag):
    """A radio button input tag
    """
    def __init__(self,**args):
        CheckboxTag.__init__(self,**args)
        self.set_property("type", "radio")


class TableTag(BaseTag):
    """A 'table' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "table"
        self.long_tag = True


class TdTag(BaseTag):
    """A 'td' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "td"
        self.long_tag = True


class ThTag(TdTag):
    """A 'th' Html tag
    """

    def __init__(self,**args):
        TdTag.__init__(self,**args)
        self.name = "th"


class TrTag(BaseTag):
    """A 'tr' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "tr"
        self.long_tag = True


class UlTag(BaseTag):
    """A 'ul' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "ul"
        self.long_tag = True


class LiTag(BaseTag):
    """A 'li' Html tag
    """

    def __init__(self,**args):
        BaseTag.__init__(self,**args)
        self.name = "li"
        self.long_tag = True