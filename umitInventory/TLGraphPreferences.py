# Copyright (C) 2007 Adriano Monteiro Marques
#
# Authors: Guilherme Polo <ggpolo@gmail.com>
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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA

import os
import gtk

from umitCore.I18N import _
from umitCore.Paths import Path

from higwidgets.higwindows import HIGWindow
from higwidgets.higboxes import HIGVBox, HIGHBox, hig_box_space_holder
from higwidgets.higlabels import HIGEntryLabel
from higwidgets.higbuttons import HIGButton

profiles = [
    _("Custom"), _("Standard"), _("Best Performance"),
    _("Best Visual")
    ]

pixmaps_dir = Path.pixmaps_dir

if pixmaps_dir:
    logo = os.path.join(pixmaps_dir, 'wizard_logo.png')
else:
    logo = None

class GraphPreferences(HIGWindow):
    """
    Graph Preferences Editor
    """

    def __init__(self, daddy=None):
        HIGWindow.__init__(self)

        self.daddy = daddy # TLGraphToolbar instance
        self.wtitle = _("Graph Preferences Editor")

        # header
        self.title_markup = "<span size='16500' weight='heavy'>%s</span>"
        self.ttitle = HIGEntryLabel("")
        self.ttitle.set_line_wrap(False)
        self.ttitle.set_markup(self.title_markup % self.wtitle)
        self.umit_logo = gtk.Image()
        self.umit_logo.set_from_file(logo)
        # profiles
        self.graph_profile_lbl = HIGEntryLabel(_("Profile"))
        self.graph_profile = gtk.combo_box_new_text()
        # horizontal divisors/balloons
        self.hdivs_lbl = HIGEntryLabel(_("Horizontal divisors"))
        self.hdivs = gtk.SpinButton(gtk.Adjustment(value=5, lower=2, upper=10,
            step_incr=1), 1)
        # arc drawing
        self.draw_arc_lbl = HIGEntryLabel('')
        self.draw_arc_lbl.set_markup(_("<b>Points higlight</b>"))
        self.draw_arc_onsel = gtk.RadioButton(label=_("On Selection"))
        self.draw_arc_always = gtk.RadioButton(self.draw_arc_onsel,
            label=_("Always"))
        self.draw_arc_bounds = gtk.RadioButton(label=_("Boundary points only"))
        self.draw_arc_allpts = gtk.RadioButton(self.draw_arc_bounds,
            label=_("Every point"))
        self.balloons = gtk.CheckButton(_("Show balloons on selection"))
        # vertical divisors
        self.draw_vertdiv = gtk.CheckButton(_("Draw vertical lines"))
        self.draw_vertdiv_dash = gtk.RadioButton(label=_("Dashed"))
        self.draw_vertdiv_solid = gtk.RadioButton(self.draw_vertdiv_dash,
            label=_("Solid"))
        # background fill
        self.bg_gradient = gtk.CheckButton(_("Gradient background"))
        self.bg_gradient_vert = gtk.RadioButton(label=_("Vertical gradient"))
        self.bg_gradient_horiz = gtk.RadioButton(self.bg_gradient_vert,
            label=_("Horizontal gradient"))
        # selection fill
        self.selection_fill = gtk.CheckButton(_("On selection do "
            "progressive fill"))
        self.selection_fill_solid = gtk.RadioButton(label=_("Solid fill"))
        self.selection_fill_gradient = gtk.RadioButton(
            self.selection_fill_solid, label=_("Gradient fill"))
        # bottom buttons
        self.help = HIGButton(stock=gtk.STOCK_HELP)
        self.help.connect('clicked', self._show_help)
        self.apply = HIGButton(stock=gtk.STOCK_APPLY)
        self.apply.connect('clicked', self._save_pref)
        self.cancel = HIGButton(stock=gtk.STOCK_CANCEL)
        self.cancel.connect('clicked', self._exit)
        self.ok = HIGButton(stock=gtk.STOCK_OK)
        self.ok.connect('clicked', self._save_pref_and_leave)


        self.append_profiles()
        start_profile = self.load_options_from_graph()
        self.setup_controls(None, start_profile)

        self.__do_connects()
        self.__set_props()
        self.__do_layout()


    def append_profiles(self):
        """
        Write profiles to combobox.
        """
        for p in profiles:
            self.graph_profile.append_text(p)

        self.graph_profile.set_active(1)


    def graph_attrs(self):
        """
        Tuple of attributes in graph.
        """
        return (
            "hdivisors", "draw_arcs_always", "draw_every_arc",
            "show_balloons", "draw_dashed_vert", "draw_solid_vert",
            "gradient_fill", "gradient_direction", "selection_effect",
            "selection_gradient" )


    def load_options_from_graph(self):
        """
        Load startup graph settings.
        """
        # horizontal divisors
        hdivs = self.daddy.graph_attr("hdivisors") + 1
        # arcs
        draw_arcs_always = int(self.daddy.graph_attr("draw_arcs_always"))
        draw_every_arc = int(self.daddy.graph_attr("draw_every_arc"))
        # balloons
        balloons = self.daddy.graph_attr("show_balloons")
        # vertical lines
        vert_enabled = True
        if self.daddy.graph_attr("draw_dashed_vert"):
            vert_line = 0
        elif self.daddy.graph_attr("draw_solid_vert"):
            vert_line = 1
        else:
            vert_line = -1
            vert_enabled = False
        # widget background
        gradient_bg = True and self.daddy.graph_attr("gradient_fill")
        if not gradient_bg:
            gradient_bg_dir = -1
        else:
            gradient_bg_dir = int(self.daddy.graph_attr("gradient_direction"))
        # selection
        selection_effect = True and self.daddy.graph_attr("selection_effect")
        selection_fill = int(self.daddy.graph_attr("selection_gradient"))

        profile = {"Startup": (
            hdivs, draw_arcs_always, draw_every_arc,
            balloons, vert_enabled, vert_line,
            gradient_bg, gradient_bg_dir,
            selection_effect, selection_fill)}

        return profile


    def setup_controls(self, event, startup=None):
        """
        Enable/Disable controls.
        """
        opt_profiles = (
            _("Standard"), _("Best Performance"), _("Best Visual")
            )

        profile = self.graph_profile.get_active_text()
        indx_active = self.graph_profile.get_active()
        if not profile in opt_profiles: # custom
            return

        # dict with default values for each option in this window.
        profiles_d = {
            _("Standard"): (5, 0, 1, True, False, -1, False, -1, True, 0),
            _("Best Performance"): (3, 0, 0, True, False, -1, False, -1,
                False, 0),
            _("Best Visual"): (5, 0, 1, True, True, 0, True, 0, True, 1)
            }

        if startup:
            found_profile = False
            for p, values in profiles_d.items():
                if startup["Startup"] == values:
                    index_profile = profiles.index(p)
                    self.graph_profile.set_active(index_profile)
                    indx_active = self.graph_profile.get_active()
                    profile = p
                    found_profile = True
                    break

            if not found_profile: # custom
                indx_active = 0
                profile = _("Custom")
                self.graph_profile.set_active(indx_active)
                temp = { }
                temp[_("Custom")] = startup["Startup"]
                profiles_d.update(temp)


        controls = (self.hdivs, (self.draw_arc_onsel, self.draw_arc_always),
                    (self.draw_arc_bounds, self.draw_arc_allpts),
                    self.balloons, self.draw_vertdiv, (self.draw_vertdiv_dash,
                    self.draw_vertdiv_solid), self.bg_gradient,
                    (self.bg_gradient_vert, self.bg_gradient_horiz),
                    self.selection_fill, (self.selection_fill_solid,
                    self.selection_fill_gradient))

        for indx, control in enumerate(controls):
            value = profiles_d[profile][indx]

            if value >= 2: # it is spinbutton
                control.set_value(float(value))
            elif type(value) == type(True): # checkbutton
                control.set_active(value)
            elif value != -1: # radiobutton
                control[value].set_active(True)


        checkbtns = (self.draw_vertdiv, self.bg_gradient)
        methods = (self._vertdiv_changed, self._bgfill_changed)

        for indx, checkbtn in enumerate(checkbtns):
            methods[indx](checkbtn.get_active(), indx_active)

        return True


    def _vertdiv_changed(self, event, custom=0):
        """
        Vertical divisors enabled/disabled.
        """
        status = self.get_status(event)

        self.draw_vertdiv_dash.set_sensitive(status)
        self.draw_vertdiv_solid.set_sensitive(status)

        self.graph_profile.set_active(custom)


    def _bgfill_changed(self, event, custom=0):
        """
        Gradient background fill enabled/disabled.
        """
        status = self.get_status(event)

        self.bg_gradient_vert.set_sensitive(status)
        self.bg_gradient_horiz.set_sensitive(status)

        self.graph_profile.set_active(custom)


    def get_status(self, event):
        """
        Get event status.
        """
        if type(event) == type(True):
            status = event # event generated by profile change
        else:
            status = event.get_active() # event generated by mouse click

        return status


    def _show_help(self, event):
        """
        Show help for Graph Preferences.
        """


    def _save_pref(self, event):
        """
        Save preferences.
        """
        profile = self.graph_profile.get_active_text()

        cmds = {
            _("Standard"): "standard_mode",
            _("Best Performance"): "speedup_performance",
            _("Best Visual"): "best_visual" }

        if profile != _("Custom"):
            self.daddy.change_graph_mode = cmds[profile]
            return

        controls = (self.hdivs, self.draw_arc_always, self.draw_arc_allpts,
                    self.balloons, (self.draw_vertdiv, self.draw_vertdiv_dash,
                    self.draw_vertdiv_solid), self.bg_gradient,
                    self.bg_gradient_horiz, self.selection_fill,
                    self.selection_fill_gradient)

        indx = 0
        for control in controls:
            if type(control) == type(tuple()): # group of controls
                enable = True
                if not control[0].get_active():
                    enable = False

                for c in control[1:]:
                    if enable == False:
                        self.daddy.change_graph_attr = (
                            self.graph_attrs()[indx], False)
                    else:
                        self.daddy.change_graph_attr = (
                            self.graph_attrs()[indx], c.get_active())
                    indx += 1

                continue

            elif hasattr(control, "get_active"): # radio/checkbutton
                self.daddy.change_graph_attr = (
                    self.graph_attrs()[indx], control.get_active())
                    
            elif hasattr(control, "set_width_chars"): # spinbutton
                nhdiv = int(control.get_text())
                self.daddy.change_graph_attr = self.graph_attrs()[indx], nhdiv

            indx += 1

        self.daddy.update_graph()


    def _save_pref_and_leave(self, event):
        """
        Saves preferences and close window.
        """
        self._save_pref(None)
        self._exit(None)


    def _exit(self, event):
        """
        Close window.
        """
        self.destroy()


    def __do_connects(self):
        """
        Connect signals.
        """
        self.hdivs.connect('value-changed',
            lambda c: self.graph_profile.set_active(0))

        self.draw_arc_always.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.draw_arc_bounds.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.draw_arc_allpts.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.balloons.connect('toggled',
            lambda c: self.graph_profile.set_active(0))

        self.draw_vertdiv.connect('toggled', self._vertdiv_changed)
        self.draw_vertdiv_dash.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.draw_vertdiv_solid.connect('clicked',
            lambda c: self.graph_profile.set_active(0))

        self.bg_gradient.connect('toggled', self._bgfill_changed)
        self.bg_gradient_vert.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.bg_gradient_horiz.connect('clicked',
            lambda c: self.graph_profile.set_active(0))

        self.selection_fill.connect('toggled',
            lambda c: self.graph_profile.set_active(0))
        self.selection_fill_solid.connect('clicked',
            lambda c: self.graph_profile.set_active(0))
        self.selection_fill_gradient.connect('clicked',
            lambda c: self.graph_profile.set_active(0))

        self.graph_profile.connect('changed', self.setup_controls)


    def __set_props(self):
        """
        Set window properties.
        """
        self.set_title(self.wtitle)


    def __do_layout(self):
        """
        Layout widgets in window.
        """

        def left_padding(widget):
            """
            Add left padding for a widget.
            """
            left_padding_align = gtk.Alignment(0.5, 0.5, 1, 1)
            left_padding_align.set_padding(0, 0, 12, 0)
            left_padding_align.add(widget)
            return left_padding_align


        main_vbox = HIGVBox()
        main_vbox.set_border_width(5)
        main_vbox.set_spacing(12)
        header_hbox = HIGHBox()
        profile_hbox = HIGHBox()
        hdivs_hbox = HIGHBox()
        arcdraw_vbox = HIGVBox()
        vdivs_vbox = HIGVBox()
        bgfill_vbox = HIGVBox()
        selectfill_vbox = HIGVBox()
        btns_hbox = HIGHBox()

        # header
        header_hbox._pack_expand_fill(self.ttitle)
        header_hbox._pack_noexpand_nofill(self.umit_logo)

        # profiles
        profile_hbox._pack_noexpand_nofill(self.graph_profile_lbl)
        profile_hbox._pack_noexpand_nofill(self.graph_profile)

        # horizontal divisors
        hdivs_hbox._pack_noexpand_nofill(self.hdivs_lbl)
        hdivs_hbox._pack_noexpand_nofill(self.hdivs)

        # arc drawing
        arcdraw_vbox._pack_noexpand_nofill(self.draw_arc_lbl)

        arcdraw_when = HIGHBox()
        arcdraw_when._pack_noexpand_nofill(self.draw_arc_onsel)
        arcdraw_when._pack_noexpand_nofill(self.draw_arc_always)

        arcdraw_where = HIGHBox()
        arcdraw_where._pack_noexpand_nofill(self.draw_arc_bounds)
        arcdraw_where._pack_noexpand_nofill(self.draw_arc_allpts)

        arcdraw_vbox._pack_noexpand_nofill(left_padding(arcdraw_when))
        arcdraw_vbox._pack_noexpand_nofill(left_padding(arcdraw_where))
        arcdraw_vbox._pack_noexpand_nofill(left_padding(self.balloons))

        # vertical divisors
        vdivs_vbox._pack_noexpand_nofill(self.draw_vertdiv)

        vdivs_kind = HIGHBox()
        vdivs_kind._pack_noexpand_nofill(self.draw_vertdiv_dash)
        vdivs_kind._pack_noexpand_nofill(self.draw_vertdiv_solid)

        vdivs_vbox._pack_noexpand_nofill(left_padding(vdivs_kind))

        # background fill
        bgfill_vbox._pack_noexpand_nofill(self.bg_gradient)

        bgfill_gtype = HIGHBox()
        bgfill_gtype._pack_noexpand_nofill(self.bg_gradient_vert)
        bgfill_gtype._pack_noexpand_nofill(self.bg_gradient_horiz)

        bgfill_vbox._pack_noexpand_nofill(left_padding(bgfill_gtype))

        # selection fill
        selectfill_vbox._pack_noexpand_nofill(self.selection_fill)

        selectfill_kind = HIGHBox()
        selectfill_kind._pack_noexpand_nofill(self.selection_fill_solid)
        selectfill_kind._pack_noexpand_nofill(self.selection_fill_gradient)

        selectfill_vbox._pack_noexpand_nofill(left_padding(selectfill_kind))

        # bottom buttons
        btns_hbox.set_homogeneous(True)
        btns_hbox._pack_expand_fill(self.help)
        btns_hbox._pack_expand_fill(hig_box_space_holder())
        btns_hbox._pack_expand_fill(self.apply)
        btns_hbox._pack_expand_fill(self.cancel)
        btns_hbox._pack_expand_fill(self.ok)


        main_vbox._pack_noexpand_nofill(header_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(profile_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(hdivs_hbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(arcdraw_vbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(vdivs_vbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(bgfill_vbox)
        main_vbox._pack_noexpand_nofill(gtk.HSeparator())
        main_vbox._pack_noexpand_nofill(selectfill_vbox)
        main_vbox.pack_end(btns_hbox, False, False, 0)
        main_vbox.pack_end(gtk.HSeparator(), False, False, 0)
        self.add(main_vbox)
