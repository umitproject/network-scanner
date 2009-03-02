# -*- coding: utf-8 -*-
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

from umit.gui.radialnet.RadialNet import *
from umit.gui.radialnet.GraphBuilder import GraphBuilder
from umit.gui.radialnet.ControlWidget import ControlWidget, ControlFisheye
from umit.gui.radialnet.Toolbar import Toolbar

from higwidgets.higboxes import HIGVBox, HIGHBox

from umit.core.I18N import _


class ScanMapperPage(HIGVBox):
    def __init__(self):
        HIGVBox.__init__(self)
        self.__parser = None 
        self.__radialnet = None
        self.__created = False
        
    def create_widgets(self):
        if self.__created:
            self.__toolbar.enable_tools()
            self.update_graph()
            return

        self.set_spacing(0)
        self.__hbox = HIGHBox(spacing=0)
        
        
        # Create RadialNet
        self.__radialnet = RadialNet(LAYOUT_WEIGHTED)
        self.__radialnet.set_no_show_all(True)
        
        self.__radialnet.set_empty()
        self.update_graph()
        self.__radialnet.show()
        
        
        # Create Controlors
        

        self.__control = ControlWidget(self.__radialnet)
        self.__fisheye = ControlFisheye(self.__radialnet)
        self.__toolbar = Toolbar(self.__radialnet,
                                        self,
                                        self.__control,
                                        self.__fisheye)
        self.__toolbar.disable_tools()
        
        
        
        self.__hbox._pack_expand_fill(self.__radialnet)
        self.__hbox._pack_noexpand_nofill(self.__control)
        
        self._pack_noexpand_nofill(self.__toolbar)
        self._pack_expand_fill(self.__hbox)
        
        self.show_all()
        self.__created = True
    def update_graph(self):
        self.__graph = GraphBuilder()
        self.__graph.make(self.__parser)
        self.__radialnet.set_graph(self.__graph)
    def set_parse(self, parse):
        self.__parser = parse
        if self.__radialnet is not None:
            self.__radialnet.set_graph(self.__graph)
