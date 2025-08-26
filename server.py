"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

import socket
from sys import argv

dns_records={}

def check(command):
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
    
def rootresponse(domain,config):
    if domain in config:
        target_port=dns_records[domain]
        return target_port
    else:
        return "NXDOMAIN"

def main(args: list[str]) -> None:
    if len(argv) != 2:
        print("INVALID ARGUMENTS") 
        return

    config_file=argv[1]
    try:
        with open(config_file, "r") as rconfig_file:
            config=rconfig_file.readlines()


            for line in config[1:]:
                line=line.strip()
                if(",") in line:
                    key,value= line.split(",",1)
                    dns_records[key]=value

            for key, value in dns_records.items():
                # print(f"Key: {key}, Value: {value}")
                for char in key:
                    if not char.isalpha() and char!='.':
                        print("INVALID CONFIGURATION")
                        return

                 ##checking the keys and values
            return

            server_port=int(config[0].strip())
            server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            server_socket.bind(("localhost",server_port))  ##this was causing the invalid port error
            server_socket.listen()

            while True:
                socket_client , _ = server_socket.accept()
                data=socket_client.recv(server_port).decode("utf-8").strip()
                # socket_client.send((data+'\n').encode("utf-8"))  #just in case to see the files inside config file
                if data.startswith('!'):
                    if(data=="!EXIT\n"):
                        socket_client.close()
                        return
                    else:
                        check(data)
                        # socket_client.send((data+'\n').encode("utf-8"))
                else:
                    if data in dns_records:
                        response=rootresponse(data,dns_records)
                        socket_client.send((response+'\n').encode("utf-8"))
                        print(f"resolve {data} to {response}",flush=True)
                    else :
                        response="NXDOMAIN"
                        socket_client.send((response+'\n').encode("utf-8"))
                        print(f"resolve {data} to {response}",flush=True)
                      
                socket_client.close()

    except FileNotFoundError:
        print("INVALID CONFIGURATION")
    except PermissionError:
        print("INVALID CONFIGURATION")
    finally:
        try:
            if server_socket:
                server_socket.close()
        except UnboundLocalError:
            return
            

if __name__ == "__main__":
    main(argv[1:])