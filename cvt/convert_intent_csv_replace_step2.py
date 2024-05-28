# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 13:37
# software: PyCharm
import random

from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.chat_models import AzureChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, ChatMessage, SystemMessage, FunctionMessage, ToolMessage
from langchain_core.prompts import SystemMessagePromptTemplate, ChatPromptTemplate, PromptTemplate, MessagesPlaceholder, \
    HumanMessagePromptTemplate

from langchain_core.utils.function_calling import convert_to_openai_function
from utils.input_wnd import input_show
import tool_funcs
import os
# init tools
import tools4dataset_zh as custom_tools
from convert_intent_csv_replace_step1 import read_from_txt,write_to_txt,write_to_json
import json
from azure_openai_for_dataset import getstr_ai_no_func


os.environ['AZURE_OPENAI_API_KEY'] = "1b35094b9d7841d083386c76a06d2cff"
os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-northcentralus.openai.azure.com/"
# init agent
gpt35Model = AzureChatOpenAI(
    deployment_name="gpt35", openai_api_version="2024-02-15-preview"
)
gptModel = gpt35Model

# os.environ['AZURE_OPENAI_API_KEY'] = "a7d194b6355e4b5b83a47979fe20d245"
# os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-eastus2.openai.azure.com/"
# gpt4Model = AzureChatOpenAI(
#     deployment_name="gpt4turbo", openai_api_version="2024-02-15-preview"
# )
# gptModel = gpt4Model

gpt4vModel = AzureChatOpenAI(
    deployment_name="gpt4turbo-vision", openai_api_version="2023-12-01-preview"
)

def print_rt(rt):
    print(rt.content)

def json_to_msg_list(sys_msg, user_content,ai_content):
    try:
        user_cont = json.loads(user_content)
        assert user_cont['role'] == 'user'
    except Exception as e:
        print("user json error !!!!")
        assert False

    try:
        ai_cont_list = json.loads("[" + ai_content + "]")
    except Exception as e:
        print("ai json error !!!!")
        assert False


    message = HumanMessage(content=user_cont['content'])
    msgs_list = [sys_msg, message]

    for ai_cont in ai_cont_list:
        if ai_cont['role'] == 'assistant':
            msg1 = AIMessage(content="")
            msg1.additional_kwargs['function_call'] = ai_cont['function_call']
            msgs_list += [msg1]
        elif ai_cont['role'] == 'function':
            msg1 = FunctionMessage(content=ai_cont['content'], name=ai_cont['name'])
            msgs_list += [msg1]
        else:
            assert False

    return msgs_list

def add_ai_summary(base_path, file_name):
    input_filename = base_path + file_name + ".txt"
    output_filename = base_path + file_name + "_" + str(random.randint(1000,10000)) + ".txt"
    # output_json_filename = base_path + file_name + ".jsonl"
    tools = tool_funcs.funcs(custom_tools)
    functions=[convert_to_openai_function(t) for t in tools]
    sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。如果需要总结，尽量简洁，30字以内。这是任务的最后一步不要调用function_call了，直接做总结就可以了。根据函数执行的情况做简要总结，尽量简洁，30字以内。如果有多步需要把多步的内容总结到一起，不要有遗漏。"
    sys_msg = SystemMessage(content=sys_prompt)

    user_content_list, ai_content_list, ai_summary_content_list = read_from_txt(input_filename)
    assert len(user_content_list) > 0
    assert len(user_content_list) == len(ai_content_list) and len(user_content_list) == len(ai_summary_content_list)
    idx = 0
    error_num = 0
    while idx < len(user_content_list):
        if ai_summary_content_list[idx] != "":
            idx += 1
            continue
        msgs_list = json_to_msg_list(sys_msg, user_content_list[idx][:-1], ai_content_list[idx][:-1])

        except_error = False
        try:
            msg = gptModel(msgs_list, functions=functions)
        except Exception as e:
            print("except! try again!")
            except_error = True

        print(idx, user_content_list[idx])
        if except_error or 'function_call' in msg.additional_kwargs:
            print("error to function_call! try again!", error_num)
            error_num += 1
            if error_num > 5:
                print("error to function_call! delete line!", idx)
                del user_content_list[idx], ai_content_list[idx], ai_summary_content_list[idx]
                error_num = 0
            continue
        assert msg.type == "ai"
        print_rt(msg)
        ai_summary_content_list[idx] = getstr_ai_no_func(msg)
        write_to_txt(user_content_list, ai_content_list, ai_summary_content_list, output_filename, False)
        error_num = 0
        idx += 1

    # write_to_json(user_content_list, ai_content_list, ai_summary_content_list, output_json_filename)

if __name__ == '__main__':
    is_base_mix_mode = True
    file_name = "output_01_02_ais"
    base_path = r"G:\Dataset_llm\dataset_intent_openai_replace/output/1_2_2ai/"
    if is_base_mix_mode:
        file_name_mix = file_name + "_mix"
        add_ai_summary(base_path, file_name_mix)
        file_name_base = file_name + "_base"
        add_ai_summary(base_path, file_name_base)
    else:
        add_ai_summary(base_path, file_name)
