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

from umit.db.Utils import log_debug
from umit.db.Connection import ConnectDB
from umit.db.Retrieve import CompositeRetrieve

from umit.core.I18N import _

debug = log_debug('umit.db.Search')

change_text = (_("change"), _("changes"))
port_text = (_("port"), _("ports"), _("service"))
comparison = ("<", ">", "==", ">=", "<=", "!=")

def perform_comparison(ports, compare, decider):
    """
    Compare ports against decider using especified comparation.
    """
    decider = int(decider)

    # ports are numbered in ascendent order.
    for port in ports:
        if compare == '>':
            if decider <= port[0]:
                return True
        if compare == '<':
            if decider < port[0]:
                return False
            elif decider > port[0]:
                return True
        if compare == '!=':
            if port[0] == decider:
                return False
        if compare == '==':
            if port[0] == decider:
                return True
        if compare == '>=':
            if port[0] >= decider:
                return True
        if compare == '<=':
            if decider < port[0]:
                if decider == port[0]:
                    return True
                return False
            return True

    if compare == '!=':
        return True

    return False


class SearchDB(ConnectDB, CompositeRetrieve):
    """
    Performs search on database.
    """
    search_meths = {"ports": "port_search", "changes": "changes_search"}


    def __init__(self, db):
        """
        Expects an umit database.
        """
        ConnectDB.__init__(self, db)
        CompositeRetrieve.__init__(self, self.conn, self.cursor)


    def search(self, host_id, query):
        """
        Convenience method. Performs searches for host_id.
        """
        if not query:
            return
        likely_category = query.split()[0]
        meth = None

        if likely_category in port_text:
            meth = self.search_meths["ports"]
        elif likely_category in change_text:
            meth = self.search_meths["changes"]

        if meth:
            res = getattr(self, meth)(host_id, query)
            if res:
                return res

        if self.search_for_hostname_for_host_from_db(host_id, query):
            return _("Hostname")

        if self.search_for_osmatch_for_host_from_db(host_id, query):
            return _("OS Match")

        if self.search_for_osclasses_for_host_from_db(host_id, query):
            return _("OS Classes")

        if self.search_for_mac_for_host_from_db(host_id, query):
            return _("MAC")

        if self.search_for_fingerprint_for_host_from_db(host_id, query):
            return _("Fingerprint")

        # if I'm still here, no results were returned. I will try to do a
        # port search then. Situation where this may happen:
        # - Person searching doesnt know about port search syntax, so it does
        #   a search like "mysql". The correct way would be: "service mysql".
        res = self.port_search(host_id, port_text[0] + " " + query)
        if res:
            return res


    def port_search(self, host_id, query):
        """
        Search for ports for host_id.
        """
        debug("Searching under Ports for %s for host_id %d..", query, host_id)
        # a port search query is expected to be something like:
        #  <port_text> <comparison OR Nothing> <something>

        query = query.split()
        if len(query) < 2 or (not query[0] in port_text):
            # bad syntax for port search
            return None

        looking_for = query[1]
        compare = None
        if len(query) == 3:
            # assuming second item is a comparion item
            if query[1] in comparison:
                # valid comparison especified
                compare = query[1]

            looking_for = query[2]


        results = ''
        portnumber = False

        try:
            int(looking_for)
            portnumber = True
        except ValueError:
            portnumber = False
            # will perform porttext search

        if portnumber:
            # search for port with number in looking_for
            if compare:
                self.cursor.execute("SELECT port.portid FROM port "
                    "JOIN _host_port ON (_host_port.fk_port=port.pk) "
                    "WHERE _host_port.fk_host=?", (host_id, ))
                search = self.cursor.fetchall()
                search = perform_comparison(search, compare, looking_for)

            else:

                self.cursor.execute("SELECT port.portid FROM port "
                    "JOIN _host_port ON (_host_port.fk_port=port.pk) "
                    "WHERE _host_port.fk_host=? AND port.portid LIKE ?",
                        (host_id, '%'+looking_for+'%'))
                search = self.cursor.fetchall()

            if search:
                results = _("Port number")
        else:
            # search for some text
            pdata = self.get_portid_and_fks_for_host_from_db(host_id)
            for pd in pdata:
                res = self._search_port_text_for_pdata(pd[1], looking_for)
                if res:
                    results = res
                    break

        return results


    def _search_port_text_for_pdata(self, service_info_id, query):
        """
        """
        bquery = '%' + query + '%'

        # Im supposing service name is more likely to be queried than
        # service info. Also, there is just one field to compare against query
        # in service_name.
        service_name = self.cursor.execute("SELECT name FROM service_name "
            "JOIN service_info ON "
            "(service_info.fk_service_name=service_name.pk) "
            "WHERE service_info.pk=? AND name LIKE ?", (service_info_id,
                bquery)).fetchall()
        if service_name:
            return _("Service name")

        service_info = self.cursor.execute("SELECT product, version, "
            "extrainfo FROM service_info WHERE service_info.pk=? AND "
            "(product LIKE ? OR version LIKE ? or extrainfo LIKE ?)",
                (service_info_id, bquery, bquery, bquery)).fetchall()
        if service_info:
            return _("Service info")


    def changes_search(self, host_id, query):
        """
        Search in _inventory_changes for something like query for host_id.
        """
        debug("Searching under Inventory changes for %s for host_id %d..",
                query, host_id)

        query = query.split()
        if len(query) < 2 or (not query[0] in change_text):
            # bad syntax for changes search
            return None

        address_id = self.get_address_pk_for_host_from_db(host_id)

        looking_for = query[1:]

        bquery = '%' + ' '.join(looking_for) + '%'

        self.cursor.execute("SELECT pk FROM _inventory_changes "
            "WHERE fk_address=? AND short_description LIKE ?", (address_id,
                bquery))
        results = self.cursor.fetchall()

        if results:
            return _("Changes")


    def search_for_hostname_for_host_from_db(self, host_id, query):
        """
        Search for hostnames like query for host_id.
        """
        debug("Searching for hostname %s for host_id %d", query, host_id)

        hostname = self.cursor.execute("SELECT hostname.name FROM hostname "
            "JOIN _host_hostname ON (_host_hostname.fk_hostname=hostname.pk) "
            "WHERE _host_hostname.fk_host=? AND hostname.name LIKE ?",
                (host_id, '%' + query + '%')).fetchall()

        if hostname:
            return True


    def search_for_osmatch_for_host_from_db(self, host_id, query):
        """
        Search for osmatch like query for host_id.
        """
        debug("Searching under OS Match for %s for host_id %d..",
                query, host_id)

        match = self.cursor.execute("SELECT name FROM osmatch "
            "WHERE fk_host=? AND name LIKE ?", (host_id,
                '%' + query + '%')).fetchall()
        if match:
            return True



    def search_for_osclasses_for_host_from_db(self, host_id, query):
        """
        Search for osclasses like query for host_id.
        """
        debug("Searching under OS Classes for %s for hots_id %d",
                query, host_id)

        bquery = '%' + query + '%'

        classes = self.cursor.execute("SELECT osclass.accuracy, osgen.gen, "
            "osfamily.family, osvendor.vendor, ostype.type FROM osclass "
            "JOIN osgen ON (osclass.fk_osgen = osgen.pk) "
            "JOIN osfamily ON (osclass.fk_osfamily = osfamily.pk) "
            "JOIN osvendor ON (osclass.fk_osvendor = osvendor.pk) "
            "JOIN ostype ON (osclass.fk_ostype = ostype.pk) "
            "WHERE osclass.fk_host = ? AND (osgen.gen LIKE ? OR "
            "osfamily.family LIKE ? OR osvendor.vendor LIKE ? OR "
            "ostype.type LIKE ?)", (host_id, bquery, bquery, bquery,
                bquery)).fetchall()

        if classes:
            return True


    def search_for_mac_for_host_from_db(self, host_id, query):
        """
        Search for MAC like query for host_id.
        """
        debug("Searching MAC address like %s for host_id %d", query, host_id)

        fk_address = self.cursor.execute("SELECT fk_address "
            "FROM _host_address WHERE fk_host = ?", (host_id, )).fetchall()

        mac = None
        for fk in fk_address:
            mac = self.cursor.execute("SELECT address FROM address "
                "WHERE type = 'mac' AND pk = ? AND address LIKE ?", (fk[0],
                    '%' + query + '%')).fetchone()
            if mac:
                return True


    def search_for_fingerprint_for_host_from_db(self, host_id, query):
        """
        Search for query in fingerprint table for host_id.
        """
        debug("Searching for Fingerprint info like %s for host_id %d",
                query, host_id)

        bquery = '%' + query + '%'
        self.cursor.execute("SELECT tcp_sequence_class, "
            "tcp_ts_sequence_class, ip_id_sequence_class "
            "FROM fingerprint_info WHERE fk_host=? AND "
            "(tcp_sequence_class LIKE ? OR tcp_ts_sequence_class LIKE ? OR "
            "ip_id_sequence_class LIKE ?)", (host_id, bquery, bquery, bquery))
        fp = self.cursor.fetchall()
        if fp:
            return True
