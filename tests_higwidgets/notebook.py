import gtk
from HIGWidgets import *

def button_start_cb(w, p):
    p.start()
def button_stop_cb(w, p):
    p.stop()

win = gtk.Window()
win.connect('delete-event', gtk.main_quit)

def cb(data):
    print 'close-clicked'

n = HIGNotebook()

for i in range(6):
    t = HIGAnimatedTabLabel("Page %s" % i)
    t.connect('close-clicked', cb)
    n.append_page(gtk.Button("teste"), t )

win.add(n)
win.show_all()

gtk.main()
