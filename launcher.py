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

            for domain, domainport in data.items():
                parts=domain.split(".")
                root_domain=parts[-1]
                partial_domain='.'.join(parts[1:])
                print(partial_domain)
                
                if root_domain not in unique_tlds: # for the root
                    unique_tlds[root_domain]=True
                    argv[2]=f"{root_domain}.config"
                    with open(argv[2],"w") as file:
                        file.write(f"{port}{root_domain},{domainport}")

                # if partial_domain not in unique_tlds:
                #     unique_tlds[partial_domain]=True
                #     argv[2]=f"{partial_domain}.config"
                #     with open(argv[2],"w") as file:
                #         file.write(f"{port}{partial_domain},{domainport}")
                    


                # if tld not in unique_tlds:
                #     unique_tlds[tld]=True

                #     argv[2]=f"{tld}.config"

                #     with open(argv[2],"w") as file:
                #         file.write(f"{domain},{port} ")
                


    except FileNotFoundError:
        print("INVALID MASTER")

    


if __name__ == "__main__":
    main(argv[1:])
