# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Maxim Gavrilov <lovelymax@gmail.com>
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

"""
Module for manage downloadable NSE bases and scripts

DownloaderManager is singletone object for some caching support
"""

import urllib2

class DownloaderManager(object):
    """
    Provide downloading operations
    """
    def __init__(self):
        self.downloaded = {}
        self.proxies = None
        self.set_proxies({})
        self._initialized = True

    def set_proxies(self, proxies):
        """
        Set proxies settings
        """
        if self.proxies != proxies:
            self.proxies = proxies
            self.opener = urllib2.build_opener(urllib2.ProxyHandler(proxies))

    def get_proxies(self):
        """
        Get proxies settings
        """
        return self.proxies
    
    def download(self, url, cached = True):
        """
        Download specified url or returns it from cache if it's enabled
        """
        if cached and self.downloaded.has_key(url):
            return self.downloaded[url]
        try:
            f = self.opener.open(url)
            data = f.read()
            f.close()
            self.downloaded[url] = data
        except urllib2.HTTPError, e:
            print "%s:%s" % (url, str(e))
            return None
        return data
    
