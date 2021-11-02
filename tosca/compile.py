#!/usr/bin/env python3

from clout import *
from inventory import *
import sys, ard


def main():
    if len(sys.argv) <= 1:
        sys.stderr.write('no URL provided\n')
        sys.exit(1)

    url = sys.argv[1]

    try:
        clout = Clout(url)
        inventory = Inventory()
        inventory.from_clout(clout)
        inventory.write(sys.stdout)
    except puccini.tosca.Problems as e:
        print('Problems:', file=sys.stderr)
        for problem in e.problems:
            ard.write(problem, sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
