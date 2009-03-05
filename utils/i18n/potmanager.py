# Find files for getting translatable strings, update the reference pot and
# merge the pot files.
#
# Written by Guilherme Polo <ggpolo@gmail.com>

import os
import subprocess

# You may change these to point to the paths where your tools live
XGETTEXT = 'xgettext'
MSGMERGE = 'msgmerge'

class POTManager(object):
    def __init__(self, python_pkgs_root, *exclude_dirs):
        """
        python_pkgs_root    -   The starting directory to look for python
                                packages to collect translatable messages.
        exclude_dirs        -   Directory names to discard when looking
                                for packages.
        """
        self.python_pkgs_root = python_pkgs_root
        self.exclude_dirs = exclude_dirs

    def find_packages(self):
        root = self.python_pkgs_root
        for dirpath, dirnames, filenames in os.walk(root):
            for name in list(dirnames):
                if name in self.exclude_dirs:
                    dirnames.remove(name)

            if '__init__.py' in filenames:
                # This directory is a package, will run xgettext here
                yield dirpath

    def update_refpot(self, output):
        """Update the reference pot file and return the path of the
        new ref pot file."""
        args = [XGETTEXT, '-L', 'Python', '-o', output]
        root = self.python_pkgs_root
        for dirname in self.find_packages():
            relative_path = dirname[len(root) + len(os.path.sep):]
            args.append(os.path.join(relative_path, "*.py"))

        # XXX is xgettext too weird or what ?
        args = ' '.join(args)
        subprocess.check_call(args, shell=True)
        return output

    def update_pots(self, refpot, locale_dir):
        """Traverse locale_dir looking for .po files only inside
        subdirectories and merge each of them with the reference pot file."""
        for name in os.listdir(locale_dir):
            namepath = os.path.join(locale_dir, name)
            if not os.path.isdir(namepath) or name[0] == '.':
                continue

            # Each directory is supposed to contain a single pot file
            pot = filter(lambda x: x.endswith('.po'), os.listdir(namepath))[0]

            # merge pots
            potpath = os.path.join(namepath, pot)
            print "Merging %r" % potpath
            subprocess.check_call([MSGMERGE, '-U', potpath, refpot])


if __name__ == "__main__":
    potgen = POTManager(os.getcwd(), 'higwidgets', 'source-plugins', 'utils')
    locale_dir = os.path.join(os.getcwd(), 'share', 'locale')
    refpot = potgen.update_refpot(output=os.path.join(locale_dir, 'umit.pot'))
    potgen.update_pots(refpot, locale_dir=locale_dir)
