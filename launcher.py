"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

from sys import argv

def validation(master_configuration):
    try:
        root_port=int(master_configuration[0])
    except ValueError:
        return False


def main(args: list[str]) -> None:
    if len(argv) !=1:
        print('INVALID ARGUMENTS')
        return
    
    master_confi=argv[1]
        
    
    pass


if __name__ == "__main__":
    main(argv[1:])
