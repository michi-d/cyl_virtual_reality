#!/usr/bin/python
__author__      = "Michael Drews"
__copyright__   = "Michael Drews"
__email__       = "drews@neuro.mpg.de"

import sys, getopt
from core.base import CalibrationArena
from experiment.Shared import Shared


def main(argv):

    shared = Shared()
    shared.check_readiness = [1,1,0]
    arena = CalibrationArena([0, 0, 0, 0, 0, 0, 0.0, 0.0, 0.0, 0, 0.0, 0, (0.0, 0.0), (0.0, 0.0)], shared)
    arena.run()

if __name__ == "__main__":
    main(sys.argv[1:])