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

from higwidgets.higtables import HIGTable
from higwidgets.hignotebooks import HIGNotebook

from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higentries import HIGTextEntry
from higwidgets.higbuttons import HIGButton

from umit.core.UmitLogging import log
from umit.core.I18N import _

from umit.preferences.FramesHIG import *
from umit.preferences.PreviewWindowObj import PreviewWindowObj

# Import config parsers
from umit.preferences.conf.ExposeConf import expose_conf
from umit.preferences.conf.ProfilesConf import profile_conf


class ExposeGeneral(HIGNotebook):
    def __init__(self, name):
        HIGNotebook.__init__(self)
        self._create_widgets()


    def _create_widgets(self):
        # Notebook
        self._nb = self
        self._create_expose()
        self._create_expose_settings()

        self._nb.append_page(self._expose_box, gtk.Label(_('Expose')))
        self._nb.append_page(self._expose_settings_box, gtk.Label(_('Advanced')))

    def _create_expose(self):
        self._expose_box = ExposeWindow('Expose')


    def _create_expose_settings(self):
        self._expose_settings_box = ExposeSettings()

class ExposeSettings(TabBox, object):
    def __init__(self):
        TabBox.__init__(self, _('Expose Settings'))

        self._pack_widgets()
        self._create_events()


        # Default propertys
        self.page_inside = expose_conf.page_inside

    def _create_widgets(self):
        #self._create_fonts_widgets()
        self._create_tabs_widgets()

    def _create_fonts_widgets(self):
        self._box_fonts_frame = HIGFrame(_('Fonts'))
    def _create_tabs_widgets(self):

        # Tabs
        self._frame_tabs = HIGFrame(_('Tabs'))
        self._box_tabs = HIGVBox()
        self._radio_inside = gtk.RadioButton(None, _('Scans inside Umit'))
        self._radio_outside = gtk.RadioButton(self._radio_inside,\
                                              _('Scans outside Umit'))


        # Toolbar:
        self._frame_toolbar = HIGFrame(_('Toolbar'))
        self._lbl_tlb_size = gtk.Label(_('Toolbar Size: '))
        self._lbl_tlb_style = gtk.Label(_('Toolbar Style: '))

        self._cmb_tlb_size = gtk.combo_box_new_text()

        self._cmb_tlb_size.append_text(_('Small'))
        self._cmb_tlb_size.append_text(_('Medium'))
        self._cmb_tlb_size.append_text(_('Larger'))
        self._cmb_tlb_size.append_text(_('System Default'))

        self._cmb_tlb_style = gtk.combo_box_new_text()
        self._cmb_tlb_style.append_text(_('Icons'))
        self._cmb_tlb_style.append_text(_('Text'))
        self._cmb_tlb_style.append_text(_('Both'))


        self._tbl_tlb = HIGTable()




    def _pack_widgets(self):

        # Pack Tabs
        self.pack_start(self._frame_tabs, False, False)
        self._frame_tabs.add(self._box_tabs)
        self._box_tabs.pack_start(self._radio_inside, False, False)
        self._box_tabs.pack_start(self._radio_outside, False, False)

        # Pack Toolbar

        self.pack_start(self._frame_toolbar, False, False)
        self._frame_toolbar.add(self._tbl_tlb)

        self._tbl_tlb.attach_label(self._lbl_tlb_size,0,1,0,1)
        self._tbl_tlb.attach_entry(self._cmb_tlb_size, 1,2,0,1)

        self._tbl_tlb.attach_label(self._lbl_tlb_style,0,1,1,2)
        self._tbl_tlb.attach_entry(self._cmb_tlb_style, 1,2,1,2)



        # Pack Fonts
        #self.pack_start(self._box_fonts_frame)

    def _create_events(self):
        self._radio_inside.connect("toggled", self.update_page)
        self._radio_outside.connect("toggled", self.update_page)

    def update_page(self, widget):
        print "lol"
        if not widget.get_active():
            return
        # Widget is enable.
        ## But which is enable?
        print "updating page!"
        if widget == self._radio_inside:
            expose_conf.page_inside = True
        elif widget == self._radio_outside:
            expose_conf.page_inside = False

    # API
    def get_page_inside(self):
        print "get page"
        if self._radio_inside.get_active():
            return True
        else:
            return False
    def set_page_inside(self, page):
        if page:
            self._radio_inside.set_active(True)
        else:
            self._radio_outside.set_active(True)

    page_inside = property(get_page_inside, set_page_inside)



class ExposeWindow(TabBox):
    """
    Import a Widget with a small preview of Umit (PreviewWindow)
    Aim of widget is change structure of Umit like hide menu, etc

    """

    def __init__(self, name):
        """ Create defaults Widget """
        TabBox.__init__(self, name)
    def _create_widgets(self):
        """ Create widgets"""

        # Create table and attach it contains
        self.__table = HIGTable(5,2)
        binary_mask = gtk.EXPAND|gtk.SHRINK
        p = PreviewWindowObj()
        p.set_size_request(300,300)

        align = gtk.Alignment()
        align.add(p)
        align.set_padding(10,10,10,10)
        self.__table.attach(align, 0,1,0,1,binary_mask, gtk.FILL)

        self.pack_start(self.__table, False, False)
    def _create_expose_interface(self):
        pass

class ExposeProfiles(TabBox, object):

    def __init__(self, name):
        """ Create defaults Widget """
        TabBox.__init__(self, name)
        self._pack_widgets()
        self._connect_events()
    def _create_widgets(self):
        """ Create widgets"""

        self._frm_option = HIGFrame(_('Options'))
        self._box_option = HIGHBox()
        self.__lbl_file_opt = HIGEntryLabel(_('File:'))
        self.__entry_file_opt = HIGTextEntry()
        self.__entry_file_opt.set_editable(False)
        self.__file_browser_opt = HIGButton(_('Browse file'), \
                                            gtk.STOCK_DIRECTORY)

        self._frm_profile = HIGFrame(_('Profile'))
        self._box_profile = HIGHBox()
        self.__lbl_file_profile = HIGEntryLabel(_('File:'))
        self.__entry_file_profile = HIGTextEntry()
        self.__entry_file_profile.set_editable(False)
        self.__file_browser_profile = HIGButton(_('Browse file'), \
                                            gtk.STOCK_DIRECTORY)

        self._frm_wizard = HIGFrame(_('Wizard'))
        self._box_wizard = HIGHBox()

        self.__lbl_file_wizard = HIGEntryLabel(_('File:'))
        self.__entry_file_wizard = HIGTextEntry()
        self.__entry_file_wizard.set_editable(False)
        self.__file_browser_wizard = HIGButton(_('Browse file'), \
                                            gtk.STOCK_DIRECTORY)

        self.__btn_restore = HIGButton(_('Restore Defaults'), gtk.STOCK_CLEAR)

    def _pack_widgets(self):

        # Options
        self._box_option._pack_noexpand_nofill(self.__lbl_file_opt)
        self._box_option._pack_noexpand_nofill(self.__entry_file_opt)
        self._box_option._pack_noexpand_nofill(self.__file_browser_opt)
        self._frm_option.add(self._box_option)

        # Profile
        self._box_profile._pack_noexpand_nofill(self.__lbl_file_profile)
        self._box_profile._pack_noexpand_nofill(self.__entry_file_profile)
        self._box_profile._pack_noexpand_nofill(self.__file_browser_profile)
        self._frm_profile.add(self._box_profile)

        # Wizard
        self._box_wizard._pack_noexpand_nofill(self.__lbl_file_wizard)
        self._box_wizard._pack_noexpand_nofill(self.__entry_file_wizard)
        self._box_wizard._pack_noexpand_nofill(self.__file_browser_wizard)
        self._frm_wizard.add(self._box_wizard)

        # Pack Frames
        self.pack_start(self._frm_option, False,False)
        self.pack_start(self._frm_profile, False, False)
        self.pack_start(self._frm_wizard, False, False)
    
    def _connect_events(self):
        self.__entry_file_opt.connect("changed", self.update_file_opt)
        self.__entry_file_profile.connect("changed", self.update_file_profile)
        self.__entry_file_wizard.connect("changed", self.update_file_wizard)
    # Callbacks
    
    # Should be merged callback based on a dict or whatever.
    def update_file_opt(self):
        profile_conf.options = self.__entry_file_opt.get_text()
    
    def update_file_profile(self):
        profile_conf.profile = self.__entry_file_wizard.get_text()
        
    def update_file_wizard(self):
        profile_conf.wizard = self.__entry_file_wizard.get_text()
        
        
    # API 
    def get_profile(self):
        return self.__entry_file_profile.get_text()
    def set_profile(self, profile):
        self.__entry_file_profile.set_text(profile)
    
    def get_wizard(self):
        return self.__entry_file_wizard.get_text()
    def set_wizard(self, wizard):
        self.__entry_file_wizard.set_text(wizard)
    
    def set_options(self, options):
        self.__entry_file_opt.set_text(options)
    def get_options(self):
        return self.__entry_file_opt.get_text()
    
    profile = property(get_profile, set_profile)
    wizard = property(get_wizard, set_wizard)
    options = property(get_options, set_options)

class Factory:
    def create(self, name):
        if name == "window":
            return ExposeWindow('Expose')
        elif name == "settings":
            return ExposeSettings()
        elif name == "profiles":
            return ExposeProfiles('Profiles')
