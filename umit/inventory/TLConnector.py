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

import gobject

class Connector(gobject.GObject):
    __gsignals__ = {
        # graph-show is used at Timeline to hide/show graph and filter.
        'graph_show': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (bool, )),

        # line filter updates. Timeline handles this signals and updates
        # TLGraph accordingly.
        'filter_update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
            (object, )),

        # TLGraph emits this signal when a new selection is done, TLBase
        # grabs it, handles it and stores selected timerange.
        'selection_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
            (object, )),

        # After TLBase defines the timerange for selection, it emits
        # a selection-update, meaning that TLBarDisplay now may use this
        # range to grab data for display statistics. It is also used
        # at TLChangesTree to updates changes listing.
        'selection_update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
            (object, object)),

        # data-changed is used as a way to tell that graph needs a redraw,
        # it is used at TLGraphToolbar to update graph mode and kind.
        # TLBase handles this signal and updates everything needed.
        'data_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
            (str, str)),
        
        # After handling data-changed at TLBase, it emits a new signal:
        # data_update with new data. Timeline catches this signal and
        # requests graph update.
        'data_update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE,
            (object, object, object, object, object, object, object)),
        
        # date-changed is used at TLToolBar to update ranges and labels.
        # TLBase emits this after emitting data-update.
        'date_changed': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, ()),
        
        # date-update is emitted from TLToolBar when a date update is
        # requested, Timeline grabs it, then updates date based on current
        # mode and then emits a date-update.
        'date_update': (gobject.SIGNAL_RUN_FIRST, gobject.TYPE_NONE, (int, ))
    }

    def __init__(self):
        self.__gobject_init__()


gobject.type_register(Connector)
