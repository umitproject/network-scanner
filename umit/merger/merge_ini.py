import os
import shutil
import ConfigParser

from umit.merger.errors import OriginError, DestinationError

def merge(from_file, to_file):
    """
    @from_file: Path to a supposed newer ini file
    @to_file: Path to a supposed older ini file
    @return true or false
    """
    if not os.path.exists(from_file):
        raise OriginError(from_file)
    if not os.path.exists(to_file):
        raise DestinationError(to_file)

    # Read new file
    config_new = ConfigParser.RawConfigParser()
    config_new.read(from_file)

    # Read old file
    config = ConfigParser.RawConfigParser()
    config.read(to_file)

    # Merge files
    changed = False
    for section in config_new.sections():
        if config.has_section(section):
            # Merge section's content
            for option, value in config_new.items(section):
                if not config.has_option(section, option):
                    # Add the new option
                    config.set(section, option, value)
                    changed = True
        else:
            # section does not exist in the old ini file, copy it there
            copy_section(config, config_new, section)
            changed = True

    if changed:
        # Backup the destination
        shutil.copyfile(to_file, to_file + '.bak')

        # Write back the merged configuration
        f = open(to_file, 'wb')
        config.write(f)

def copy_section(config, config_new, section):
    config.add_section(section)
    for k, v in config_new.items(section):
        config.set(section, k, v)


if __name__=="__main__":
    import sys
    if len(sys.argv) != 3:
        print "Test usage: %s fromcfg tocfg" % __file__
        sys.exit(1)

    merge(*sys.argv[1:])
