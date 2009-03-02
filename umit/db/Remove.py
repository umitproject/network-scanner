# Copyright (C) 2007 Adriano Monteiro Marques
#
# Author:  Guilherme Polo <ggpolo@gmail.com>
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

from datetime import datetime, timedelta

from umit.db.Utils import log_debug
from umit.db.Connection import ConnectDB
from umit.db.Retrieve import CompositeRetrieve

debug = log_debug('umit.db.Remove')

class ScanRemover(ConnectDB, CompositeRetrieve):
    """
    Removes scans from database.
    """

    def __init__(self, database):
        ConnectDB.__init__(self, database)
        CompositeRetrieve.__init__(self, self.conn, self.cursor)


    def remove_scan(self, fk_scan):
        """
        Removes a scan from database.
        """
        # hosts associated with this scan
        hosts_ids = self.get_hosts_id_for_scan_from_db(fk_scan)
        hosts_ids = [h_id[0] for h_id in hosts_ids]

        # remove host data associated with this scan
        for h_id in hosts_ids:
            self._remove_fingerprint_info(h_id)
            self._remove_host_hostname(h_id)
            self._remove_host_address(h_id)
            self._remove_osmatch(h_id)
            self._remove_osclasses(h_id)
            self._remove_extraports(h_id)
            self._remove_portused(h_id)
            self._remove_hostport(h_id)
            self._remove_host(h_id)

        # remove scan data associated with this scan
        self._remove_scaninfo(fk_scan)
        self._remove_inventoryscan(fk_scan)
        self._remove_scan(fk_scan)

        # make changes come true!
        self.conn.commit()


    def remove_old_umit_scans(self, older_than=None):
        """
        Remove scans that aren't in Inventory that are older than N days.
        """
        if older_than < 1:
            # passed invalid older_than value
            return

        old_data_date = datetime.now() - timedelta(days=older_than)

        # get scans from table scan older than especified days
        scans_ids = self.cursor.execute("SELECT pk FROM scan WHERE finish <= ?",
                                        (old_data_date, )).fetchall()
        scans_ids = set([s_id[0] for s_id in scans_ids])

        # get fk_scans from table _inventory_scan older than especified days
        inventory_scans_ids = self.cursor.execute("SELECT fk_scan FROM "
            "_inventory_scan JOIN scan ON (_inventory_scan.fk_scan=scan.pk) "
            "WHERE scan.finish <= ?", (old_data_date, )).fetchall()
        inventory_scans_ids = set([i_id[0] for i_id in inventory_scans_ids])

        # get scans that will be removed
        to_remove = scans_ids.difference(inventory_scans_ids)

        if not to_remove:
            # nothing to do
            return

        debug("Removing UMIT scans older than %d days "
            "from database..", older_than)

        # remove scans
        for scan_id in to_remove:
            self.remove_scan(scan_id)

        debug("Removal completed")


    def remove_old_inventory_scans(self, older_than=None):
        """
        Remove Inventory scans that are older than N days. N >= 1
        """
        if older_than < 1:
            # passed invalid older_than value
            return

        old_data_date = datetime.now() - timedelta(days=older_than)

        # get scans that will be removed
        scans_ids = self.cursor.execute("SELECT fk_scan FROM _inventory_scan "
            "JOIN scan ON (_inventory_scan.fk_scan=scan.pk) "
            "WHERE scan.finish <= ?", (old_data_date, )).fetchall()
        scans_ids = [s_id[0] for s_id in scans_ids]

        if not scans_ids:
            # nothing to do
            return

        debug("Removing Inventory scans older than %d days "
            "from database..", older_than)

        # remove scans
        for scan_id in scans_ids:
            self.remove_scan(scan_id)

        # get changes that will be removed
        changes_ids = self.cursor.execute("SELECT pk FROM _inventory_changes "
            "WHERE entry_date <= ?", (old_data_date, )).fetchall()
        changes_ids = [c_id[0] for c_id in changes_ids]

        for change_id in changes_ids:
            self._remove_inventory_change(change_id)

        self.conn.commit()
        
        debug("Removal completed")


    def _remove_fingerprint_info(self, fk_host):
        """
        Remove fingerprint_info associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM fingerprint_info WHERE fk_host=?",
            (fk_host, ))


    def _remove_host_hostname(self, fk_host):
        """
        Remove hostnames associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM _host_hostname WHERE fk_host=?",
            (fk_host, ))


    def _remove_host_address(self, fk_host):
        """
        Remove addresses associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM _host_address WHERE fk_host=?",
            (fk_host, ))


    def _remove_osmatch(self, fk_host):
        """
        Remove osmatch associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM osmatch WHERE fk_host=?", (fk_host, ))


    def _remove_osclasses(self, fk_host):
        """
        Remove osclasses associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM osclass WHERE fk_host=?", (fk_host, ))


    def _remove_extraports(self, fk_host):
        """
        Remove extraports associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM extraports WHERE fk_host=?",
            (fk_host, ))


    def _remove_portused(self, fk_host):
        """
        Remove portused associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM portused WHERE fk_host=?",
            (fk_host, ))


    def _remove_hostport(self, fk_host):
        """
        Remove ports associated with fk_host from database.
        """
        self.cursor.execute("DELETE FROM _host_port WHERE fk_host=?",
            (fk_host, ))


    def _remove_host(self, pk):
        """
        Remove host associated with pk from database.
        """
        self.cursor.execute("DELETE FROM host WHERE pk=?", (pk, ))


    def _remove_scaninfo(self, fk_scan):
        """
        Remove scaninfo associated with fk_scan from database.
        """
        self.cursor.execute("DELETE FROM scaninfo WHERE fk_scan=?", (fk_scan, ))


    def _remove_inventoryscan(self, fk_scan):
        """
        Remove inventory scans associated with fk_scan from database.
        """
        self.cursor.execute("DELETE FROM _inventory_scan WHERE fk_scan=?",
            (fk_scan, ))


    def _remove_scan(self, pk):
        """
        Remove scan associated with pk from database.
        """
        self.cursor.execute("DELETE FROM scan WHERE pk=?", (pk, ))


    def _remove_inventory_change(self, pk):
        """
        Remove inventory_change associated with pk from database.
        """
        self.cursor.execute("DELETE FROM _inventory_changes WHERE pk=?", (pk, ))


if __name__ == "__main__":
    # sample
    remover = ScanRemover("/home/polo/.umit/umitng.db")
    #remover = ScanRemover("../share/umit/config/umitng.db")
    remover.remove_old_inventory_scans(5)
    #remover.remove_old_umit_scans(120)
