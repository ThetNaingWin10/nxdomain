"""
Write code for your verifier here.

You may import library modules allowed by the specs, as well as your own other modules.
"""
from sys import argv
import pathlib

def read_configuration(filepath) :
    list=[]
 
    with open(filepath,'r') as file:
        for line in file:
            line=line.strip()
            if line:
                list.append(line)
    return list

def compare_config(masterconfig,singlefileconfig):
    return masterconfig==singlefileconfig

def main(args: list[str]) -> None:
    master_file=argv[1]
    single_files=argv[2]

    masterconfig=read_configuration(master_file)
    print(masterconfig[0])
    print(masterconfig[1])
    print(masterconfig[2])

    single_dir=pathlib.Path(single_files).iterdir()

    # for singlefile in single_dir:
    #     if singlefile.is_file():
    #         config=read_configuration(singlefile)
    #         if config is not None:
    #             if not compare_config(masterconfig,config):
    #                 result= "neq"
    #                 break
    # print("eq")
    


if __name__ == "__main__":
    main(argv[1:])
