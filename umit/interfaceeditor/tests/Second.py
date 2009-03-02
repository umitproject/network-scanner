from unittest import TestCase, main
import gtk
import time
import gtk


import sys
sys.path.append("../")
sys.path.append("../selectborder")
from umitInterfaceEditor import umitInterfaceEditor



# Stolen from Kiwi
def refresh_gui(delay=0):
  while gtk.events_pending():
      gtk.main_iteration_do(block=False)
  time.sleep(delay)
class MyView(gtk.VBox):

  def __init__(self):
      super(MyView, self).__init__()
      self._button  = gtk.Button('Click Me')
      self._label = gtk.Label()
      self.pack_start(self._button)
      self.pack_start(self._label)
      self._count = 0
      self._button.connect('clicked', self.on_button_clicked)

  def on_button_clicked(self, button):
      self._count = self._count + 1
      self._label.set_text('clicked %s times' % self._count)
    
class MyViewTest(TestCase):

  def setUp(self):
      self._v = umitInterfaceEditor()

  #def test_count(self):
      #self.assertEqual(self._v._count, 0)
      #self._v._button.clicked()
      #refresh_gui()
      #self.assertEqual(self._v._count, 1)

  #def test_label(self):
      #self._v._button.clicked()
      #refresh_gui()
      #self.assertEqual(self._v._label.get_text(), 'clicked 1 times')

if __name__ == '__main__':
  main()
