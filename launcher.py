"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import os
import sys

from sys import argv

def validation(master_configuration):
    try:
        root_port=int(master_configuration[0])
    except ValueError:
        return False


def main(args: list[str]) -> None:
    if len(sys.argv) !=3:
        print('INVALID ARGUMENTS')
        sys.exit(1)
    
    master_confi=sys.argv[1]
    singlefile_output=sys.argv[2]

    if not os.path.isfile(master_confi):
        print("INVALID MASTER\n")
        sys.exit(1)
    
    pass


if __name__ == "__main__":
    main(argv[1:])
