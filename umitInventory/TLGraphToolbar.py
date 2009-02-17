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

"""
Timeline graph toolbar.
"""

import gtk
import gobject

from umitCore.I18N import _
from umitCore.UmitLogging import log

from umitInventory.TLBase import view_mode
from umitInventory.TLBase import view_kind
from umitInventory.TLBase import view_mode_order
from umitInventory.TLBase import view_kind_order
from umitInventory.TLGraphPreferences import GraphPreferences
from umitInventory.RefreshDialog import custom_refresh

REFRESH = [60, 60 * 5, 60 * 60, -1]
REFRESH_MODEL = (
    _("Refresh Now"), _("Refresh Enabled"),
    (_("Refresh Every minute"), REFRESH[0]),
    (_("Refresh Every 5 minutes"), REFRESH[1]),
    (_("Refresh Every hour"), REFRESH[2]),
    (_("Custom"), REFRESH[3])
    )

class GraphControllerTB(gtk.Toolbar):
    """
    Builds a Toolbar for controlling Interactive Timeline Graph.
    """

    def __init__(self, daddy, connector, graph_mode=None, graph_kind=None):
        gtk.Toolbar.__init__(self)

        self.daddy = daddy
        self.connector = connector
        self.refresher = -1
        self.timeout = REFRESH_MODEL[3][1] # default to 5 minutes
        self.indxrefresh = 3
        self.tooltips = gtk.Tooltips()

        self._queue_graph_refresh(None, self.timeout, self.indxrefresh)

        index = (i for i in xrange(7))

        self.insert(self.viewing_mode(graph_mode), index.next())
        self.insert(self.viewing_kind(graph_kind), index.next())
        self.insert(self.graph_kind(), index.next())
        self.insert(self.visibility(), index.next())
        self.insert(self.graph_pref(), index.next())
        self.insert(gtk.SeparatorToolItem(), index.next())
        self.insert(self.graph_refresh(), index.next())


    def packed(self, *widgets):
        """
        Pack widgets in a gtk.HBox and returns a gtk.ToolItem
        """
        tbox = gtk.HBox()
        for w in widgets:
            tbox.pack_start(w, False, False, 0)

        titem = gtk.ToolItem()
        titem.add(tbox)

        return titem


    def viewing_mode(self, omode=None):
        """
        Setup combobox for managing viewing modes.
        """
        self.viewmode = gtk.combo_box_new_text()

        for mode in view_mode_order:
            self.viewmode.append_text(view_mode[mode])

        if omode:
            option = view_mode_order.index(omode)
        else:
            option = 0

        self.viewmode.set_active(option)

        self.viewmode.connect('changed', self._change_graph_viewmode)

        return self.packed(self.viewmode)

    
    def viewing_kind(self, okind=None):
        """
        Combobox that displays possible ways on how graph may grab changes.
        """
        self.evtsgraph = gtk.combo_box_new_text()
        self.evtsgraph.append_text(_("Select visualization"))

        for kind in view_kind_order:
            self.evtsgraph.append_text(view_kind[kind])

        if okind:
            option = view_kind_order.index(okind) + 1
        else:
            option = 0

        self.evtsgraph.set_active(option)

        self.evtsgraph.connect('changed', self._change_graph_viewkind)

        return self.packed(self.evtsgraph)


    def graph_kind(self):
        """
        Combobox for setting graph kind. Right now there is only line graph
        and area graph.
        """
        modes = _("Line Graph"), _("Area Graph")
        self.cbgraphs = gtk.combo_box_new_text()
        self.cbgraphs.append_text(_("Select a graph style"))

        for mode in modes:
            self.cbgraphs.append_text(mode)

        self.cbgraphs.set_active(1)
        self.cbgraphs.connect('changed', self._change_graph_kind)

        return self.packed(self.cbgraphs)


    def visibility(self):
        """
        Control for hiding/showing graph.
        """
        modes = _("Visible"), _("Hidden")
        self.visibility = gtk.combo_box_new_text()
        self.visibility.append_text(_("Graph visibility"))

        for mode in modes:
            self.visibility.append_text(mode)

        self.visibility.set_active(1)
        self.visibility.connect('changed', self._change_graph_visibility)

        return self.packed(self.visibility)


    def graph_pref(self):
        """
        Button for opening Graph Preferences window.
        """
        self.btn_gpref = gtk.Button(stock=gtk.STOCK_EDIT)
        self.sched_name_edit = gtk.Button(stock=gtk.STOCK_EDIT)
        # get label widget to change default label text "Edit" to
        # "Graph Preferences"
        blbl_box = self.btn_gpref.get_children()[0].get_children()[0]
        blbl = blbl_box.get_children()[1]
        blbl.set_text(_("Graph Preferences"))

        self.btn_gpref.connect('clicked', self._open_graph_pref)
        self.btn_gpref.show()

        self.tooltips.set_tip(self.btn_gpref, _("Edit Graph Preferences"))

        return self.packed(self.btn_gpref)


    def graph_refresh(self):
        """
        Control graph refreshing.
        """
        def where_to_popup(menu, button):
            """
            Calculates position to popup menu.
            """
            winx, winy = self.window.get_position()

            btn_alloc = button.get_allocation()
            btnx, btny = (btn_alloc[0], btn_alloc[1] + btn_alloc[3])

            return (winx + btnx, winy + btny, True)


        def popup_refresh_menu(widget):
            """
            Popup a menu for controlling graph refresh options.
            """
            pmenu = gtk.Menu()

            radiogroup = gtk.RadioMenuItem(None, REFRESH_MODEL[3][0])
            if self.indxrefresh == 3:
                radiogroup.set_active(True)
            radiogroup.connect('toggled', self._queue_graph_refresh,
                REFRESH_MODEL[3][1], 3)

            for indx, item in enumerate(REFRESH_MODEL):
                if indx == 0: # refresh now
                    submenu_item = gtk.MenuItem(item)
                    submenu_item.connect('activate', self._graph_refresh)

                    pmenu.add(submenu_item)
                    pmenu.add(gtk.SeparatorMenuItem())

                elif indx == 1: # refresh enabled/disabled
                    submenu_item = gtk.CheckMenuItem(item)

                    if self.refresher == -1:
                        submenu_item.set_active(False)
                    else:
                        submenu_item.set_active(True)

                    submenu_item.connect('activate', self._graph_refresh_state,
                        pmenu)


                    pmenu.add(submenu_item)
                    pmenu.add(gtk.SeparatorMenuItem())

                elif indx == 3: # refresh every 5 minutes, radio group
                    # entry has been created earlier, just add it
                    pmenu.add(radiogroup)

                else: # other radio buttons
                    radio = gtk.RadioMenuItem(radiogroup, item[0])
                    if self.indxrefresh == indx:
                        radio.set_active(True)

                    if indx == len(REFRESH_MODEL) - 1: # custom refresh
                        radio.connect('button-press-event',
                            self._change_custom_refresh, item[1], indx)

                    radio.connect('toggled', self._queue_graph_refresh,
                        item[1], indx)
                    pmenu.add(radio)

            pmenu.show_all()
            pmenu.popup(None, None, where_to_popup, 1, 0, widget)


        refresh_btn = gtk.Button()
        refresh_btn.set_relief(gtk.RELIEF_NONE)
        self.tooltips.set_tip(refresh_btn, _("Graph Refresh"))

        img = gtk.Image()
        img.set_from_stock(gtk.STOCK_REFRESH, gtk.ICON_SIZE_BUTTON)
        box = gtk.HBox()
        box.pack_start(img, False, False, 0)
        box.pack_end(gtk.Arrow(gtk.ARROW_DOWN, gtk.SHADOW_OUT), False, False, 0)
        refresh_btn.add(box)
        refresh_btn.connect('clicked', popup_refresh_menu)

        return self.packed(refresh_btn)


    def update_graph(self):
        """
        Update graph after setting new options for it.
        """
        self.daddy.setup_new_graph()


    def _change_graph_viewmode(self, event):
        """
        Set new viewing mode.
        """
        mode = view_mode_order[event.get_active()]
        kind = self.evtsgraph.get_active()

        if kind == 1:
            self.connector.emit('data-changed', mode, 'sum')
        elif kind == 2:
            self.connector.emit('data-changed', mode, 'category')


    def _change_graph_viewkind(self, event):
        """
        Changing how graph displays events will result in grabbing events in
        a different way.
        """
        active = event.get_active()
        if active: # Didnt select "Select visualization"
            mode = view_mode_order[self.viewmode.get_active()]

            if active == 1:
                self.connector.emit('data-changed', mode, 'sum')
            elif active == 2:
                self.connector.emit('data-changed', mode, 'category')


    def _change_graph_kind(self, event):
        """
        Set new graph kind.
        """
        active = event.get_active()
        if active: # Didnt select "Select a graph style"
            setattr(self.daddy, "graph_type", active-1)


    def _change_graph_visibility(self, event):
        """
        Change graph visibility.
        """
        status = event.get_active()
        if status:
            if status == 1:
                self.connector.emit('graph-show', True)
            elif status == 2:
                self.connector.emit('graph-show', False)


    def _open_graph_pref(self, event):
        """
        Open Graph Preferences window.
        """
        w = GraphPreferences(self)
        w.show_all()


    def _graph_refresh(self, event):
        """
        Perform graph refresh now.
        """
        log.info(">>> TLGraph being refreshed!")
        self.connector.emit('data-changed', None, None)

        return True


    def _graph_refresh_state(self, event, submenu):
        """
        Change graph refresh to enabled/disabled.
        """
        if not event.get_active(): # disable timer
            if self.refresher != -1:
                gobject.source_remove(self.refresher)
                self.refresher = -1

        else: # enable timer, get current selection
            for indx, child in enumerate(submenu.get_children()[4:]):
                if child.get_active():
                    self._queue_graph_refresh(None, REFRESH[indx], indx + 2)
                    break


    def _change_custom_refresh(self, event, what, what2, rindx):
        """
        Change Custom refresh settings.
        This is used when user clicks on 'Custom' but it is already selected,
        so signal toggled isn't activated, instead, we handle
        button-press-event so it opens dialog for changing custom minutes.
        """
        if not event.get_active():
            return

        else:
            self.indxrefresh = rindx
            ret = custom_refresh(self.timeout/60)
            if ret:
                self.timeout = ret * 60

        if self.timeout < 1:
            return

        if self.refresher != -1:
            # remove previous timer
            gobject.source_remove(self.refresher)

        self.refresher = gobject.timeout_add(self.timeout * 1000,
            self._graph_refresh, None)


    def _queue_graph_refresh(self, event, time, rindx):
        """
        Perform graph refresh after some time.
        """
        self.indxrefresh = rindx
        
        if self.refresher != -1:
            # remove previous timer
            gobject.source_remove(self.refresher)
            self.refresher = -1

        if time == -1:
            if type(event.__class__) != type(type):
                # Custom was toggled/activated or deactivated
                if event.get_active():
                    ret = custom_refresh(self.timeout/60)
                    if ret:
                        self.timeout = ret * 60
        else:
            self.timeout = time

        self.refresher = gobject.timeout_add(self.timeout * 1000,
            self._graph_refresh, None)


    def __set_graph_mode(self, mode):
        """
        Change graph mode.
        """
        getattr(self.daddy, mode)()


    def __set_graph_attr(self, (attr, value)):
        """
        Change some graph attribute.
        """
        setattr(self.daddy, attr, value)


    def graph_attr(self, attr):
        """
        Return some graph attribute.
        """
        return getattr(self.daddy, attr)


    # Properties
    change_graph_mode = property(fset=__set_graph_mode)
    change_graph_attr = property(fset=__set_graph_attr)
