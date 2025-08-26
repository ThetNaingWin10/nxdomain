"""
Write code for your recursor here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
import socket
import signal

from sys import argv
root_server_ip = "127.0.0.1"
root_server_port = 1026

def timeoutsignal(signalnumber,frame):
    raise TimeoutError("NXDOMAIN")
  
def valid(domain_name):
    list=domain_name.split(".")
    if len(list)==3 or len(list)==4:
        C=list[-3]
        B=list[-2]
        A=list[-1]
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
    else :
        return False
        

def resolve_domain(root_serversocket,time_out,domain):
        signal.signal(signal.SIGALRM,timeoutsignal)
        timeout=float(time_out)
        signal.alarm(round(timeout))
        try:

            root_serversocket.send(f"{domain.split('.')[-1]}\n".encode('utf-8'))

            data=root_serversocket.recv(1024).decode('utf-8') #received the TLD port
            # the invalids outputs are from incorrect domains.

            if data:
                if data.startswith("NXDOMAIN"):
                    print("NXDOMAIN", flush=True) 
                else :
                    data=int(data)
            
                    tld_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                    try:   
                        tld_socket.connect((root_server_ip,data))
                    except ConnectionRefusedError:
                        print("FAILED TO CONNECT TO TLD")
                        return
                    tld_socket.send(f"{domain.split('.')[-2]}.{domain.split('.')[-1]}\n".encode("utf-8"))

                    #port of the authoritative nameserver
                    
                    response=tld_socket.recv(1024).decode("utf-8")
                    
                    if(response.startswith("NXDOMAIN")):
                        print("NXDOMAIN", flush=True)
                    else :
                        auth_port=int(response)
                        auth_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
                        try:
                            auth_socket.connect((root_server_ip,int(auth_port)))
                        except ConnectionRefusedError:
                            print("FAILED TO CONNECT TO AUTH")
                            return
                        auth_socket.send(f"{domain}\n".encode("utf-8"))

                        ip=auth_socket.recv(1024).decode("utf-8")
                        print(f"{ip}".strip(),flush=True)
                        
            else:
                print("No data received")
        except TimeoutError:
            print("NXDOMAIN",flush=True)
        finally:
            signal.alarm(0)

        

def main(args: list[str]) -> None:
    if len(args)!=2:
        print("INVALID ARGUMENTS")
        return
    
    root=int(argv[1])
    time_out=argv[2]
    
    try :
        server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        server_socket.connect((root_server_ip,root))
    except ConnectionRefusedError:
        print("FAILED TO CONNECT TO ROOT")
        return
    except OverflowError:
        print("INVALID ARGUMENTS")
        return

    try:
        while True:
            domain_name=input()
            if not valid(domain_name):
                print("INVALID",flush=True)
                return
            else:
                resolve_domain(server_socket,time_out,domain_name)
            
    except EOFError:
        return

if __name__ == "__main__":
    main(argv[1:])
