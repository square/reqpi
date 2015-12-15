import sys

from twisted.scripts import twistd

REQPI_MAIN_OK = True


def main(args):
    # Telling lies for fun and profit
    sys.argv = ['twistd', '--nodaemon', '--pidfile=', 'reqpi'] + args[1:]
    twistd.run()
