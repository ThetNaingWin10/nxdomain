"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import sys
import time

from sys import argv
root_server_ip = "127.0.0.1"
root_server_port = 1026
            
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

def resolve_domain(root_server_ip, root_port,time_out,domain):
        starttime=time.time()

        root_server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        root_server_socket.connect((root_server_ip,root_port))
        # server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        root_server_socket.send(f"{domain.split('.')[-1]}\n".encode('utf-8'))

        data=root_server_socket.recv(1024).decode('utf-8') #received the TLD port

        if(data):
            tld_port=int(data)

            tld_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            tld_socket.connect((root_server_ip,tld_port))
            
            tld_socket.send(f"{domain}\n".encode("utf-8"))

            #port of the authoritative nameserver
            
            response=tld_socket.recv(1024).decode("utf-8")

            if(response.startswith("NXDOMAIN")):
                print("NXDOMAIN",flush=True)
            else:
                auth_port=response
                auth_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                auth_socket.connect((root_server_ip,int(auth_port)))
                auth_socket.send(f"{domain}\n".encode("utf-8"))

                ip=auth_socket.recv(1024).decode("utf-8")


                timetaken=time.time()-starttime

                if(timetaken>time_out):
                    print("NXDOMAIN",flush=True)
                else:
                    print(f"{ip}",flush=True)
                
        else:
            print("No data received")
        
        #Query the TLD
        

def main(args: list[str]) -> None:
    if len(sys.argv)!=3:
        print("INVALID ARGUMENTS")
        sys.exit(1)
    root=int(sys.argv[1])
    time_out=int(sys.argv[2])
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
            else:
                resolve_domain(root_server_ip,root,time_out,domain_name)
            
    except EOFError:
        sys.exit(1)

if __name__ == "__main__":
    main(argv[1:])
