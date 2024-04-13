import os
import pandas as pd


def map_directory(
        item_name,
        ignore=[],
        sort_items=True,
        ):

    if os.path.isdir(item_name):
        dir_items = [
            item for item in os.listdir(item_name) if item not in ignore
            ]

        if sort_items:
            dir_items.sort()
        
        return {item_name: [
            map_directory(item, ignore, sort_items) for item in dir_items
            ]}

    return item_name


def render_map_as_str(directory_map):
    def get_depths(item, depth=0):
        depths = []

        if type(item) == dict:
            item_name = str(list(item.keys())[0])
            sub_items = list(item.values())[0]
            
            depths += [(item_name, depth)]

            for sub_item in sub_items:
                depths += get_depths(sub_item, depth+1)
            
            return depths
        
        else:
            return [(item, depth)]
        
    depths = get_depths(directory_map)

    str_map = ""
    for item, depth in depths:
        str_map += "\t" * depth + item + "\n"
    return str_map[:-1]


def get_context(path, ignore=[]):
    item_name = path.split('/')[-1]

    if item_name in ignore:
        context = f"\n===== {path} ignored =====\n"
    
    elif os.path.isdir(path):
        context = ""

        for item in os.listdir(path):
            context += get_context(os.path.join(path, item), ignore)
    
    elif os.path.isfile(path):
        full_read_files = ('py', 'txt', 'sh', 'ipynb', 'gitignore')

        file_ext = path.split('.')[-1]

        if file_ext in full_read_files:
            context = f"\n===== Begin file {path} =====\n"

            with open(path, 'r') as f:
                context += f.read()
            
            context += f"\n===== End file {path} =====\n"
        
        else:
            raise NotImplementedError(f"File type for {path} not implemented yet")
    
    else:
        raise ValueError(f"{path} does not appear to be a file or directory")
        
    return context