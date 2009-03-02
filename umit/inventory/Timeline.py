# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import gtk

from umit.core.I18N import _

from umit.inventory.ChangesDiff import ChangesDiff
from umit.inventory.ChangesList import ChangesList

from umit.inventory.TLGraph import InteractiveGraph
from umit.inventory.TLConnector import Connector
from umit.inventory.TLBarDisplay import TLSelected
from umit.inventory.TLGraphToolbar import GraphControllerTB
from umit.inventory.TLToolbar import FilterBox
from umit.inventory.TLToolbar import TimeBox
from umit.inventory.TLChangesTree import TLChangesTree
from umit.inventory.TLBase import TLBase

class TLHolder(gtk.VBox):
    def __init__(self, inventory=None, hostaddr=None):
        """
        Load timeline for every inventory, or if especified, a single
        host in an inventory.
        """

        gtk.VBox.__init__(self)

        self.connector = Connector()
        self.base = TLBase(self.connector, inventory, hostaddr)

        # startup data
        line_filter, start, evts = self.base.grab_data()
        xlabel = self.base.xlabel
        glabel = self.base.title_by_graphmode()
        dlabel = self.base.descr_by_graphmode()

        # graph
        self.graph = InteractiveGraph(evts, start, x_label=xlabel,
            y_label=_('Number of events'), graph_label=glabel,
            descr_label=dlabel, vdiv_labels=self.base.labels,
            line_filter=line_filter, connector=self.connector)
        # graph toolbar
        self.graphtb = GraphControllerTB(self.graph, self.connector,
            self.base.graph_mode, self.base.graph_kind)
        # graph filter
        self.filterbtns = FilterBox(filter=line_filter,
            connector=self.connector)
        # graph date
        self.dateview = TimeBox(self.connector, self.base)
        # categories label
        self.viewing_lbl = gtk.Label(_("Viewing"))
        # tl selected, bar display
        self.tlsel = TLSelected(self.connector, self.base)
        # changes tree
        categories = self.base.get_categories()
        cnames = [value[1] for value in categories.values()]
        self.changestree = TLChangesTree(self.connector, self.base, cnames,
            inventory, hostaddr)
        # changes displaying
        self.changes_display = ChangesDiff(self.base)
        self.changes_list = ChangesList(self, self.base,
            self.changes_display, None, load_now=False)


        self.connector.connect('data-update', self._update_graph)
        self.connector.connect('filter-update', self._update_graph_filter)
        self.connector.connect('graph-show', self._update_graph_visibility)
        self.changestree.connect('data-update', self._changes_show)

        self.__layout()


    def _update_graph(self, obj, *args):
        """
        New graph data arrived.
        """
        line_filter, start, evts, labels, xlabel, glabel, dlabel = args

        # new graph data
        self.graph.start_pts_data = start
        self.graph.graph_data = evts

        # new line filter (or not)
        if [value[1] for value in line_filter.values()] != \
           [value[1] for value in self.graph.line_filter.values()]:
            # changed graph mode
            self.connector.emit('filter-update', line_filter)
            self.graph.line_filter = line_filter

        # find new max value
        self.graph.find_max_value()

        # update graph labels
        self.graph.xlabel = xlabel
        self.graph.graph_label = glabel
        self.graph.descr_label = dlabel
        self.graph.vdiv_labels = labels

        # do graph animation with new data
        self.graph.do_animation()


    def _update_graph_filter(self, obj, lfilter):
        """
        Sets a new line filter.
        """
        self.graph.line_filter = lfilter # set new filter
        self.graph.find_max_value() # find new max value
        self.graph.setup_new_graph() # redraw graph with new settings


    def _update_graph_visibility(self, obj, show):
        """
        Graph visibility updated, lets update controls visibility.
        """
        widgets = (self.graph, self.tlsel, self.filterbtns, self.viewing_lbl,
            self.dateview)

        if show:
            meth = "show"
        else:
            meth = "hide"

        for w in widgets:
            getattr(w, meth)()


    def _changes_show(self, obj, data_kind, content):
        """
        New selection (data) from ChangesTree arrived.
        """
        changesl = None
        data_range = self.base.sel_range

        if data_kind == "especific":
            changesl = {
                'data': content, 'data_built': False,
                'data_range': data_range
                }

        elif data_kind in ("category", "full"):
            changesl = {
                'data': content, 'data_built': True,
                'data_range': data_range
                }

        if changesl:
            # setup new data in ChangesList
            self.changes_list._set_data(**changesl)


    def __layout(self):
        """
        Layout widgets
        """
        filterbox = gtk.HBox()
        left_vbox = gtk.VBox()
        graph_hbox = gtk.HBox()
        main_hbox = gtk.HBox()
        main_hpaned = gtk.HPaned()
        changes_vpaned = gtk.VPaned()

        # filter
        filterbox.pack_start(self.dateview, False, False, 0)
        filterbox.pack_end(self.filterbtns, False, False, 0)
        filterbox.pack_end(self.viewing_lbl, False, False, 0)

        # graph and bar display
        graph_hbox.pack_start(self.graph, True, True, 3)
        graph_hbox.pack_start(self.tlsel, False, False, 3)

        # changestree
        left_vbox.pack_start(self.changestree, True, True, 0)

        # changes displaying
        changes_vpaned.add1(self.changes_list)
        changes_vpaned.add2(self.changes_display)

        main_hpaned.add1(left_vbox)
        main_hpaned.add2(changes_vpaned)

        main_hbox.pack_start(main_hpaned, True, True, 3)

        self.pack_start(self.graphtb, False, False, 0)
        self.pack_start(filterbox, False, False, 0)
        self.pack_start(graph_hbox, False, False, 3)
        self.pack_start(main_hbox, True, True, 3)

