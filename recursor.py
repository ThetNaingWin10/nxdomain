"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

from sys import argv


def main(args: list[str]) -> None:
    if len(sys.argv) !=3:
        print("INVALID ARGUMENTS")
        sys.exit(1)
    try:
        root=int(sys.argv[1])
        timeout=float(sys.argv[2])

    except Exception as e:
        print("Error",str(e))
        
    pass


if __name__ == "__main__":
    main(argv[1:])
