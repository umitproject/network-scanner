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
import gobject
from higwidgets.higwindows import HIGWindow, HIGMainWindow
from higwidgets.higboxes import HIGVBox, HIGHBox
from higwidgets.higframe import HIGFrame
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.hignotebooks import HIGNotebook

from umit.core.UmitLogging import log
from umit.core.I18N import _

from umit.preferences.TabsWidget import TabsIcon, TabWidget
from umit.preferences.VTabManager import VTabManager


from umit.core.UmitConf import GeneralSettingsConf


import os.path
from umit.core.Paths import Path

from umit.preferences.GeneralSettings import *
from umit.preferences.Interfaces import InterfaceDetails
from umit.preferences.Expose import ExposeGeneral
from umit.preferences.conf.ExposeConf import expose_conf
from umit.preferences.NetworkSettings import NetworkTab
from umit.preferences.conf.NetworkConf import network_conf
from umit.preferences.conf.NSEConf import nse_conf

# Develpment step
# COMMENT/DELETE ME
#Path.set_umit_conf("umit")


"""
Preferences Window is a module that managing the interface of Preferences


References:
http://faq.pygtk.org/index.py?req=show&file=faq19.016.htp - 26 June 2008

"""

class PreferencesWindow(HIGMainWindow):
    def __init__(self):
        HIGMainWindow.__init__(self)
        self.set_title("Preferences")
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.resize(950,500)
        self.set_border_width(10)
        self.__pixmap_d = Path.pixmaps_dir
        self.__list = {
            'General settings':'general.svg',
            'Fonts':'fonts.svg',
            'Expose/Interface':'expose.svg',
            'Network':'network.svg'
            }
        self.__list_bw = {
            'General settings':'general-bw.svg',
            'Fonts':'fonts-bw.svg',
            'Expose/Interface':'expose-bw.svg',
            'Network':'network-bw.svg'
            }
        # FIXME
        ### Replace two list above
        self.__dic_tabs = {
            'Expose/Interface':['expose.svg','expose-bw.svg', ExposeGeneral],
            #'Network':['network.svg', 'network-bw.svg', NetworkTab],
            '.General settings':['general.svg','general-bw.svg',\
                                 GeneralSettings],
            'Interface Details':['fonts.svg','fonts-bw.svg', InterfaceDetails],
            }

        self.__create()
        self.__pack()
        self.__frame = None





        #self.connect("destroy", lambda w: gtk.main_quit())
        self.connect("delete_event", lambda w, e: self.close())
        self._create_frame("General Settings", GeneralSettings)



        # Add button Close and Help Button
        self.__closeb = HIGButton(stock=gtk.STOCK_CANCEL)
        self.__helpb = HIGButton(stock=gtk.STOCK_HELP)
        self.__applyb = HIGButton(stock = gtk.STOCK_APPLY)
        self.__okb = HIGButton(stock = gtk.STOCK_OK)
        self.__buttons_box = HIGHBox()

        self.__alignb_c = gtk.Alignment(0,0,0,0)
        self.__alignb_h = gtk.Alignment(0,0,0,0)
        self.__alignb_y = gtk.Alignment(0,0,0,0)
        self.__alignb_k = gtk.Alignment(0,0,0,0)

        self.__alignb_c.add(self.__closeb)
        self.__alignb_h.add(self.__helpb)
        self.__alignb_y.add(self.__applyb)
        self.__alignb_k.add(self.__okb)
        self.__alignb_y.set_padding(0,0, 1,1)
        self.__alignb_c.set_padding(0,0, 1,1)
        self.__alignb_h.set_padding(0,0, 1,1)
        self.__alignb_k.set_padding(0,0, 1,1)

        self.__buttons_box.pack_end(self.__alignb_k, False, False)
        self.__buttons_box.pack_end(self.__alignb_y, False, False)
        self.__buttons_box.pack_end(self.__alignb_c, False, False)

        self.__buttons_box.pack_start(self.__alignb_h, False, False)




        self.__box.pack_end(self.__buttons_box, False,  True)

        self.__closeb.connect("clicked", lambda e: self.close())
        self.__applyb.connect("clicked", self.save_changes)
        self.__okb.connect("clicked", self._save_close)

        self.connect("key-press-event", self.cb_keypress)
        self.show_all()



    # Callbacks

    def cb_keypress(self, widget, event):
        '''
        handle the "key-press-event" signal
        '''


        n = ord(event.string) if len(event.string) > 0 else ''
        kv = event.keyval
        print 'n: %s, keyval: %s' % (n, hex(kv))
        def test1():
            print "test"
        string_dict = {
            12 : test1 # ctrl-L
        }

        keyval_dict = {
            gtk.keysyms.space : self.ac
        }

        # TODO: do return values propagate correctly?
        if n in string_dict:
            string_dict[n]()
            return True # event handled
        elif kv in keyval_dict:
            keyval_dict[kv]()
            return True

    def ac(self):

        print "action"

    def _save_close(self, widget):
        self.save_changes(None)
        self.close()
        
    def save_changes(self, widget):
        log.info('>>> Saving preferences changes')
        general_settings.save_changes()
        expose_conf.save_changes()
        network_conf.save_changes()
        nse_conf.save_changes()
        
        # save changes of registered pages
        self.__vt.save_changes()

    def on_change(self, widget, text):

        #get classname
        classname = self.__dic_tabs.get(text)[2]

        self._create_frame(text, classname)

    #DELME
    ### Old school
    def on_select(self,icon_view, model=None, current=None):
        selected = icon_view.get_selected_items()

        # Frame changes
        if len(selected) == 0: return
        i = selected[0][0]


        # Put Black and White the last selected item

        if (current[0] != None and current[0] != i ):
            cat = category = model[current[0]][0]
            model.remove(model.get_iter(current[0]))
            if (current[0]>model.get_n_columns()):
                current[0]=current[0]-1
                iter_bw = None
            else:
                iter_bw = model.get_iter(current[0])
            self.__t.add_item(category, self.__list_bw.get(category), \
                          iter_bw)
            current[0] = i


        category = model[i][0]

        #get classname
        classname = self.__dic_tabs.get(category)[2]

        self._create_frame(category, classname)

        model.remove(model.get_iter(i))

        if (i>model.get_n_columns()):
            i=i-1
            iter = None
        else:
            iter = model.get_iter(i)




        self.__t.add_item(category, self.__list.get(category), \
                          iter)

    def __create(self):
        """ Create mainly widgets"""

        # TabsWidget - Create


        self.__t = TabWidget()
        self.__vt = VTabManager()

        #self.__t.add_item("General settings", "general.svg")
        #self.__t.add_item("Fonts", "fonts-bw.svg")
        #self.__t.add_item("Expose/Interface", "expose-bw.svg")
        #self.__t.add_item("Network", "network-bw.svg")
        for i in self.__dic_tabs.items():
            pixmap = os.path.join(self.__pixmap_d, "Preferences" ,i[1][0])
            pixmap_bw = os.path.join(self.__pixmap_d, "Preferences" ,i[1][1])
            self.__t.add_item(i[0], pixmap, pixmap_bw)

        self.__t.connect('changed',self.on_change)

        self.__mbox = HIGHBox()

        self.__box = HIGVBox()

    # Used for Vertical :
    def change_page(self, page):
        if self.__frame is not None:
            self.__box.remove(self.__frame)
            self.__frame.destroy()
        self.__frame = page
        self.__frame.show_all()
        self.__box.pack_start(self.__frame, True, True)
        self.__frame.set_border_width(10)

    def _create_frame(self, name, classname):
        if self.__frame is not None:
            self.__box.remove(self.__frame)
            self.__frame.destroy()

        self.__frame = classname(name)
        self.__frame.show_all()
        self.__box.pack_start(self.__frame, True, True)
        self.__frame.set_border_width(10)







    def __pack(self):
        """ Organize widgets  """


        self.__mbox.pack_start(self.__vt, False, False)
        self.__mbox.pack_start(self.__box, True, True)
        self.add(self.__mbox)


    def close(self):
        """ Close the window """

        self.hide()
        ## Save Information needed
        self.destroy()




if __name__=="__main__":
    p = PreferencesWindow()
    p.show_all()

    gtk.main()
