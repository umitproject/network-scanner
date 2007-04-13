import gtk
from HIGWidgets import *

def test_entries():
    
    w = HIGWindow()
    w.connect("delete-event", gtk.main_quit)
    
    # vb is the top-most vertical box
    vb = HIGVBox()
    w.add(vb)
    
    # vb
    #  - packed in: w
    #  - packs: * "Section" label
    #               * hb
    vb._pack_noexpand_nofill(HIGSectionLabel("Section"))
    
    # hb
    #  - packed in: vb
    #  - packs: * et
    hb = HIGHBox()
    hb._pack_noexpand_nofill(HIG_box_space_holder())
    
    # let is the Label/Entry Table
    let = HIGTable(2, 2)
    let.attach_label(HIGEntryLabel("Entry 1:"), 0, 1, 0, 1)
    let.attach_entry(gtk.Entry(), 1, 2, 0, 1)
    let.attach_label(HIGEntryLabel("Entry 2:"), 0, 1, 1, 2)
    let.attach_entry(gtk.Entry(), 1, 2, 1, 2)
    hb._pack_expand_fill(let)
	
    vb.pack_line(hb)
    w.show_all()
	
    gtk.main()

if __name__ == '__main__':
    test_entries()
