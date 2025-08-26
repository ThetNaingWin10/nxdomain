"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

from sys import argv
            
def valid(domain_name):
    list=domain_name.split(".")
    if len(list)!=3:
        return False
    else :
        C=list[0]
        B=list[1]
        A=list[2]
        #validating C
        if C.startswith(".") or C.endswith("."):
            return False
        if not all(char.isalnum() or char == "-" or char == "." for char in C):
            return False
        #validating B
        if not all(char.isalnum() or char == "-"  for char in B):
            return False
        #validating A
        if not all(char.isalnum() or char == "-"  for char in A):
            return False
        else:
            return True
    

def main(args: list[str]) -> None:
    if len(sys.argv) !=3:
        print("INVALID ARGUMENTS")
        sys.exit(1)
    root=int(sys.argv[1])
    time_out=sys.argv[2]
    root_server_ip=socket.gethostbyname("localhost")

    server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server_socket.connect((root_server_ip,root))

    try:
        while True:
            domain_name=input()
            if not domain_name:
                break
            if not valid(domain_name):
                print("INVALID",flush=True)
                #dsaf
    except EOFError:
        sys.exit(1)

if __name__ == "__main__":
    main(argv[1:])
