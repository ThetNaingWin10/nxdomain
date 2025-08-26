"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

import socket
import sys

from sys import argv
dns_records={}
def handle_command(command):
    global dns_records
    parts=command.split()
    if(len(parts)==3):
        action, hostname, port=partsif
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
        server_socket=(("localhist"),port)
        server_socket.listen(5)

        while True:
            socket_client ,address_client= server.socket.accept()
            while True:
                data=socket_client.recv(1024).decode("utf-8")
                if not data:
                    break
                message+=data
                
                    
            message= ""
            socket_client.close()
    
    except FileNotFoundError:
        print("INVALID CONFIGURATION")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main(argv[1:])
