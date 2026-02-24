import os
import json
import shutil
from subprocess import PIPE, run
import sys

GAME_DIR_PATTERN="game"

def find_all_game_paths(source):
    game_paths=[]

    for root, dirs, files in os.walk(source):#recursively walk through the source directory
        for directory in dirs:
            if GAME_DIR_PATTERN in directory.lower():
                game_paths.append(os.path.join(root, directory))
                
        # for file in files:
        #     if GAME_DIR_PATTERN in file.lower():
        #         game_paths.append(os.path.join(root, file))    #uncomment this block to also find files with the pattern in their name, comment it to only find directories with the pattern in their name

            # break #uncomment this line to only find the first game directory, comment it to find all game directories
    return game_paths
            
def get_name_from_paths(paths, to_strip):
    new_names=[]
    for path in paths:
        _,dir_name=os.path.split(path)
        new_dir_name=dir_name.replace (to_strip,"").strip() #strip the to_strip string from the dir_name and also strip any leading or trailing whitespace
        new_names.append(new_dir_name)
    return new_names


def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


def copy_and_overwrtrite(source, target):
    if os.path.exists(target):
        shutil.rmtree(target) #remove the target directory and all its contents if it already exists
    shutil.copytree(source, target) #copy the source directory to the target directory

def make_json_metadata_file(path, game_dirs):
    data={
        "gamNames": game_dirs,
        "numberOfGames": len(game_dirs)
    }
    with open(path,"w") as f:
        json.dump(data,f, indent=4)

def compile_go_files(game_paths):
    for path in game_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                if file.endswith(".go"):
                    file_path=os.path.join(root, file)
                    result=run(["go", "build", file_path], stdout=PIPE, stderr=PIPE, text=True)
                    if result.returncode != 0:
                        print(f"Error compiling {file_path}: {result.stderr}")
                    else:
                        print(f"Successfully compiled {file_path}")

def main(source, target):
    cwd=os.getcwd()
    source_path=os.path.join(cwd,source)
    target_path=os.path.join(cwd,target)
    
    game_paths=find_all_game_paths(source_path)
    new_game_dirs=get_name_from_paths(game_paths, "_game")
    
    create_dir(target_path)

    dest_paths = []
    for src, dest in zip(game_paths, new_game_dirs):
        dest_path=os.path.join(target_path, dest)
        copy_and_overwrtrite(src, dest_path)
        dest_paths.append(dest_path)

    

    json_path=os.path.join(target_path, "metadata.json")
    make_json_metadata_file(json_path, new_game_dirs)
    compile_go_files(dest_paths)




if __name__ == "__main__":
    args = sys.argv
    # print(args)
    if len(args)!=3:
        raise Exception ("You must pass a source and target directory")
    
    source, target=args[1:] #to strip the first element which is the script name
    print(source, target)
    main (source, target)