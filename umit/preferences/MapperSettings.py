# Copyright (C) 2010 Adriano Monteiro Marques.
#
# Author: Diogo Ricardo Marques Pinheiro <diogormpinheiro@gmail.com>
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
from higwidgets.hignotebooks import HIGNotebook
from higwidgets.higtables import HIGTable
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higboxes import  hig_box_space_holder, HIGScrolledWindow
from umit.preferences.FramesHIG import *

from umit.gui.radialnet.ControlWidget import ControlVariableWidget, OPTIONS
from umit.gui.radialnet.RadialNet import INTERPOLATION_CARTESIAN, INTERPOLATION_POLAR
from umit.gui.radialnet.RadialNet import LAYOUT_SYMMETRIC, LAYOUT_WEIGHTED
from umit.preferences.conf.MapperConf import mapper_conf
from umit.core.I18N import _



class MapperSettings(TabBox):
    
    def __init__(self, name):
        TabBox.__init__(self, name)
                
    def _create_widgets(self):
        """
        Design all
        """
        self.create_interpolation()
        self.create_layout()
        self.create_view()
        self.pack_start(self._box_interpolation, False, False)
        self.pack_start(self._box_layout, False, False)
        self.pack_start(self._box_view, False, False)
        
    def create_interpolation(self):
        vbox = HIGVBox()
        self._box_interpolation = HIGFrame('Interpolation')
        self._box_interpolation.add(vbox)
        self.__cartesian_radio = gtk.RadioButton(None, 'Cartesian')
        self.__polar_radio = gtk.RadioButton(self.__cartesian_radio, 'Polar')
        self.__cartesian_radio.connect('toggled',
                                       self.__change_system,
                                       INTERPOLATION_CARTESIAN)
        self.__polar_radio.connect('toggled',
                                   self.__change_system,
                                   INTERPOLATION_POLAR)

        self.__system_box = HIGHBox()
        self.__system_box._pack_noexpand_nofill(self.__polar_radio)
        self.__system_box._pack_noexpand_nofill(self.__cartesian_radio)

        self.__frames_box = HIGHBox()
        self.__frames_label = gtk.Label('Frames')
        self.__frames_label.set_alignment(0.0, 0.5)
        self.__frames = gtk.Adjustment(mapper_conf.frames,
                                       1,
                                       1000,
                                       1)
        self.__frames.connect('value_changed', self.__change_frames)
        self.__frames_spin = gtk.SpinButton(self.__frames)
        self.__frames_box._pack_noexpand_nofill(self.__frames_label)
        self.__frames_box._pack_noexpand_nofill(self.__frames_spin)

        vbox._pack_noexpand_nofill(self.__frames_box)
        vbox._pack_noexpand_nofill(self.__system_box)
        
        
    def __change_system(self, widget, value):
        mapper_conf.interpolation = value                
                
    def __change_frames(self, widget):
        mapper_conf.frames = int(self.__frames_spin.get_value())
        
        
    def create_layout(self):
        hbox = HIGHBox()
        self._box_layout = HIGFrame('Layout')
        self._box_layout.add(hbox)
        
        self.__layout = gtk.combo_box_new_text()
        self.__layout.append_text('Symmetric')
        self.__layout.append_text('Weighted')
        self.__layout.set_active(mapper_conf.layout)
        self.__layout.connect('changed', self.__change_layout)

        hbox._pack_noexpand_nofill(self.__layout)
        
    def __change_layout(self, widget):
        mapper_conf.layout = self.__layout.get_active()
        
        
    def create_view(self):
        vbox = HIGVBox()
        self._box_view = HIGFrame('View')
        self._box_view.add(vbox)
        
        self.__zoom = ControlVariableWidget('Zoom',
                                               self.__get_zoom,
                                               self.__set_zoom,
                                               1)

        self.__ring_gap = ControlVariableWidget('Ring gap',
                                               self.__get_ring,
                                               self.__set_ring,
                                               1)

        self.__label = gtk.Label('Lower ring gap')
        self.__label.set_alignment(0.0, 0.5)
        self.__adjustment = gtk.Adjustment(mapper_conf.lower_ring,
                                           0,
                                           50,
                                           1)
        self.__lring_spin = gtk.SpinButton(self.__adjustment)
        self.__lring_spin.connect('value_changed', self.__change_lower)

        self.__lower_hbox = HIGHBox()
        self.__lower_hbox._pack_noexpand_nofill(self.__label)
        self.__lower_hbox._pack_noexpand_nofill(self.__lring_spin)
        
        self.create_view_options()
        vbox._pack_noexpand_nofill(self.scroll_window)
        vbox._pack_noexpand_nofill(self.__zoom)
        vbox._pack_noexpand_nofill(self.__ring_gap)
        vbox._pack_noexpand_nofill(self.__lower_hbox)
        
    def __change_lower(self, widget):
        mapper_conf.frames = int(self.__lring_spin.get_value())
        
    def __set_zoom(self, zoom):
        if float(zoom) >= 1:
            mapper_conf.zoom = float(zoom) / 100.0
        
    def __get_zoom(self):
        return int(round(mapper_conf.zoom * 100))
    
    def __set_ring(self, value):
        mapper_conf.ring = value
        
    def __get_ring(self):
        return mapper_conf.ring
    
    
    def create_view_options(self):
        self.views_enabled = []
        self.scroll_window = HIGScrolledWindow()

        self.scroll_window.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_ALWAYS)
        self.scroll_window.set_shadow_type(gtk.SHADOW_NONE)

        self.__liststore = gtk.ListStore(gobject.TYPE_BOOLEAN,
                                         gobject.TYPE_STRING)

        self.__liststore.append([None, OPTIONS[0]])
        self.__liststore.append([None, OPTIONS[1]])
        self.__liststore.append([None, OPTIONS[2]])
        self.__liststore.append([None, OPTIONS[3]])
        self.__liststore.append([None, OPTIONS[4]])
        self.__liststore.append([None, OPTIONS[5]])
        self.__liststore.append([None, OPTIONS[6]])

        self.__cell_toggle = gtk.CellRendererToggle()
        self.__cell_toggle.set_property('activatable', True)
        self.__cell_toggle.connect('toggled',
                                   self.__change_option,
                                   self.__liststore)

        self.__column_toggle = gtk.TreeViewColumn('', self.__cell_toggle)
        self.__column_toggle.add_attribute(self.__cell_toggle, 'active', 0)

        self.__cell_text = gtk.CellRendererText()

        self.__column_text = gtk.TreeViewColumn('Enable',
                                                self.__cell_text,
                                                text=1)

        self.__treeview = gtk.TreeView(self.__liststore)
        self.__treeview.set_enable_search(True)
        self.__treeview.set_search_column(1)
        self.__treeview.append_column(self.__column_toggle)
        self.__treeview.append_column(self.__column_text)

        self.scroll_window.add_with_viewport(self.__treeview)
        
        self.__update_options()
        
        
    def __update_options(self):
        """
        """
        model = self.__liststore

        model[OPTIONS.index('address')][0] = 'address' in mapper_conf.view
        model[OPTIONS.index('hostname')][0] = 'hostname' in mapper_conf.view
        model[OPTIONS.index('icon')][0] = 'icon' in mapper_conf.view
        model[OPTIONS.index('latency')][0] = 'latency' in mapper_conf.view
        model[OPTIONS.index('ring')][0] = 'ring' in mapper_conf.view
        model[OPTIONS.index('region')][0] = 'region' in mapper_conf.view
        model[OPTIONS.index('slow in/out')][0] = 'slow' in mapper_conf.view

        return True


    def __change_option(self, cell, option, model):
        """
        """
        option = int(option)
        model[option][0] = not model[option][0]
        
        if OPTIONS[option] == 'address':
            if model[option][0]:
                self.views_enabled.append('address')
            else:
                self.views_enabled.remove('address')

        elif OPTIONS[option] == 'hostname':
            if model[option][0]:
                self.views_enabled.append('hostname')
            else:
                self.views_enabled.remove('hostname')

        elif OPTIONS[option] == 'icon':
            if model[option][0]:
                self.views_enabled.append('icon')
            else:
                self.views_enabled.remove('icon')

        elif OPTIONS[option] == 'latency':
            if model[option][0]:
                self.views_enabled.append('latency')
            else:
                self.views_enabled.remove('latency')

        elif OPTIONS[option] == 'ring':
            if model[option][0]:
                self.views_enabled.append('ring')
            else:
                self.views_enabled.remove('ring')

        elif OPTIONS[option] == 'region':
            if model[option][0]:
                self.views_enabled.append('region')
            else:
                self.views_enabled.remove('region')

        elif OPTIONS[option] == 'slow in/out':
            if model[option][0]:
                self.views_enabled.append('slow')
            else:
                self.views_enabled.remove('slow')
                
        mapper_conf.view = self.views_enabled
