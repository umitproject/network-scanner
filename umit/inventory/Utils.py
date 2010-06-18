from umit.core.I18N import _

def append_s(word, count):
    if count == 0 or count > 1:
        word += _("s")
    return word
