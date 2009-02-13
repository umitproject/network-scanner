import gtk, gtk.glade
import os.path
import gobject


class PWE:
	
	def __init__(self, gladefile="pwe.glade"):
		self.__wd=gtk.glade.XML(gladefile)
		self.__read_widgets()
		self.__groupslist()
		self.BoxOption()
		self.__optionlist("optionlist")
		#self.detailsBox()




	def detailsBox(self, name, command, root):
		"""
		Fill Details Box

		"""
		self.__detailsBox = self.__wd.get_widget("entry2")
		self.__detailsBox.set_text(name)
	
	def __read_widgets(self):
		self.__window = self.__wd.get_widget("window1")
		
		self.__toolbar = self.__wd.get_widget("toolbar_up_main")
		self.__toolbar.set_style(gtk.TOOLBAR_ICONS)
		
		self.__toolbar2 = self.__wd.get_widget("toolbar_down_main")
		self.__toolbar2.set_style(gtk.TOOLBAR_ICONS)
		
	def __groupslist(self):
		self.__tabs = self.__wd.get_widget("tabs")
		
		treemodel=gtk.TreeStore(gobject.TYPE_STRING)
		self.__tabs.set_model(treemodel)
		#Column 1
		renderer=gtk.CellRendererText()
		column=gtk.TreeViewColumn("Group",renderer, text=0)
		self.__tabs.append_column(column)
		#Column 2

		model = treemodel
		# List is NOT static, this is only a test to be quick. 
		lista = ["Scan", "Ping", "Target", "Source", "Other", "Advanced"]	
		for i in lista:
			myiter=model.insert_after(None,None)
			model.set_value(myiter,0,i)
	
	def fullPath(self,file):
		homepath = os.path.expanduser("~")
		homepath = homepath + "/.umit/" + file
		return homepath
	def BoxOption(self):
		#read box
		self.boxOp=self.__wd.get_widget("listaopcoes")
		self.treemodel = gtk.TreeStore(gobject.TYPE_STRING)
		self.boxOp.set_model(self.treemodel)

		#Column 1
		self.addColumn("Name", self.boxOp, 0)	
		
		fullp = self.fullPath("options.xml")

		xml = XMLEdit(fullp)	
		fill_tree = xml.read()
		model=self.treemodel
		#print fill_tree
		for i, v  in fill_tree:
			myiter = model.insert_after(None, None)	
			model.set_value(myiter, 0, i)
		
		#Events: 
		
		
		selection = self.boxOp.get_selection()
		selection.connect("changed", self.display_selected_option)
			
	def display_selected_option(self, w):
		sel = self.boxOp.get_selection()
		(model, iter) = sel.get_selected()
		name_of_data = self.treemodel.get_value(iter, 0)
		self.detailsBox(name_of_data, "cmd", True)
	def addColumn(self,name, tv, i):
		renderer = gtk.CellRendererText()
		column = gtk.TreeViewColumn(name, renderer, text=i)
		tv.append_column(column)
	
	
	def __optionlist(self, treename):
		#Read option list TreeView
		self.__optionlist = self.__wd.get_widget(treename)
		treemodel = gtk.TreeStore(gobject.TYPE_STRING, gobject.TYPE_STRING)
		self.__optionlist.set_model(treemodel)
		#Column 1
		self.addColumn("Name", self.__optionlist,0)
		#this is only for *nix systems, but It's just a draft of interface, in glade.. It's not important right now. 
		
		homepath = self.fullPath("options.xml") 
		xml = XMLEdit(homepath)	
		fill_tree = xml.read()
		model=treemodel
		#print fill_tree
		j = 0
		for i, v  in fill_tree:
			myiter=model.insert_after(None,None)
			model.set_value(myiter,0,i)
			#sumulation: 
			j = j+1
			if (j>7):
				break
	def show_all(self):
		self.__tabs.show()
		self.__optionlist.show()	
		self.boxOp.show()
		self.__window.show()


from xml.dom import minidom
class XMLEdit: 
	def __init__(self, filename="/home/kop/.umit/options.xml"):
		#xml_desc = open(filename)
		self.filename=filename
		self.doc = minidom.parse(filename)
		#xml_desc.close()
	def read(self,tag="option",name="name",option="option"):
		#print tag, name, option	
		result = []
		for node in self.doc.getElementsByTagName(tag):
			tmp_name= node.getAttribute(name)
			tmp_option = node.getAttribute(option)
			#print option
			result.append((tmp_name,tmp_option))
		return result

p=PWE()
p.show_all()

gtk.main()




		


