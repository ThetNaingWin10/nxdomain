"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

from sys import argv

# def resolve_domain(root_port, timeout) :
#     try:
#         root_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #socket to connect to the root directory
#         root_socket.connect(("localhost",root_port))

#         while True:
#             domain=input("Please Enter a Domian or CtrlD to exit") 
#             if not domain:
#                 break
        

#         root_socket.send(f"{domain}\n".encode("utf-8")) #send the query to the domain server
        
#         startingtime=time.time() #starting the timer

#         tld_port=root_socket.recv(1024).decode("utf-8").strip() # receiving the response from the root server
#         print(f"{tld_port}")
#         duration= time.time()-startingtime # checking if the duration of the program running exceeds the timeout
#         if duration>timeout:
#             print("NXDOMAIN (Timeout)")
            

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
    except EOFError:
        sys.exit(1)

if __name__ == "__main__":
    main(argv[1:])
