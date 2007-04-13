import os, os.path, time
from threading import Thread

command = 'nmap -oN %s -oX %s -vv -sV 127.0.0.1 > %s'

if os.name == 'nt':
    tempdir = 'C:\\'
elif os.name == 'posix':
    tempdir = '/tmp'

class NmapThread(Thread):
    def __init__(self, name=None):
        Thread.__init__(self, group=None, name=name)

        self.std_output_filename = os.path.join(tempdir, "thread_%s.std_output" % self.getName())
        self.normal_output_filename = os.path.join(tempdir, "thread_%s.normal_output" % self.getName())
        self.xml_output_filename = os.path.join(tempdir, "thread_%s.xml_output" % self.getName())

    def run(self):
        self.command_result = os.system (command % (self.normal_output_filename,
                                                    self.xml_output_filename,
                                                    self.std_output_filename))

l = []
for i in range(10):
    print '>>> Creating Thread %s' % i
    l.append(NmapThread(name=str(i)))
    print '>>> Starting Thread %s' % i
    l[i].start()

while True:
    if len(l) == 0: break
    for t in l:
        name = t.getName()
        status = {True  : 'Running',
                  False : 'Finished'}[t.isAlive()]
        print '>>>>>>>>>>>>>>> Checking Thread %s >>>>>>>>>>>>>>>>>>' % t.getName()
        print '>>> Status: %s' % status
        print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>'
        if os.path.exists(t.std_output_filename):
            print open(t.std_output_filename).read()
        time.sleep(1)
        if status == 'Finished':
            print '>>> Removing Thread %s' % name
            l.remove(t)
