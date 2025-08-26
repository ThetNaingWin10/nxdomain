"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path
import pathlib
master_list=[]

def compare_config(masterconfig,singlefileconfig):
    return masterconfig==singlefileconfig

def main(args: list[str]) -> None:
    master_file=Path(argv[1])
    single_files=Path(argv[2])
    master_lines=master_file.read_text().split("\n")

    currentport=master_lines[0].strip()
    domain=master_lines[1].split(",")[0]
    target_port=int(master_lines[1].split(",")[1])

    print(currentport)
    print(domain)
    print(target_port)

    for single_file in single_files.iterdir():
        if single_file.is_file():
            content=single_file.read_text().split("\n")
            portofcontent=content[0].strip()
            domaincontent=content[1].split(",")[0]
            contentaddr=content[1].split(",")[1]
            print(portofcontent)
            print(domaincontent)
            print(contentaddr)
            
            

            
            

            # if(currentport) != content_lines[0].strip().split(",")[-1]:

        
   


        # first_line=file.readline().strip()
        # second_line=file.readline().strip()
        # parts=second_line.split(',')
        # if(len(parts)==2):
        #     url,port=parts
        #     master_list.append((url,int(port)))
   
    

if __name__ == "__main__":
    main(argv[1:])
 