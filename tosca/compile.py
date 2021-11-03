#!/usr/bin/env python3

import clout, puccini.tosca, inventory, ard, sys


def main():
    if len(sys.argv) <= 1:
        sys.stderr.write('no URL provided\n')
        sys.exit(1)

    url = sys.argv[1]

    try:
        clout_ = clout.Clout(url)
        inventory_ = inventory.Inventory(clout_)
        inventory_.write(sys.stdout)
    except puccini.tosca.Problems as e:
        print('Problems:', file=sys.stderr)
        for problem in e.problems:
            ard.write(problem, sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
