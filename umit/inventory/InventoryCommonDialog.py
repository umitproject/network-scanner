from umit.core.I18N import _

from higwidgets.higdialogs import HIGAlertDialog

# inventory without schedule, this happens when:
# - someone "creates" the inventory while adding a finished scan
#   from umit to the inventory viewer;
# - someone smart uses a database from somewhere else without
#   updating other files like schemas file.
class NoScheduleDlg(HIGAlertDialog):
    def __init__(self, parent=None):
        title = _("Inventory without scheduling profile.")
        message = _(
                "This Inventory was created when a scan realized in UMIT "
                "was requested to be added to the Network Inventory Viewer, "
                "so there is no scheduling profile for it.\n\n"
                "This Inventory is not editable.\n\n"
                "(If the mentioned reason above is incorrect, either you have "
                "a database from somewhere else or report as bug)"
                )

        HIGAlertDialog.__init__(self, parent,
                message_format=title, secondary_text=message)
