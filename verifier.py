"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import pathlib

def read_configuration(filepath) :
    list={}
 
    with open(filepath,'r') as file:
        for line in file:
            line=line.strip()
            if line:
                id,value=line.split(',')
                list[int(id)]=value
    return list

def compare_config(masterconfig,singlefileconfig):
    return masterconfig==singlefileconfig

def main(args: list[str]) -> None:
    master_file=argv[1]
    single_files=argv[2]

    masterconfig=read_configuration(master_file)

    single_dir=pathlib.Path(single_files).iterdir()
    result="eq"

    for singlefile in single_dir:
        if singlefile.is_file():
            config=read_configuration(singlefile)
            if config is not None:
                if not compare_config(masterconfig,config):
                    result= "neq"
                    break
    print(result)
    


if __name__ == "__main__":
    main(argv[1:])
