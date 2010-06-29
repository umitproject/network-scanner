#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2008 Adriano Monteiro Marques
#
# Author: Gunjan Bansal<gunjanbansal000@gmail.com>
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




import sys
import os
import gtk,gobject


from umit.plugin.Engine import Plugin
from umit.plugin.Core import Core
from higwidgets.hignotebooks import HIGAnimatedTabLabel
from higwidgets.higtooltips import *

try:
	if(os.name!='posix'):
		raise Exception 
except:
	raise Exception("This Plugin is Only for Posix Systems\n")
	
_ = str

 

class NetPidPage(gtk.VBox):

	def __init__(self):
		gtk.VBox.__init__(self)
		self.create_ui()
		self.right_click_kill_pid=""
	
	def create_ui(self):
		
		sw = gtk.ScrolledWindow()
		sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		sw.set_shadow_type(gtk.SHADOW_ETCHED_IN)
		self.store = gtk.ListStore(str,str,str,str,gobject.TYPE_BOOLEAN)
		self.tree = gtk.TreeView(self.store)

		self.tree.append_column(gtk.TreeViewColumn('Command', gtk.CellRendererText(), text=0))
		self.tree.append_column(gtk.TreeViewColumn('Pid', gtk.CellRendererText(), text=1))
		self.tree.append_column(gtk.TreeViewColumn('User', gtk.CellRendererText(), text=2))
		self.tree.append_column(gtk.TreeViewColumn('Local Port', gtk.CellRendererText(), text=3))

		#Here the checking is required
		self.checkBox=gtk.CellRendererToggle()
		self.checkBox.set_property('activatable', True)
		self.checkBox.set_property('visible',True)
		self.checkBox.connect('toggled',self.col1_toggled_cb,self.store)
		self.killColumn = gtk.TreeViewColumn("KILL", self.checkBox)
		self.killColumn.add_attribute( self.checkBox, "active", 4)
		self.tree.append_column( self.killColumn )

		self.tree.set_search_column(3)#search using PID
		self.tree.set_enable_search(self.tree.get_enable_search())
		#add stuff to container sw
		sw.add(self.tree)

		self.tree.get_column(0).set_resizable(True)
		self.tree.get_column(1).set_resizable(True)
		self.tree.get_column(2).set_resizable(True)
		self.tree.get_column(3).set_resizable(True)
		self.tree.get_column(4).set_resizable(True)
	
		self.tree.get_column(0).set_expand(True)
		self.tree.get_column(1).set_expand(True)
		self.tree.get_column(2).set_expand(True)
		self.tree.get_column(3).set_expand(True)
		self.tree.get_column(4).set_expand(True)

		self.tree.set_reorderable(True)

		btn = gtk.Button(stock=gtk.STOCK_REFRESH)
		btn.connect('clicked', self.__on_refresh)
		btnKill=gtk.Button(stock=gtk.STOCK_CLOSE)
                btnKill.set_label("KILL")
		btnKill.connect('clicked',self.__on_close)
		
		#add stuff to container btnBox
		btnBox = gtk.HButtonBox()
		btnBox.set_layout(gtk.BUTTONBOX_END)
		btnBox.pack_start(btn, False, False)
		btnBox.pack_end(btnKill, False, False)

		#pack stuff
		self.pack_start(sw)
		self.pack_end(btnBox, False, False)
		self.show_all()

		self.popupMenu=gtk.Menu()
		self.popupItem=gtk.MenuItem("KILL")
		self.popupMenu.append(self.popupItem)

		self.popupItem.show()
		self.popupItem.connect("activate",self._kill_on_right_click,None)

		self.tree.connect("button_press_event",self.on_right_click)
		self.reRun()

	def on_right_click(self,tree,event):
		if event.button == 3:	#Only on right click
			x = int(event.x)
			y = int(event.y)
			time=event.time
			pathinfo= tree.get_path_at_pos(x,y)
			if pathinfo is not None: #Right click i on some row
				path,col,cellx,celly=pathinfo
				location=self.store.get_iter(path)		
				tree.grab_focus()
				tree.set_cursor(path,col,0)
				self.popupMenu.popup(None,None,None,event.button,time)
				self.right_click_kill_pid=self.store[location][1]
				


	def _kill_on_right_click(self,widget,string):
		if os.getuid()==0:
			var='sudo kill -9 '
		else:
			var='kill -9 '
		temp=var+self.right_click_kill_pid
		self.right_click_kill_pid=""
		os.system(temp)
		self.reRun()

	def __on_refresh(self, btn):
		self.reRun()

	def __on_close(self,btnKill):
		if os.getuid()==0:
			var='sudo kill -9 '
		else:
			var='kill -9 '
		itr = self.store.get_iter_first()
		while itr!=None:
			if(self.store[itr][4]==True):
				temp=var+self.store[itr][1]#kill with PID
				#print temp
				os.system(temp)
			itr=self.store.iter_next(itr)
		self.reRun()

	def reRun(self):
		self.store.clear()
		if os.getuid()==0: 
			var='sudo lsof -i -n -P'
		else:
			var='lsof -i -n -P'
			print "Warning Only Current user shown"

		list_all=[]	
		fp=os.popen(var)	
		for i in fp:
			list_all.append(i)
		fp.close()
		for x in range(1,len(list_all)):
			value=[]
			temp_str=list_all[x]
			temp_part=''
			max_len=len(temp_str)
			a=0
			while a < max_len:#dont use in range as it will distort the order
				if(temp_str[a]!=' '):
					temp_part+=temp_str[a]
					a=a+1
				else:
					value.append(temp_part)
					temp_part=''
					while temp_str[a]==' ':
						a=a+1
			#0,1,2,8 Commans,Pid,User,Port
			#extract the port from 8th part
			if(len(value)>8):
				if(value[8][0]=='['):#incase of [::1] and [::xxx.xxx.xxx.xxx]
					temp=''
					a=3
					while a < len(value[8]):
						if(value[8][a]==':'):
							a+=1
							break
						else:
							a=a+1
					while a < len(value[8]) :
						if(value[8][a]!='-'):
							temp+=value[8][a]
							a=a+1
						else:
							break
					value[8]=temp
				elif(value[8][0]=='*'):
					temp=''
					for a in range(2,len(value[8])):
						temp=temp+value[8][a]
					value[8]=temp
				else:
					temp=''
					a=0

					while a < len(value[8]):
						if(value[8][a]==':'):
							a=a+1
							break
						else:
							a=a+1

					while a < len(value[8]) :
						if(value[8][a]!='-'):
							temp+=value[8][a]
							a=a+1
						else:
							break
					value[8]=temp
					
				self.store.append([value[0],value[1],value[2],value[8],None])
			
	def col1_toggled_cb( self, cell, path, model ):
		model[path][4] = not model[path][4]
		return

	
		
	

class NetPid(Plugin):
	def start(self, reader):
		#Insert a Icon in toolbar
		self.reader=reader
		self.icon = gtk.ToolButton(None,"Local Ports")
		image=gtk.image_new_from_stock(gtk.STOCK_DISCONNECT,gtk.ICON_SIZE_LARGE_TOOLBAR)
		image.show()
		self.icon.set_icon_widget(image)
		Core().get_main_toolbar().insert(self.icon,-1)	
		self.icon.connect('clicked',self.__on_created)
		self.icon.show_all()

			
	
	def stop(self):
		Core().get_main_toolbar().remove(self.icon)

		
	
	def __on_created(self,widget):#Do the Page creation here
		pid_page=Core().get_main_scan_notebook()#create a page
		widget=NetPidPage()
		widget.show_all()
		label=HIGAnimatedTabLabel("Local Ports")
		label.connect('close-clicked',self._close_window,widget)
		gtk.Notebook.append_page(pid_page,widget,label)
		
		
	def _close_window(self,widget,page):
		pid_page=Core().get_main_scan_notebook()
		index=gtk.Notebook.page_num(pid_page,page)
		page.hide()
		gtk.Notebook.remove_page(pid_page,index)
		

__plugins__ = [NetPid]



