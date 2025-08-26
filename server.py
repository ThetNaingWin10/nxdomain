"""
Write code for your server here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

import socket
from sys import argv
ENCODING = "utf-8"
dns_records={}

def _valid_label(label: str) -> bool:
    if not (1 <= len(label) <= 63):
        return False
    if label[0] == '-' or label[-1] == '-':
        return False
    return all(c.isalnum() or c == '-' for c in label)

def is_valid_hostname(name: str) -> bool:
    # Accept 1+ labels (supports TLD-only like 'com' as well as 'www.google.com')
    if not name:
        return False
    parts = name.split('.')
    return all(_valid_label(p) for p in parts if p)

def check(command: str) -> str:
    parts = command.strip().split()
    if not parts:
        return "INVALID"
    if parts[0] == "!EXIT" and len(parts) == 1:
        return "!EXIT"
    if len(parts) == 3 and parts[0] == "!ADD":
        _, hostname, port = parts
        if not is_valid_hostname(hostname):
            return "INVALID"
        if not port.isdigit():
            return "INVALID"
        p = int(port)
        if not (1 <= p <= 65535):
            return "INVALID"
        dns_records[hostname] = str(p)
        return "OK"
    if len(parts) == 2 and parts[0] == "!DEL":
        _, hostname = parts
        if not is_valid_hostname(hostname):
            return "INVALID"
        dns_records.pop(hostname, None)
        return "OK"
    return "INVALID"

def rootresponse(domain: str, mapping: dict[str,str]) -> str:
    return mapping.get(domain, "NXDOMAIN")

def main(args: list[str]) -> None:
    if len(argv) != 2:
        print("INVALID ARGUMENTS") 
        return

    config_file=argv[1]
    try:
        with open(config_file, "r") as rconfig_file:
            config = rconfig_file.readlines()
            if not config:
                print("INVALID CONFIGURATION")
                return

            # Validate and parse server port (first line)
            first = config[0].strip()
            if not first.isdigit():
                print("INVALID CONFIGURATION")
                return
            server_port = int(first)
            if not (1 <= server_port <= 65535):
                print("INVALID CONFIGURATION")
                return

            # Parse records
            for line in config[1:]:
                line = line.strip()
                if not line:
                    continue
                if "," not in line:
                    print("INVALID CONFIGURATION")
                    return
                key, value = line.split(',', 1)
                key = key.strip()
                value = value.strip()
                if not is_valid_hostname(key):
                    print("INVALID CONFIGURATION")
                    return
                if not value.isdigit():
                    print("INVALID CONFIGURATION")
                    return
                p = int(value)
                if not (1 <= p <= 65535):
                    print("INVALID CONFIGURATION")
                    return
                dns_records[key] = str(p)

            server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            server_socket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            server_socket.bind(("127.0.0.1", server_port))
            server_socket.listen()

            while True:
                socket_client, _ = server_socket.accept()
                try:
                    data = socket_client.recv(1024).decode(ENCODING)
                    if not data:
                        continue
                    data = data.strip()

                    if data.startswith('!'):
                        resp = check(data)
                        if resp == "!EXIT":
                            socket_client.sendall(b"OK\n")
                            socket_client.close()
                            server_socket.close()
                            return
                        socket_client.sendall((resp + "\n").encode(ENCODING))
                    else:
                        if data in dns_records:
                            response = rootresponse(data, dns_records)
                        else:
                            response = "NXDOMAIN"
                        socket_client.send((response + '\n').encode(ENCODING))
                        print(f"resolve {data} to {response}", flush=True)
                finally:
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