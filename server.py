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
    if(len(parts)==2):
        action,hostname=parts
        if action =="!DEL":
            if hostname in dns_records.keys():
                del dns_records[hostname]
            else:
                return
        else :
            print("INVALID",flush=True)
    
def root_responses(domain,port,config):
    target_port=get_port(domain,config)
    if target_port is not None:
        return str(target_port)
    else:
        return "NXDOMAIN"
    
def get_port(domain,config):
    for line in config:
        return int(dns_records[domain])
    return None

def main(args: list[str]) -> None:
    if len(sys.argv) != 2:
        print("INVALID ARGUMENTS")
        sys.exit()

    config_file=sys.argv[1]
    try:
        with open(config_file, "r") as rconfig_file:
            config=rconfig_file.readlines()
            contents=rconfig_file.read()


            for line in config[1:]:
                line=line.strip()
                if(",") in line:
                    key,value= line.split(",",1)
                    dns_records[key]=value

            server_port=int(config[0].strip())
            server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_socket.bind(("localhost",server_port))
            #adsf
            server_socket.listen()
            socket_client.send((contents+'\n').encode("utf-8"))

            while True:
                socket_client , _ = server_socket.accept()
                data=socket_client.recv(server_port).decode("utf-8").strip()

                if data.startswith('!'):
                    if(data=="!EXIT\n"):
                        socket_client.close()
                        sys.exit(1)
                    else:
                        handle_command(data)
                        # socket_client.send((data+'\n').encode("utf-8"))

                else:
                    if data in dns_records:
                        port=dns_records[data]
                        response=root_responses(data,port,dns_records)
                        socket_client.send((response+'\n').encode("utf-8"))
                        print(f"resolve {data} to {response}",flush=True)
                    
                socket_client.close()

    except FileNotFoundError:
        print("INVALID CONFIGURATION")
    finally:
        if server_socket:
            server_socket.close()

if __name__ == "__main__":
    main(argv[1:])