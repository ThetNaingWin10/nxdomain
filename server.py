"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

import socket
import sys

from sys import argv
dns_records={}
message=""

def handle_command(command):
    global dns_records
    parts=command.split()
    if(len(parts)==3):
        action, hostname, port=parts
        if action=="!ADD" :
            dns_records[hostname]=port
        elif action=="!DEL":
            if hostname in dns_records:
                del dns_records[hostname]
        elif action=="!EXIT" :
            sys.exit(1)
        else:
            print("INVALID")
    else:
        print("INVALID")
    
def root_responses(hostname):
    if hostname in dns_records:
        print(f"{dns_records[hostname]}")
        return dns_records[hostname]
    else:
        print("NXDOMAIN")
        return "NXDOMAIN"

def main(args: list[str]) -> None:
    if len(sys.argv) != 2:
        print("INVALID ARGUMENTS")
        sys.exit()

    config_file=sys.argv[1]

    try:
        with open(config_file, "r") as rconfig_file:
            port = int(rconfig_file.readline().strip())  
            print(f"Server Test runnin on {port}")  
        server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        server_socket.bind(("localhost",1024))
        server_socket.listen(1024)

        #while True:
            #socket_client ,address_client= server_socket.accept()
           # message=''
            #while True:
              #  data=socket_client.recv(1024).decode("utf-8")
               # if not data:
                  #  break
               # message+=data
              #  if message.endswith('\n'):
                    #response=root_responses(message.strip())
                   # socket_client.send(response.encode("utf-8"))
                   # message=""
                
           # socket_client.close()
    
    except FileNotFoundError:
        print("INVALID CONFIGURATION")
    #finally:
        #if server_socket:
            #server_socket.close()

if __name__ == "__main__":
    main(argv[1:])
