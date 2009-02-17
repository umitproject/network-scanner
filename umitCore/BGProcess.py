import os
import sys
import signal

try:
    DEVNULL = os.devnull
except AttributeError:
    DEVNULL = '/dev/null'

def daemon_init(new_cwd='/', umask=0):
    pid = os.fork()
    if pid:
        # parent terminates
        sys.exit(0)

    # child 1 continues
    os.setsid() # Become session leader

    signal.signal(signal.SIGHUP, signal.SIG_IGN)
    pid = os.fork()
    if pid:
        # child 1 terminates
        sys.exit(0)

    # child 2 continues
    os.umask(0)

    if new_cwd is not None:
        os.chdir(new_cwd)

    # Redirect stdin, stdout, and stderr to DEVNULL
    for fobj in (sys.stdin, sys.stdout, sys.stderr):
        fobj.close()
    sys.stdin = open(DEVNULL, 'r')
    sys.stdout = open(DEVNULL, 'a+')
    sys.stderr = open(DEVNULL, 'a+')

    # Success!


def run_on_background(*args, **kwargs):
    if hasattr(sys, 'winver'):
        print "Too bad"
    else:
        daemon_init(*args, **kwargs)
