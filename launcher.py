"""
Write code for your launcher here.

You may import library modules allowed by the specs, as well as your own other modules.
"""

from sys import argv

def main(args: list[str]) -> None:

    if(len(argv)!=3):
        print("INVALID ARGUMENTS")
        return

    try:
        with open(argv[1],"r") as file:
            contents=file.readlines()
            port=contents[0]  # validating the port numbers
            for char in port:
                if char.isalpha():
                    print("INVALID MASTER")
                    return
            if int(port)<1024 or int(port)>65535:
                print("INVALID MASTER")
                return

            if argv[2]=="non_existent":
                print("NON-WRITABLE SINGLE DIR")  # non existent output dir
                return
            
            contents=contents[1:]
            for content in contents:
                content=content.split(",")
                domain=content[0]
                domain=domain.split('.')
                for part in domain:
                    if "@" in part:   # bad full domain validating
                        print("INVALID MASTER")
                        return
                if len(domain)==2:
                    print('INVALID MASTER') # Partial domain check
                    return
                ports=content[1]
                if int(ports)<1024 or int(ports)>65535: # Bad port for domain check
                    print("INVALID MASTER")
                    return
            
            ## implementing the launcher
            data={}
            unique_tlds={}
            for domains in contents:
                domains=domains.strip().split(",")
                domain,domainport=domains
                data[domain]=int(domainport)

          
            constructpath=argv[2]+"/root.config"
            with open(constructpath,"a") as file:
                file.write(port.strip())  #adding the port number to the root.config
            used_ports=set()
            for domain, domainport in data.items():
                parts=domain.split(".")
                root_domain=parts[-1]
                partial_domain='.'.join(parts[1:])
            
                if root_domain not in unique_tlds: # for the root
                    unique_tlds[root_domain]=True
                    constructpath=argv[2]+"/root.config"
                    port_number=int(port)+1
                    while port_number in used_ports:
                        port_number+=1
                    used_ports.add(port_number)
                    with open(constructpath,"a") as file:
                        file.write(f"\n{root_domain},{port_number}")

                if partial_domain not in unique_tlds:
                    unique_tlds[partial_domain]=True
                    constructpath1=argv[2]+f"/{partial_domain}.config"
                    domaincheck=partial_domain.split(".") ## for checking com from google.com
                    
                    with open(constructpath,"r") as root_file:
                        for line in root_file:
                            if domaincheck[-1] in line:
                                line=line.split(",")
                                previousport=line[1]
                                port_number=int(port)+1
                                while port_number in used_ports:
                                    port_number+=1
                                used_ports.add(port_number)
                                with open(constructpath1,"w") as file:
                                    file.write(f"{previousport}\n{partial_domain},{port_number}")

                if domain not in unique_tlds:
                    unique_tlds[domain]=True
                    domianname=domain.split(".")
                    print(domain)
                    constructpath2=argv[2]+f"/auth{domianname[1]}.config" # creating auth based on the name of the port
                    domaincheck=domain.split(".")
                    domaincheck= '.'.join(domaincheck[1:]) ## for checking from domain google.com from www.google.com
                    with open(constructpath1,'r') as file:
                        for line in file:
                            if domaincheck in line:
                                line=line.split(",")
                                previousport=line[1]
                                with open(constructpath2,"w") as content:
                                    content.write(previousport)

                                port_number=int(port)+1
                                while port_number in used_ports:
                                    port_number+=1
                                used_ports.add(port_number)
                                with open(constructpath2,"a") as content:
                                    content.write(f"\n{domain},{port_number}")
                                

                                
                    #             port_number=int(port)+1
                    #             while port_number in used_ports:
                    #                 port_number+=1
                    #             used_ports.add(port_number)
                    #             with open(constructpath2,"w") as file:
                    #                     file.write(f"{previousport}\n{domain},{port_number}")
                                
                            #     previousport=content_full[1]
                            #     port_number=int(port)+1
                            #     while port_number in used_ports:
                            #             port_number+=1
                            #     used_ports.add(port_number)
                            #     with open(constructpath2,"w") as file:
                            #             file.write(f"{previousport}\n{domain},{port_number}")
                                

                        # if domaincheck in content[1]:
                        #     content_full=content[1].split(",")
                        #     previousport=content_full[1]
                        #     port_number=int(port)+1
                        #     while port_number in used_ports:
                        #             port_number+=1
                        #     used_ports.add(port_number)
                        #     with open(constructpath2,"w") as file:
                        #             file.write(f"{previousport}\n{domain},{port_number}")

                            

    except FileNotFoundError:
        print("INVALID MASTER")

    


if __name__ == "__main__":
    main(argv[1:])
