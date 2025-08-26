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
            port=contents[0]  # validating the port numbers
            for char in port:
                if char.isalpha():
                    print("INVALID MASTER")
                    return
            if int(port)<1024 or int(port)>65535:
                print("INVALID MASTER")
            
            contents=contents[1:]
            for content in contents:
                content=content.split(",")
                domain=content[0]
                domain=domain.split('.')
                for part in domain:
                    if "@" in part:   # bad full domain validating
                        print("INVALID")
                        return
                if len(domain)==2:
                    print('INVALID MASTER') # Partial domain check
                    return
                ports=content[1]
                if int(ports)<1024 or int(port)>65535: # Bad port for domain check
                    print("INVALID MASTER")
                    return


    except FileNotFoundError:
        print("INVALID MASTER")

    


if __name__ == "__main__":
    main(argv[1:])
