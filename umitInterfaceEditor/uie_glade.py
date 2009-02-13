import gtk, gtk.glade
import os.path
import gobject


class UIE:
	
	def __init__(self, gladefile="draft_1.glade"):
		self.wd=gtk.glade.XML(gladefile)
		self.window = self.wd.get_widget("window1")
		

	def show_all(self):
		self.window.show_all()

p=UIE()
p.show_all()

gtk.main()




		


