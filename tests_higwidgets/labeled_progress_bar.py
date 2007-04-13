import gtk
from HIGWidgets import *

w = HIGWindow()
n = gtk.Notebook()

pages = [HIGVBox() for i in range(0, 5)]

for i in range(0, 5):
    p = HIGLabeledProgressBar("10.1.1.%s" % i)
    p.show_all()
    pages[i].set_size_request(200, 200)
    n.insert_page(pages[i], p)

w.add(n)
w.connect("delete-event", lambda w, p: gtk.main_quit())
w.show_all()

gtk.main()
