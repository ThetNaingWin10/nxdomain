"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path
import pathlib
master_list=[]

def check(currentport,domain,content,i):
    if(content[0]==currentport):
                for line in content:
                    if "," in line:
                        parts=line.split(',')
                        domain_check=parts[0]
                        porting_address=parts[1]
                        if(domain_check==domain.rsplit('.',3)[3]):
                            return porting_address
    return None


def main(args: list[str]) -> None:
    try:
        master_file=Path(argv[1])
        single_files=Path(argv[2])
    except IndexError:
         print("invalid arguments")
         return
    try:      
        master_lines=master_file.read_text().split("\n")
    except FileNotFoundError:
        print("invalid arguments")
        return  
    try:
        currentport=master_lines[0].strip()
        domain=master_lines[1].split(",")[0]
        target_port=int(master_lines[1].split(",")[1])
    except FileNotFoundError:
         print("invalid master")

    for char in currentport:
         if char.isalpha():
              print("invalid master")
              return
    print(currentport)
    print(domain)
    print(target_port)
    domain_length=domain.split(".")
    i=len(domain_length)-1
    # z=0
    

    for single_file in single_files.iterdir():
        if single_file.is_file():
            content=single_file.read_text().split("\n")
            while i>0:
                # print(currentport)
                # print(domain.rsplit('.',3)[3])
                # print(content)
                print(i)
                print(currentport)
                address_port=check(currentport,domain,content,i)
                if address_port==None:
                    break
                else :
                    currentport=address_port
                    # print(currentport)
                    i-=1
                    break

                # if(z>2):
                #     porting_address=check(currentport,domain,content,0)
                # elif(z==len(domain_length)):
                #     break
                # else :        
                # z+=1
            # i-=1
            
            
    #         if(content[0]==currentport):
    #             for line in content:
    #                 if "," in line:
    #                     parts=line.split(',')
    #                     domain_check=parts[0]
    #                     porting_address=parts[1]
    #                     if(domain_check==domain.rsplit('.',3)[3]):
    #                         currentport=porting_address

    # for single_file in single_files.iterdir():
    #     if single_file.is_file():
    #         content=single_file.read_text().split("\n")
            
    #         if(content[0]==currentport):
    #             for line in content:
    #                 if "," in line:
    #                     parts=line.split(',')
    #                     domain_check=parts[0]
    #                     porting_address=parts[1]
    #                     if(domain_check==domain.rsplit('.',2)[2]):
    #                         currentport=porting_address

            # if(currentport) != content_lines[0].strip().split(",")[-1]:

        
   


        # first_line=file.readline().strip()
        # second_line=file.readline().strip()
        # parts=second_line.split(',')
        # if(len(parts)==2):
        #     url,port=parts
        #     master_list.append((url,int(port)))
   
    

if __name__ == "__main__":
    main(argv[1:])
 