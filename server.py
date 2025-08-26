"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

import socket
import sys


from sys import argv
dns_records={}

def handle_command(command):
    parts=command.split()
    if(len(parts)==3):
        action,hostname,port=parts
        if action=="!ADD":
            if port in dns_records.values():
                return
            else:
                dns_records[hostname]=port
        else:
            print("INVALID",flush=True)
            
            
    

            
    # global dns_records
    # parts=command.split()
    # if(len(parts)==3):
    #     action, hostname, port=parts
    #     if action=="!ADD" :
    #         dns_records[hostname]=port
    #     elif action=="!DEL":
    #         if hostname in dns_records:
    #             del dns_records[hostname]
    #     elif action=="!EXIT\n" :
    #         sys.exit(1)
    #     else:
    #         print("INVALID")
    # else:
    #     print("INVALID")
    
def root_responses(domain,port,config):
    target_port=get_port(domain,config)
    if target_port is not None:
        return str(target_port)
    else:
        return "NXDOMAIN"
    
def get_port(domain,config):
    for line in config:
        parts=line.strip().split(',')
        if parts[0]==domain:
            return int(parts[1])
    return None

def main(args: list[str]) -> None:
    if len(sys.argv) != 2:
        print("INVALID ARGUMENTS")
        sys.exit()

    config_file=sys.argv[1]
    try:
        server_socket='none'
        with open(config_file, "r") as rconfig_file:

            for line in rconfig_file:
                line=line.strip()
                if("," in line):
                    key,value=line.split(",",1)
                    dns_records[key]=int(value) ##storing the initial keys and values from the config file

            config=rconfig_file.readlines() ## reading the config file

            server_port=int(config[0].strip()) ## getting the first port
            server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_socket.bind(("localhost",server_port))
            server_socket.listen()

            for hostname,port in dns_records.items(): ## looping through the values in the dns_records

                while True:
                    socket_client , _ = server_socket.accept()
                    data=socket_client.recv(server_port).decode("utf-8").strip()

                    if data.startswith('!'):
                        if(data=="!EXIT\n"):
                            socket_client.close()
                            sys.exit(1)
                        else:
                            handle_command(data)

                    else:
                        response=root_responses(data,port,config)
                        socket_client.send((response+'\n').encode("utf-8"))
                        dns_records[f"{data}"]=response
                        print(f"resolve {data} to {response}",flush=True)
                        
                    socket_client.close()

    except FileNotFoundError:
        print("INVALID CONFIGURATION")
    finally:
        if server_socket:
            server_socket.close()

if __name__ == "__main__":
    main(argv[1:])
