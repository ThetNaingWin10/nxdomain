"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

from sys import argv

def main(args: list[str]) -> None:

    if(len(argv)!=3):
        print("INVALID ARGUMENTS")
        return

    try:
        with open(argv[1],"r") as file:
            contents=file.readlines()
            port=contents[0]
            for char in port:
                if char.isalpha():
                    print("INVALID MASTER")
                    return
            if int(port)<1024 or int(port)>65535:
                print("INVALID MASTER")
            
            
            # for char in contents:
            #     if char.isalpha():
            #         print("INVALID")
            #         return

            # if int(port)<1024 or int(port)>65535 or port.isalpha():  #validating the port number
            #     print("INVALID MASTER")
            


    except FileNotFoundError:
        print("INVALID MASTER")

    


if __name__ == "__main__":
    main(argv[1:])
