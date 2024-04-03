import os

def map_directory(
        item_name,
        ignore=[],
        sort_items=True,
        ):

    if os.path.isdir(item_name):
        dir_items = [item for item in os.listdir(item_name) if item not in ignore]

        if sort_items:
            dir_items.sort()
        
        return {item_name: [map_directory(item, ignore, sort_items) for item in dir_items]}

    return item_name