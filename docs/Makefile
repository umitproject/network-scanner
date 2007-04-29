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
#
# 30 April 2007 -- More generic structure
#                  Maxim Gavrilov <lovelymax@gmail.com>

VPATH = comparing_results \
	profile_editor \
	nse_facilitator \
	scanning \
	searching \
	wizard

OUTDIR = .
XSL = /usr/share/xml/docbook/stylesheet/nwalsh/html/docbook.xsl

OUTPUTS = $(addsuffix .html, $(VPATH))

%.html : %.xml
	xsltproc -o $(OUTDIR)/$@ $(XSL) $<

all: create-dir $(OUTPUTS)

create-dir:
	@mkdir -p $(OUTDIR)

clean:
	@rm -f $(OUTDIR)/*.html

