import json
import os
import random

from openai import AzureOpenAI
import tool_funcs
from json import dumps as json_dumps
from langchain_core.utils.function_calling import convert_to_openai_function
from utils.input_wnd import input_show
from auto_check import check_result
from gen_user_prompt import gen_user_prompt_input, gen_user_prompt_function
import tools4dataset_zh as custom_tools
from utils.input_wnd import msg_box

def str_replace(text):
    return text.replace("\"", "'").replace("\n", "；").replace("\t", " ")

def getstr_ai_func_call(msg):
    assert msg.finish_reason == 'function_call'
    function_call = {"name": msg.message.function_call.name, "arguments":msg.message.function_call.arguments}
    if msg.message.content is None:
        return {"role": "assistant", "function_call":function_call}
    else:
        return {"role": "assistant", "function_call":function_call, "content":msg.message.content}

# def getstr_function(msg):
#     assert msg.type == "function"
#     text = "{\"role\": \"function\", \"name\": \""+ msg.name +"\", \"content\": \""+ str_replace(msg.content) +"\"},"
#     return text

def getstr_ai_no_func(msg):
    if msg.finish_reason == 'content_filter':
        return {"role": "assistant", "content": "已完成！"}
    assert msg.finish_reason == 'stop'
    return {"role": "assistant", "content":msg.message.content}

def add_msgs_ai(msgs_list, msg):
    log_text = str(len(msgs_list)-2) + ":"
    if msg.finish_reason == 'function_call':
        rt = getstr_ai_func_call(msg)
        log_text += str(rt)
    else:
        rt = getstr_ai_no_func(msg)
        log_text += str(rt)
    msgs_list += [rt]
    print(log_text)

def add_msgs_func(msgs_list, msg):
    log_text = str(len(msgs_list)-2) + ":"
    log_text += str(msg)
    msgs_list += [msg]
    print(log_text)



def make_msgs_func(para):
    name, text = para
    return {"role": "function", "name": name, "content": text}

def gpt_chat(input_text, sys_prompt, model_name):

    if model_name == "gpt35":
        print("***********************gpt35***********************************")
        api_key = "1b35094b9d7841d083386c76a06d2cff"
        azure_endpoint = "https://loox-northcentralus.openai.azure.com/"
    elif model_name == "gpt4turbo":
        print("=======================gpt4turbo===============================")
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    tools = tool_funcs.funcs(custom_tools)
    functions=[convert_to_openai_function(t) for t in tools]

    print("=:", input_text)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages, functions=functions)
    msg = response.choices[0]
    add_msgs_ai(messages, msg)
    # print(msg.message)
    # print(response.model_dump_json(indent=2))

    while response.choices[0].finish_reason == 'function_call':
        func_msg = make_msgs_func(func_call_rt(msg.message.function_call.name, model_name, messages))
        add_msgs_func(messages, func_msg)
        response = client.chat.completions.create(model=model_name, messages=messages, functions=functions) #,temperature=temperature
        msg = response.choices[0]
        add_msgs_ai(messages, msg)

    check_result(messages)
    print("end")

def func_call_rt(name, model_name, messages):
    if name == "ImReadMsg":
        return name, gen_user_prompt_function(model_name, messages)
        # return name, "李四说你好"
        # return name, "张三说你好"
        # return name, str_replace(input_show("请输入看到的消息"))
    elif name == "LocalOrder":
        return name, "总花费：100元，凉拌菜一份"
    return name, "Done"

if __name__ == '__main__':
    sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。如果需要总结，尽量简洁，30字以内。"
    # sys_prompt = "你的角色是Ghost个人助理"
    # sys_prompt = ""
    # model_name = "gpt4turbo"
    model_name = "gpt35"


    # input_text = "看一下我的未读消息"
    # input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发" #！！！
    # gpt_chat(input_text, sys_prompt, model_name)

    user_inputs = gen_user_prompt_input(model_name)
    input_json = json.loads(user_inputs)
    for con in input_json:
        input_text = con['content']
        if msg_box(text=input_text, cancel_bt="跳过", ok_bt="继续", title="是否使用以下指令继续？"):
            gpt_chat(input_text, sys_prompt, model_name)
