from umitCore.I18N import _

class NoInventory(Exception):
    def __init__(self, missing_inventory=None):
        self.missing_inventory = missing_inventory

    def __str__(self):
        if self.missing_inventory:
            return _("No inventory named %r" % self.missing_inventory)
        else:
            return ''
