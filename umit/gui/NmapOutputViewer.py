#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2005-2006 Insecure.Com LLC.
# Copyright (C) 2007-2008 Adriano Monteiro Marques
#
# Author: Adriano Monteiro Marques <adriano@umitproject.org>
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
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA

import sys
import gtk
import gtk.gdk
import pango
import re

from threading import Thread

from higwidgets.higbuttons import HIGButton
from higwidgets.higboxes import HIGVBox

from umit.core.I18N import _, enc
from umit.core.UmitLogging import log
from umit.core.UmitConf import NmapOutputHighlight

from umit.gui.NmapOutputProperties import NmapOutputProperties

class NmapOutputViewer (HIGVBox):
    def __init__ (self, refresh=1, stop=1):
        self.nmap_highlight = NmapOutputHighlight()
        HIGVBox.__init__ (self)
        
        # Creating widgets
        self.__create_widgets()
        
        # Setting scrolled window
        self.__set_scrolled_window()
        
        # Setting text view
        self.__set_text_view()
        
        # Setting buttons
        self.__set_buttons()
        
        # Getting text buffer
        self.text_buffer = self.text_view.get_buffer()
        
        self.refreshing = True
        self.thread = Thread()
        
        # Adding widgets to the VPaned
        self._pack_expand_fill(self.scrolled)
        self._pack_noexpand_nofill(self.hbox_buttons)
        
        self.nmap_output_file = None
        self.nmap_previous_output = ''
        self.brazil = True

        # We have to create a mark to follow changes in the view with left grav.
        self.mark = self.text_buffer.create_mark(
            'start', 
            self.text_buffer.get_start_iter(),
            True
        )
        
        self.__create_tags()


    def __create_tags(self):
        tag_table = self.text_buffer.get_tag_table()
        
        properties = ["details",
              "date",
              "hostname",
              "ip",
              "port_list",
              "open_port",
              "closed_port",
              "filtered_port"]

        for name in properties:
            tag = tag_table.lookup(name)
            if tag:
                tag_table.remove(tag)
        
        for p in xrange(len(properties)):
            settings = self.nmap_highlight.__getattribute__(properties[p])
            
            # Create a tag name
            tag = gtk.TextTag(properties[p])
                
            if settings[0]:
                tag.set_property("weight", pango.WEIGHT_HEAVY)
            else:
                tag.set_property("weight", pango.WEIGHT_NORMAL)
                
            if settings[1]:
                tag.set_property("style", pango.STYLE_ITALIC)
            else:
                tag.set_property("style", pango.STYLE_NORMAL)
            
            if settings[2]:
                tag.set_property("underline", pango.UNDERLINE_SINGLE)
            else:
                tag.set_property("underline", pango.UNDERLINE_NONE)

            text_color = settings[3]
            highlight_color = settings[4]

            tag.set_property("foreground",
gtk.color_selection_palette_to_string([gtk.gdk.Color(*text_color),]))
            tag.set_property("background",
gtk.color_selection_palette_to_string([gtk.gdk.Color(*highlight_color),]))

            tag_table.add(tag)
            tag.set_priority(p)
        
        # brasil tags
        names = ('brasil1', 'brasil2', 'brasil3')
        prop = ('foreground', 'background', 'weight')
        values = (('#EAFF00', '#21C800', pango.WEIGHT_HEAVY),
                  ('#0006FF', '#21C800', pango.WEIGHT_HEAVY),
                  ('#FFFFFF', '#21C800', pango.WEIGHT_HEAVY))
        
        for name in names:
            tag = tag_table.lookup(name)
            if tag:
                tag_table.remove(tag)

        for i in xrange(len(names)):
            tag = gtk.TextTag(names[i])
            for tup in zip(prop, values[i]):
                tag.set_property(tup[0], tup[1])
            tag_table.add(tag)

        self.txg_font = gtk.TextTag()
        self.txg_date = gtk.TextTag()
        self.txg_font.set_property("family", "Monospace")

        tag_table.add(self.txg_font)
        tag_table.add(self.txg_date)
    
    def __create_widgets (self):
        # Creating widgets
        self.scrolled = gtk.ScrolledWindow ()
        self.text_view = gtk.TextView ()
        self.btn_refresh = gtk.Button (stock=gtk.STOCK_REFRESH)
        self.check_enable_color = gtk.CheckButton(\
            _("Enable Nmap output highlight"))
        self.btn_output_properties = HIGButton(stock=gtk.STOCK_PREFERENCES)
        self.hbox_buttons = gtk.HBox (spacing=5)
    
    def __set_scrolled_window(self):
        # By default the vertical scroller remains at bottom
        self._scroll_at_bottom = True

        # Seting scrolled window
        self.scrolled.set_border_width(5)
        self.scrolled.add(self.text_view)
        self.scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        vadjust = self.scrolled.get_vadjustment()
        vadjust.connect('changed', self.__adjustment_update)
        vadjust.connect('value-changed', self.__adjustment_at_bottom)

    def __adjustment_at_bottom(self, adjustment):
        vadjust_end = adjustment.upper - adjustment.page_size
        self._scroll_at_bottom = adjustment.value == vadjust_end

    def __adjustment_update(self, adjustment):
        if self._scroll_at_bottom:
            adjustment.set_value(adjustment.upper - adjustment.page_size)

    def __set_text_view(self):
        self.text_view.set_wrap_mode(gtk.WRAP_WORD)
        self.text_view.set_editable(False)
        
    def __set_buttons (self):
        self.check_enable_color.set_active(self.nmap_highlight.enable)
        
        # Connecting events
        self.btn_refresh.connect('clicked',
                                 self.refresh_output)
        self.btn_output_properties.connect("clicked",
                                           self.show_output_properties)
        self.check_enable_color.connect("toggled",
                                        self.enable_color_highlight)
        
        # Setting hbox
        self.hbox_buttons.set_border_width(5)
        
        # Packing buttons
        self.hbox_buttons.pack_start(self.check_enable_color)
        self.hbox_buttons.pack_start(self.btn_output_properties)
        self.hbox_buttons.pack_start(self.btn_refresh)

    def enable_color_highlight(self, widget):
        if widget.get_active():
            self.nmap_highlight.enable = 1
        else:
            self.nmap_highlight.enable = 0

        self.update_output_colors()

    def show_output_properties(self, widget):
        nmap_out_prop = NmapOutputProperties(self.text_view)
        nmap_out_prop.run()
        
        for prop in nmap_out_prop.property_names:
            widget = nmap_out_prop.property_names[prop][8]

            wid_props = []

            if widget.bold:
                wid_props.append(1)
            else:
                wid_props.append(0)

            if widget.italic:
                wid_props.append(1)
            else:
                wid_props.append(0)

            if widget.underline:
                wid_props.append(1)
            else:
                wid_props.append(0)
 
            wid_props.append("(%s, %s, %s)" % (widget.text_color.red,
                                               widget.text_color.green,
                                               widget.text_color.blue))
            wid_props.append("(%s, %s, %s)" % (widget.highlight_color.red,
                                               widget.highlight_color.green,
                                               widget.highlight_color.blue))

            self.nmap_highlight.__setattr__(widget.property_name, wid_props)
            
        nmap_out_prop.destroy()
        self.nmap_highlight.save_changes()
        
        # TODO: Foreach in all tabs to update ?
        self.__create_tags()

        self.update_output_colors()
    
    def update_output_colors(self, dialog=None, response_id=None):
        self.text_buffer.move_mark(self.mark, self.text_buffer.get_start_iter())

        buff = self.text_view.get_buffer()
        tag_table = buff.get_tag_table()
        
        # Get the not-parsed text
        start = self.text_buffer.get_iter_at_mark(self.mark)
        end = self.text_buffer.get_end_iter()
        
        self.text_buffer.remove_all_tags(start, end)
        self.text_buffer.apply_tag(self.txg_font, start, end)
        
        if not self.nmap_highlight.enable or start == end:
            return
        
        text = buff.get_text(start, end)
        
        # Get the line offset
        offset = start.get_line()
        
        if text:
            text = text.split("\n")
            properties = ["details",
                          "date",
                          "hostname",
                          "ip",
                          "port_list",
                          "open_port",
                          "closed_port",
                          "filtered_port"]
            
            for pos in xrange(len(text)):
                if not text[pos]:
                    continue
                
                for p in xrange(len(properties)):
                    settings = self.nmap_highlight.__getattribute__(\
                        properties[p])
                    match = re.finditer(settings[5], text[pos])
                    
                    for m in match:
                        buff.apply_tag(tag_table.lookup(properties[p]),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.start()),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end()))
                    
                    tag1 = tag_table.lookup('brasil1')
                    tag2 = tag_table.lookup('brasil2')
                    tag3 = tag_table.lookup('brasil3')
                    
                    match = re.finditer("Bra[sz]il", text[pos])
                    
                    for m in match:
                        buff.apply_tag(tag1,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.start()),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() - 5))

                        buff.apply_tag(tag2,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 1),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() -4))

                        buff.apply_tag(tag3,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 2),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() - 3))
                        
                        buff.apply_tag(tag1,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 3),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() - 2))

                        buff.apply_tag(tag2,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 4),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() - 1))

                        buff.apply_tag(tag3,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 5),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end()))
                    else:
                        self._brasil_log()
                    
                    match = re.finditer("BRT", text[pos])
                    
                    for m in match:
                        buff.apply_tag(tag1,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.start()),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() - 2))

                        buff.apply_tag(tag2,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 1),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end() -1))

                        buff.apply_tag(tag3,
                                       buff.get_iter_at_line_index(pos + offset,
                                                                m.start() + 2),
                                       buff.get_iter_at_line_index(pos + offset,
                                                                   m.end()))
                    else:
                        self._brasil_log()
                    
        self.text_buffer.move_mark(self.mark, self.text_buffer.get_end_iter())

    def _brasil_log(self):
        if self.brazil:
            log.info("Isto aqui, o o")
            log.info("E um pouquinho de Brasil, io io")
            log.info("Deste Brasil que canta e e feliz")
            log.info("Feliz, feliz")
            log.info("")
            log.info("E tambem um pouco de uma raca")
            log.info("Que nao tem medo de fumaca ai, ai")
            log.info("E nao se entrega, nao ")
            log.info("")
            log.info('Olha o jeito das "cadera"  que ela sabe dar')
            log.info("Olha o tombo nos quadris que ela sabe dar")
            log.info("Olha o passe de batuque que ela sabe dar")
            log.info("Olha so o remelexo que ela sabe dar")
            log.info("")
            log.info("Morena boa me faz chorar")
            log.info("Poe a sandalia de prata")
            log.info("e vem pro samba sambar")
            
            self.brazil = False
    
    def show_nmap_output(self, file):
        self.nmap_output_file = file
        self.text_buffer.set_text("")
        self.refresh_output()

    def refresh_output(self, widget=None):
        log.debug("Refresh nmap output")

        if self.nmap_output_file is not None:
            nmap_of = open(self.nmap_output_file, "r")

            new_output = nmap_of.read()

            if self.nmap_previous_output != new_output:
                # Setting text and moving mark to the start
                # to update_colors correctly
                text_prev_len = len(self.nmap_previous_output)

                self.text_buffer.insert(
                        self.text_buffer.get_end_iter(),
                        enc(new_output[text_prev_len:]))

                self.nmap_previous_output = new_output

                self.update_output_colors()

            nmap_of.close()


if __name__ == '__main__':
    w = gtk.Window()
    n = NmapOutputViewer()
    w.add(n)
    w.show_all()
    w.connect('delete-event', lambda x,y,z=None:gtk.main_quit())

    buff = n.text_view.get_buffer()
    buff.set_text(open("file_with_encoding_issues.txt", 'rb').read())

    gtk.main()
