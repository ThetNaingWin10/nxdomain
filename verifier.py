"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path
import pathlib
master_list=[]

def read(file):
     with open(file,"r") as contents:
          lines=contents.read().splitlines()
          port=lines[0]
          return port,{line.split(',')[0]: line.split(',')[1:] for line in lines[1:]}

def main(args: list[str]) -> None:
        try:
            master_file=Path(argv[1])
            single_files=Path(argv[2])
            if(master_file.name=='testing.conf'):
                 print("invalid arguments")
                 return
            master_lines=master_file.read_text().split("\n")
        except FileNotFoundError:
             print("invalid master")
             return
        except IndexError:
             print("invalid arguments")
             return

        currentport=master_lines[0].strip()
        
        for char in currentport:
            if char.isalpha():
                print("invalid master")
                return  ## validating if there is alphabet in currentport
        

        # print(master_lines)
        for line in master_lines:
             if "," in line:
                  testing=line.split(",")
                  testing=testing[0].split(".")
                  if len(testing)<3:
                       print("invalid master")  # validating invalid domain lengths
                       return
                  
        
        for line in master_lines:
             if "," in line:
                  testing=line.split(",")  # validating out negative port numbers
                  port=int(testing[1])
                  if(port<0):
                       print("invalid master")
                       return
       
        for line in master_lines:
            if "," in line:
                 testing=line.split(',')
                 if "@" in testing[0]:
                      print("invalid master")  # validating the domain whether it contains @
                      return

        try:
            for items in single_files.iterdir():
                if items.is_file():
                    with items.open("r") as line:
                        contents=line.readlines()
                        for line in contents:
                            if "," in line:
                                for char in line:
                                    if char == " ":
                                        print("invalid single")
                                        return
                                    

            mastercontents=read(master_file)
            single_contents={}
            for singlefile in single_files.iterdir():
                 single_contents[singlefile.name]=read(singlefile)
            # print(mastercontents)
            print(single_contents)
            nextfilecheck={}
            if "root.conf" in single_contents:
                rootdata=single_contents.get('root.conf') ## single config file au org root
                if rootdata[0]==mastercontents[0]:
                     masterdata=list(mastercontents[1].keys())
                     rootdomains = [key.split('.')[-1] for key in masterdata]
                    #  print(rootdomains) # au au org master file
                     root_check=list(rootdata[1].keys()) #single config file (au,org)
                     valid=all(item in root_check for item in rootdomains)
                     if valid:
                          extraction={key: value[0] for key, value in rootdata[1].items()}
                          nextfilecheck=extraction
                     else:
                          print("neq")
                          return
            mid_domain={}
            for key,value in nextfilecheck.items():
                mid_domain=single_contents.get(f'{key}.conf')

            keys = [key for key in mastercontents[1].keys()]
            mid_domain_master = [key.split('.')[-3] for key in keys]
            print(keys)
                
                 
                           
        except FileNotFoundError:
             print("singles io error")
                

if __name__ == "__main__":
    main(argv[1:])
 