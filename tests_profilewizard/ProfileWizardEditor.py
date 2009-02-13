#!/usr/bin/env python
# Copyright (C) 2007 Adriano Monteiro Marques <py.adriano@gmail.com>
#
# Author: Luis Bastiao Silva <luis.kop@gmail.com>
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


from gettext import gettext as _

import gtk

#HIG

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, HIGSpacer, hig_box_space_holder
from higwidgets.higexpanders import HIGExpander
from higwidgets.higlabels import HIGSectionLabel, HIGEntryLabel
from higwidgets.higscrollers import HIGScrolledWindow
from higwidgets.higtextviewers import HIGTextView
from higwidgets.higbuttons import HIGButton
from higwidgets.higtables import HIGTable
from higwidgets.higdialogs import HIGAlertDialog, HIGDialog




# This is my first tests with higwidgets

class ProfileWizardEditor(HIGWindow):
	def __init__(self):
		HIGWindow.__init__(self)
		self.set_title(_('Profile and Wizard Editor'))
		self.set_border_width(10)
		self.__create_mainwidgets()
		self.__expand_widgets()


def __create_mainwidgets(self):
		#Vertical BOX
		self.main_vbox = HIGVBox()
		self.set_position(gtk.WIN_POS_CENTER)
		self.widgets={}
	   
		self.__create_menubar()	
		#Create Profile tab editor
		self.notebook = gtk.Notebook()
		self.profile_vbox = HIGVBox()
		self.profile_info_vbox = HIGVBox()
	 
		self.profile_info_vbox2 = HIGVBox()

		self.profile_info_label = HIGSectionLabel(_('Profile Information'))
	def __craeate_ui_manager(self):
		self.ui_manager = gtk.UIManager()
		self.ui_options = """
		<menubar>
			<menu action='Manage'>
				<menuitem action='Abrir'/>
				<separator />
			</menu>
		<menubar>
		"""
		

	
	def __create_menubar(self):
		self.menubar = self.ui_manager.
	def __expand_widgets(self):
		self.add(self.main_vbox);
		
		self.main_vbox._pack_expand_fill(self.notebook)
		self.profile_info_vbox._pack_noexpand_nofill(self.profile_info_label)
		
		table = HIGTable()
		self.profile_info_vbox._pack_noexpand_nofill(HIGSpacer(table))
		self.notebook.append_page(self.profile_info_vbox, gtk.Label(_('Profile')))
		
		self.notebook.append_page(self.profile_info_vbox2, gtk.Label(_('Pro')))
if __name__ == '__main__':
	p = ProfileWizardEditor()
	p.show_all()
	gtk.main()
