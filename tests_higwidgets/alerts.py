import gtk
from HIGWidgets import *

HIGAlertDialog(message_format="You Have and Appointment\nin 15 minutes",
               secondary_text="You shouldn't be late this time. Oh, and\n there's a huge traffic jam on your way!").run()
