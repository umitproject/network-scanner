import sys
import time
from xmlstore import XMLStore

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print "Specify at least one XML file."
        sys.exit(0)

    start = time.ctime()
    start_ = time.time()

    storing = XMLStore("schema-testing.db")
    for file in sys.argv[1:]:
        storing.store_xml(file)

    print "Started on:", start
    print "Finished on:", time.ctime()
    print "No. of files specified:", len(sys.argv[1:])
    print "It took", time.time() - start_, "seconds to complete operation."
