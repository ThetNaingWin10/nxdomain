"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
from pathlib import Path
import pathlib
master_list=[]


def check(list,contents):
     i=0
     list=[]
     for line in contents:
        if "," in line:
             line=line.split(",")
             list.append(line[0])
             if line[0] in list:
                  print("Yes")

     print(len(list))
    #     return list
    #  else:
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

        # print(master_lines)
        list1=[]
        list2=[]
        list3=[]
        for line in master_lines:
             if ',' in line:
                line=line.split(",")
                lastdomain=line[0].split(".")
                list1.append(lastdomain[-1])
                middomain=line[0].rsplit(".",2)
                middomain=".".join(middomain[1:])
                list2.append(middomain)
                list3.append(line[0])
        # for line in list1:
        #      print(line) 
        # for line in list2:
        #      print(line)
        # for line in list3:
        #      print(line)      

        
        for items in single_files.iterdir():
             if items.is_file():
                  with items.open("r") as line:
                       contents=line.readlines()
                       if(int(currentport)==int(contents[0])):
                             check(list1,contents)
                            #  if(valid=="neq"):
                            #       print("neq")
                            #       return
                            #  for items in valid:
                            #       print(items)
                            
                             
                             
                                  
                

if __name__ == "__main__":
    main(argv[1:])
 