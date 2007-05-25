import sys
import timing
from xmlstore import XMLStore

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Specify a XML file."
        sys.exit(0)

    timing.start()

    XMLStore("schema-testing.db", sys.argv[1])

    timing.finish()
    print timing.milli()
