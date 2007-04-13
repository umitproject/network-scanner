# Copyright (C) 2005 Insecure.Com LLC.
#
# Author: Adriano Monteiro Marques <py.adriano@gmail.com>
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


html:
	# Comparing Results article
	xsltproc --output comparing_results.html \
	  /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl \
	  comparing_results/comparing_results.xml

	# Profile Editor article
	xsltproc --output profile_editor.html \
	  /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl \
	  profile_editor/profile_editor.xml

	# Scanning article
	xsltproc --output scanning.html \
	  /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl \
	  scanning/scanning.xml

	# Searching article
	xsltproc --output searching.html \
	  /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl \
	  searching/searching.xml

	# Wizard article
	xsltproc --output wizard.html \
	  /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl \
	  wizard/wizard.xml
