import gtk
from HIGWidgets import HIGSpinner

def test_cache():
    cache = HIGSpinnerCache()
    cache.load_animated_from_lookup()
    cache.load_static_from_lookup()
    cache.spinner_images.set_rest_pixbuf("gnome-spinner-rest")
    
    print cache.spinner_images.animated_pixbufs
    print cache.spinner_images.static_pixbufs
    
    cache._write_animated_pixbuf_to_files("/tmp/cache_animated_%02i.png", "png")
    cache._write_static_pixbuf_to_file("gnome-spinner-rest", "/tmp/cache_static.png", "png")
    
def test_widget(num_spinners=1):
    win = gtk.Window()
    win.connect('delete-event', gtk.main_quit)

    

    # Fun with other static pixbuffers
    # s.cache.load_static_from_lookup("stock_new-formula")
    # s.cache.spinner_images.set_rest_pixbuf("stock_new-formula")
    
    t = gtk.Table(2 * num_spinners, 2 * num_spinners)

    x_start = 0
    x_end = 2
    y_start = 0
    y_end = 1

    for i in range(num_spinners):
        s = HIGSpinner()

        s.my_index = i

        # This is a HACK, uncomment this if you want to load a animation from a file
        s.cache.spinner_images.animated_pixbufs = []
        s.cache.load_animated_from_filename("gnome-green-spinner.png", 36)
        # This is the HACK continuation
        s.cache.load_static_from_filename("gnome-green-rest.png", "gnome-green-rest")
        s.cache.spinner_images.set_rest_pixbuf("gnome-green-rest")

        s.cache.spinner_images.set_size(100, 50)
        
        start_button = gtk.Button("Start")
        start_button.connect("clicked", lambda x: s.start())
        stop_button = gtk.Button("Stop")
        stop_button.connect("clicked", lambda x: s.stop())

        # Attach button
        print 'Spinner #%s: %s, %s, %s, %s' % (i, x_start, x_end, y_start, y_end)
        t.attach(s, x_start, x_end, y_start, y_end)

        # Move downwards 
        y_start += 1; y_end += 1
        # Button spans only one cell
        x_end -= 1

        #print 'Start   #%s: %s, %s, %s, %s' % (i, x_start, x_end, y_start, y_end)
        t.attach(start_button, x_start, x_end, y_start, y_end, yoptions=0)

        # Move right
        x_start += 1; x_end += 1

        #print 'Stop    #%s: %s, %s, %s, %s' % (i, x_start, x_end, y_start, y_end)
        t.attach(stop_button, x_start, x_end, y_start, y_end, yoptions=0)

        # Now move up, and to the right
        y_start -= 1; y_end -= 1
        x_start += 1; x_end += 2
        print 
        
    
    win.add(t)
    win.show_all()
    gtk.main()

if __name__ == '__main__':
    import sys

    test_widget(int(sys.argv[1]))

    #t = gtk.IconTheme()
    #info = t.lookup_icon("gnome-spinner", -1, 0)
    #print info, dir(info)
