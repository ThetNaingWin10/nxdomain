"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

from sys import argv

def main(args: list[str]) -> None:

    if(len(argv)!=3):
        print("INVALID ARGUMENTS")
        return
    for a in argv:
        print(a)
        
    try:
        with open(argv[1],"r") as file:
            contents=file.read()
            print(contents)
    except FileNotFoundError:
        print("INVALID MASTER")

    


if __name__ == "__main__":
    main(argv[1:])
