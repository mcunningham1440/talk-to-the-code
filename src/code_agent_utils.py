import os
import autogen
from typing import Annotated

from config import *


def generate_agent_response(user_query, directory):
    code_interpreter_agent = autogen.AssistantAgent(
        name="test_agent",
        llm_config=config.llm_config,
        system_message="You are a software engineer whose job is to answer \
            questions about how a code repository functions."
        )

    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        human_input_mode="NEVER",
        code_execution_config=False,
        max_consecutive_auto_reply=10,
        is_termination_msg=lambda x: x.get("content") is not None and "TERMINATE" in x["content"],
        llm_config=config.llm_config
    )

    agent_functions = [get_context]

    for function in agent_functions:
        function_name = function.__name__

        code_interpreter_agent.register_for_llm(name=function_name, description=function.description)(function)
        user_proxy.register_for_execution(name=function_name)(function)

    directory_map = map_directory(directory)
    str_map = render_map_as_str(directory_map)

    task = f"""==== Begin repository map =====
{str_map}
===== End repository map =====

===== Begin transcript =====
{user_query}
===== End transcript =====

Above, you have been provided with a map of a code repository and a transcript \
of a user's verbal query. Provide an answer to the user's question. When you \
have finished, end your message with "TERMINATE", without the quotation marks.
"""

    chat_result = user_proxy.initiate_chat(
        code_interpreter_agent,
        message=task
    )

    return chat_result


def map_directory(item_name, sort_items=True):
    if os.path.isdir(item_name):
        dir_items = [
            item for item in os.listdir(item_name) if item not in config.ignore
            ]

        if sort_items:
            dir_items.sort()
        
        return {item_name: [
            map_directory(item, sort_items) for item in dir_items
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


def get_context(path: Annotated[str, "full path to file or directory"]) -> str:
    item_name = path.split('/')[-1]

    if item_name in config.ignore:
        context = f"\n===== {path} ignored =====\n"
    
    elif os.path.isdir(path):
        context = ""

        for item in os.listdir(path):
            context += get_context(os.path.join(path, item))
    
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

get_context.description = "Provides the full text of a given file, or, if \
    provided with a directory, the full text of every file in the directory. \
    Must be given the full path to the given item."