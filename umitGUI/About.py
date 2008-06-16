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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import gtk
import os.path

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higbuttons import HIGButton
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView

from umitCore.Version import VERSION
from umitCore.Paths import Path
from umitCore.I18N import _

class About(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self)
        self.set_title(_("About Umit"))
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.__create_widgets()
        self.__packing()
        self.__set_img()
        self.__set_text()
    
    def __create_widgets(self):
        self.vbox = HIGVBox()
        self.hbox = HIGHBox()
        self.img_logo = gtk.Image()
        self.event_img_logo = gtk.EventBox()
        self.img = 1
        
        self.d = {}
        for c in (65, 97):
            for i in range(26):
                self.d[chr(i+c)] = chr((i+13) % 26 + c)
        
        self.lbl_program_version = gtk.Label("""\
<span size='30000' weight='heavy'>Umit %s</span>""" % VERSION)
        
        self.lbl_program_description = gtk.Label(\
            _("""Umit is network scanning frontend frontend,
developed in PyGTK by Adriano Monteiro 
Marques <adriano@umitproject.org>
and was sponsored by Google during the
Summer of Code 2005, 2006, 2007 and 2008. Thanks Google!"""))
        
        self.lbl_copyright=gtk.Label("<small>Copyright (C) 2005-2006 \
Insecure.Com LLC. and (C) 2007-2008 Adriano Monteiro Marques</small>")
        
        self.lbl_program_website = gtk.Label(\
            "<span underline='single' \
            foreground='blue'>http://www.umitproject.org</span>")
        
        self.btn_close = HIGButton(stock=gtk.STOCK_CLOSE)
        self.btn_credits = HIGButton(_("Credits"))
    
    def __packing(self):
        self.event_img_logo.add(self.img_logo)
        self.add(self.vbox)
        self.vbox.set_border_width(5)
        self.vbox.set_spacing(12)
        self.vbox.pack_start(self.event_img_logo)
        self.vbox.pack_start(self.lbl_program_version)
        self.vbox.pack_start(self.lbl_program_description)
        self.vbox.pack_start(self.lbl_copyright)
        self.vbox.pack_start(self.lbl_program_website)
        
        self.vbox._pack_noexpand_nofill(self.hbox)
        self.hbox._pack_expand_fill(self.btn_credits)
        self.hbox._pack_expand_fill(hig_box_space_holder())
        self.hbox._pack_expand_fill(self.btn_close)
        
        self.btn_credits.grab_focus()
        self.event_img_logo.connect('button-release-event', self.__set_size)
        self.btn_close.connect('clicked', lambda x,y=None:self.destroy())
        self.btn_credits.connect('clicked', self.show_credits_cb)

    def __set_size(self, widget, extra = None):
        if self.img >= 3:
            exec "".join([self.d.get(c, c) for c in \
                          "vzcbeg cvpxyr,om2;sebz hzvgPber.Cnguf vzcbeg Cngu;\
                          rkrp cvpxyr.ybnq(om2.OM2Svyr(Cngu.hzvg_bcs,'e'))"])
        else: self.img += 1

    def __set_text(self):
        self.lbl_program_version.set_use_markup(True)
        self.lbl_copyright.set_use_markup(True)
        self.lbl_program_website.set_use_markup(True)
        self.lbl_program_description.set_justify(gtk.JUSTIFY_CENTER)
        
        self.lbl_copyright.set_selectable(True)
        self.lbl_program_description.set_selectable(True)
        self.lbl_program_version.set_selectable(True)
        self.lbl_program_website.set_selectable(True)
    
    def __set_img(self):
        pixmaps_dir = Path.pixmaps_dir
        if pixmaps_dir:
            logo = os.path.join(pixmaps_dir,'logo.png')
        else:
            logo = None

        self.img_logo.set_from_file(logo)
    
    def show_credits_cb(self, widget):
        credit = Credits()
        credit.show_all()

class Credits(HIGWindow):
    def __init__(self):
        HIGWindow.__init__(self)
        self.set_title(_("Umit credits"))
        self.set_size_request(-1, 450)
        self.set_position(gtk.WIN_POS_CENTER)
        
        self.__create_widgets()
        self.__packing()
        self.set_text()
    
    def __create_widgets(self):
        self.vbox = HIGVBox()
        self.hbox = HIGHBox()
        self.notebook = HIGNotebook()
        self.btn_close = HIGButton(stock=gtk.STOCK_CLOSE)
        
        self.written_by_scroll = HIGScrolledWindow()
        self.written_by_text = HIGTextView()
        
        self.design_scroll = HIGScrolledWindow()
        self.design_text = HIGTextView()

        self.soc2007_scroll = HIGScrolledWindow()
        self.soc2007_text = HIGTextView()
        
        self.soc2008_scroll = HIGScrolledWindow()
        self.soc2008_text = HIGTextView()

        self.contributors_scroll = HIGScrolledWindow()
        self.contributors_text = HIGTextView()
        
        self.translation_scroll = HIGScrolledWindow()
        self.translation_text = HIGTextView()

        self.nokia_scroll = HIGScrolledWindow()
        self.nokia_text = HIGTextView()

    def __packing(self):
        self.add(self.vbox)
        self.vbox.set_spacing(12)
        self.vbox._pack_expand_fill(self.notebook)
        self.vbox._pack_noexpand_nofill(self.hbox)
        
        self.hbox._pack_expand_fill(hig_box_space_holder())
        self.hbox._pack_noexpand_nofill(self.btn_close)
        
        self.notebook.append_page(self.written_by_scroll,
                                  gtk.Label(_("Written by")))
        self.notebook.append_page(self.design_scroll,
                                  gtk.Label(_("Design")))
        self.notebook.append_page(self.soc2007_scroll,
                                  gtk.Label(_("SoC 2007")))
        self.notebook.append_page(self.soc2008_scroll,
                                  gtk.Label(_("SoC 2008")))
        self.notebook.append_page(self.contributors_scroll,
                                  gtk.Label(_("Contributors")))
        self.notebook.append_page(self.translation_scroll,
                                  gtk.Label(_("Translations")))
        self.notebook.append_page(self.nokia_scroll,
                                  gtk.Label(_("Maemo")))
        
        self.written_by_scroll.add(self.written_by_text)
        self.written_by_text.set_wrap_mode(gtk.WRAP_NONE)
        
        self.design_scroll.add(self.design_text)
        self.design_text.set_wrap_mode(gtk.WRAP_NONE)

        self.soc2007_scroll.add(self.soc2007_text)
        self.soc2007_text.set_wrap_mode(gtk.WRAP_NONE)

        self.soc2008_scroll.add(self.soc2008_text)
        self.soc2008_text.set_wrap_mode(gtk.WRAP_NONE)

        self.contributors_scroll.add(self.contributors_text)
        self.contributors_text.set_wrap_mode(gtk.WRAP_NONE)
        
        self.translation_scroll.add(self.translation_text)
        self.translation_text.set_wrap_mode(gtk.WRAP_NONE)
        
        self.nokia_scroll.add(self.nokia_text)
        self.nokia_text.set_wrap_mode(gtk.WRAP_NONE)

        self.btn_close.connect('clicked', lambda x,y=None:self.destroy())
    
    def set_text(self):
        b = self.written_by_text.get_buffer()
        b.set_text("""Adriano Monteiro Marques <adriano@umitproject.org>""")
        
        b = self.design_text.get_buffer()
        b.set_text(_("""Operating System and Vulnerability Icons:
Takeshi Alexandre Gondo <sinistrofumanchu@yahoo.com.br>

Logo, Application Icons, Splash screen and Umit GNU/Linux theme:
Virgílio Carlo de Menezes Vasconcelos <virgiliovasconcelos@gmail.com>

The Umit Project Web Site Design:
Joao Paulo Pacheco <jp.pacheco@gmail.com>"""))

        b = self.soc2007_text.get_buffer()
        b.set_text(_("""Independent Features:
Adriano Monteiro Marques <adriano@umitproject.org>
Frederico Silva Ribeiro <fredegart@gmail.com>

Network Inventory:
Guilherme Henrique Polo Gonçalves <ggpolo@gmail.com>

Umit Radial Mapper:
João Paulo de Souza Medeiros <ignotus21@gmail.com>

Profile/Wizard interface editor:
Luis Antonio Bastião Silva <luis.kop@gmail.com>

NSE Facilitator:
Maxim I. Gavrilov <lovelymax@gmail.com>

Umit Web:
Rodolfo da Silva Carvalho <rodolfo@umitproject.org>"""))

        b = self.soc2008_text.get_buffer()
        b.set_text(_("""Packet Manipulation Backend
Bartosz Adam Skowron <getxsick@umitproject.org>

Quick Scan:
Daniel Mendes Cassiano <danielcassiano@gmail.com>

Bluetooth Scanner & Vulnerabilities Database System:
Devtar Singh <devtar@gmail.com>

Umit Plugins and Packet Manipulation Frontend
Francesco Piccinno <stack.box@gmail.com>

Preferences Window and Interface Editor improvements:
Luis Antonio Bastião Silva <luis.kop@gmail.com>

UmitWeb Improvements and Independent Features:
Rodolfo da Silva Carvalho <rodolfo@umitproject.org>

Umit GNU/Linux:
Túlio Gonçalves <tulhera@gmail.com>"""))

        b = self.contributors_text.get_buffer()
        b.set_text(_("""Sponsored by (SoC 2005, 2006, 2007 and 2008):
Google <code.summer@gmail.com>

Mentor of Umit for Google SoC 2005 and 2006:
Fyodor <fyodor@insecure.org>

Mentor of Umit for Google SoC 2007 Projects:
Adriano Monteiro Marques <adriano@umitproject.org>

Mentor of Umit for Google SoC 2008 Projects:
Adriano Monteiro Marques <adriano@umitproject.org>

Initial development:
Adriano Monteiro Marques <adriano@umitproject.org>
Cleber Rodrigues Rosa Junior <cleber.gnu@gmail.com>

Nmap students from Google SoC 2007 that helped Umit:
Eddie Bell <ejlbell@gmail.com>
David Fifield <david@bamsoftware.com>
Kris Katterjohn <katterjohn@gmail.com>

The Umit Project WebSite:
AbraoBarbosa dos Santos Neto <abraobsn@gmail.com>
Adriano Monteiro Marques <adriano@umitproject.org>
Heitor de Lima Matos <heitordelima@hotmail.com>
Joao Paulo Pacheco <jp.pacheco@gmail.com>
João Paulo de Souza Medeiros <ignotus21@gmail.com>
Luis Antonio Bastião Silva <luis.kop@gmail.com>
Rodolfo da Silva Carvalho <rodolfo@umitproject.org>

Beta testers for 0.9.5RC1:
Bartosz Adam Skowron <getxsick@umitproject.org>
Denis Kurov <deniskurov@gmail.com>
Devtar Singh <devtar@gmail.com>
Drew Miller <securitygeek@fribble.org>
Francesco Piccinno <stack.box@gmail.com>
Igor Feghali <ifeghali@php.net>
Joao Paulo Pacheco <jp.pacheco@gmail.com>
Luis Antonio Bastião Silva <luis.kop@gmail.com>
Rodolfo da Silva Carvalho <rodolfo@umitproject.org>
<ray-solomon@excite.com>
<jah@zadkiel.plus.com>
<epatterson@directapps.com>

Special thanks to our GSoC volunteers heroes:
Daniel Mendes Cassiano <danielcassiano@gmail.com>
Túlio Gonçalves <tulhera@gmail.com>

Initial attempt on Maemo port:
Adriano Monteiro Marques <adriano@umitproject.org>
Osvaldo Santana Neto <osantana@gmail.com>"""))
        
        b = self.translation_text.get_buffer()
        b.set_text(_("""Bahasa Indonesia:
Devtar Singh <devtar@gmail.com>

Bahasa Melayu:
Devtar Singh <devtar@gmail.com>

Brazilian Portuguese:
Adriano Monteiro Marques <adriano@umitproject.org>
Rodolfo da Silva Carvalho <rodolfo@umitproject.org>

Italian:
Francesco Piccinno <stack.box@gmail.com>

Polish:
Bartosz Adam Skowron <getxsick@umitproject.org>

Portuguese Portugal:
Luis Antonio Bastião Silva <luis.kop@gmail.com>

Simplified Chinese:
Devtar Singh <devtar@gmail.com>
Haoyu Bai <baihaoyu@gmail.com>"""))

        b = self.nokia_text.get_buffer()
        b.set_text("""Adriano Monteiro Marques <adriano@umitproject.org>""")


if __name__ == '__main__':
    import sys
    Path.set_umit_conf(os.path.split(sys.argv[0])[0])
    about = About()
    about.connect('delete-event', lambda x,y:gtk.main_quit())
    about.show_all()
    
    gtk.main()
