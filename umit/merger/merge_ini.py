import os
import shutil
import ConfigParser

def merge(old_file, new_file):
    """
    @old_file: Path to a supposed older ini file
    @new_file: Path to a supposed newer ini file
    @return true or false
    """
    if not os.path.exists(old_file) or not os.path.exists(new_file):
        return False

    # Backup old file
    shutil.copyfile(old_file, old_file + '.bak')

    # Read new file
    config_new = ConfigParser.RawConfigParser()
    config_new.read(new_file)

    # Read old file
    config = ConfigParser.RawConfigParser()
    config.read(old_file)

    # Merge files
    for section in config_new.sections():
        if config.has_section(section):
            # Merge section's content
            for option, value in config_new.items(section):
                if not config.has_option(section, option):
                    # Add the new option
                    config.set(section, option, value)
        else:
            # section does not exist in the old ini file, copy it there
            copy_section(config, config_new, section)

    # Write back the merged configuration
    f = open(old_file, 'wb')
    config.write(f)

    return True

def copy_section(config, config_new, section):
    config.add_section(section)
    for k, v in config_new.items(section):
        config.set(section, k, v)


if __name__=="__main__":
    import sys
    if len(sys.argv) != 3:
        print "Test usage: %s oldcfg newcfg" % __file__
        sys.exit(1)

    merge(*sys.argv[1:])
