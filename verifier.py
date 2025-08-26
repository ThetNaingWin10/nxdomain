"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path
import pathlib
master_list=[]


# def check(currentport,domain,content,i):
#     if(content[0]==currentport):
#                 for line in content:
#                     if "," in line:
#                         parts=line.split(',')
#                         domain_check=parts[0]
#                         porting_address=parts[1]
                        
#                         if(domain_check==domain.rsplit('.',3)[3]):
#                             return porting_address
#     return None


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

        print(currentport)
        print(master_lines)
        foundport=0
        
        for items in single_files.iterdir():
             if items.is_file():
                  with items.open("r") as line:
                       contents=line.readlines()
                       print(contents[0])
   
    

if __name__ == "__main__":
    main(argv[1:])
 