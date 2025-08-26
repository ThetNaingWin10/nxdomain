"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

from sys import argv

def resolve_domain(root_port, timeout) :
    try:
        root_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket to connect to the root directory
        root_socket.connect(("localhost",root_port))
        while True:
            domain=input("Please Enter a Domian or CtrlD to exit") 
            if not domain:
                break
        

        root_socket.send(f"{domain}\n".encode("utf-8")) #send the query to the domain server
        
        startingtime=time.time() #starting the timer

        tld_port=root_socket.recv(1024).decode("utf-8").strip() # receiving the response from the root server
        print(f"{tld_port}")
        duration= time.time()-startingtime # checking if the duration of the program running exceeds the timeout
        if(duration>timeout) :
            print("NXDOMAIN (Timeout)")


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
