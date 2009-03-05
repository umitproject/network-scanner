# Find files for getting translatable strings, update the reference pot,
# merge the pot files and compile them.
#
# Written by Guilherme Polo <ggpolo@gmail.com>

import os
import subprocess

# You may change these to point to the paths where your tools live
# XXX Need to update this utility to use the python version of these utilities
# in case the gnu ones are not present.
XGETTEXT = 'xgettext'
MSGMERGE = 'msgmerge'
MSGFMT = 'msgfmt'

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
        for pot in self._find_pots(locale_dir):
            # merge pots
            print "Merging %r" % pot
            subprocess.check_call([MSGMERGE, '-U', pot, refpot])

    def compile(self, locale_dir, use_fuzzy=True, verbose=False, do_checks=True,
            statistics=False, appname='umit', mo_dir='LC_MESSAGES'):
        """Traverse locale_dir looking for .po files only inside
        subdirectories and compile them to .mo files."""
        extra_opts = []
        if use_fuzzy:
            extra_opts.append('-f')
        if verbose:
            extra_opts.append('-v')
        if do_checks:
            extra_opts.append('-c')
        if statistics:
            extra_opts.append('--statistics')

        for pot in self._find_pots(locale_dir):
            potdir = os.path.dirname(pot)
            mo_path = os.path.join(potdir, mo_dir, "%s.mo" % appname)
            # compile pot
            print "Compiling %r to %r" % (pot, mo_path)
            subprocess.check_call([MSGFMT, pot, '-o', mo_path] + extra_opts)

    def _find_pots(self, basedir):
        """Find pot files just in the way that the methods compile and
        update_pots expect."""
        for name in os.listdir(basedir):
            namepath = os.path.join(locale_dir, name)
            if not os.path.isdir(namepath) or name[0] == '.':
                continue

            for name in os.listdir(namepath):
                if name.endswith('.po'):
                    yield os.path.join(namepath, name)
                    # Each directory is supposed to contain a single pot file
                    break


if __name__ == "__main__":
    potgen = POTManager(os.getcwd(), 'higwidgets', 'source-plugins', 'utils')
    locale_dir = os.path.join(os.getcwd(), 'share', 'locale')
    refpot = potgen.update_refpot(output=os.path.join(locale_dir, 'umit.pot'))
    potgen.update_pots(refpot, locale_dir=locale_dir)
    potgen.compile(locale_dir)
