# -*- coding:utf-8 -*-
# author:xiajiayi
# datetime:2024/1/24 13:37
# software: PyCharm
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
# os.environ['AZURE_OPENAI_API_KEY'] = "1b35094b9d7841d083386c76a06d2cff"
# os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-northcentralus.openai.azure.com/"

os.environ['AZURE_OPENAI_API_KEY'] = "a7d194b6355e4b5b83a47979fe20d245"
os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-eastus2.openai.azure.com/"


# init agent
gpt35Model = AzureChatOpenAI(
    deployment_name="gpt35", openai_api_version="2024-02-15-preview"
)

gpt4Model = AzureChatOpenAI(
    deployment_name="gpt4turbo", openai_api_version="2024-02-15-preview"
)

gpt4vModel = AzureChatOpenAI(
    deployment_name="gpt4turbo-vision", openai_api_version="2023-12-01-preview"
)

def print_rt(rt):
    print(rt.content)

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        sys_prompt = f.read()
    return sys_prompt


if __name__ == '__main__':

    # sys_prompt = "你是一个翻译助手，请按照如下规则来完成事项，只输出json结果；1、识别下面句子是什么语言 2、列出下面句子里的表示名字、商品的名词，并给出英文原文对照表；" \
    #              "3、将下面句子翻译成英文；4、以json的格式输出，格式为{\"language\":语言,\"translation\":翻译内容,\"wordlist\":[英文原文对照表]}"
    # input_text = "请飞书给Icy王发个消息， 我想和她一起去买个new balance鞋。"
    #
    #
    # sys_prompt = "你是一个翻译助手，请把下面句子translation中的内容翻译成language字段规定的语言，wordlist中包含的单词需要严格按照对应关系翻译"
    # input_text = "{\"language\":\"Chinese\",\"translation\":\"Please send a message to Icy Wang via Feishu, I want to go with her to buy a pair of New Balance shoes.\"," \
    #              "\"wordlist\":[{\"Chinese\":\"飞书\",\"English\":\"Feishu\"},{\"Chinese\":\"Icy王\",\"English\":\"Icy Wang\"},{\"Chinese\":\"new balance鞋\",\"English\":\"New Balance shoes\"}]}"

    # sys_prompt = "你是一个翻译助手，下面是一个中文写的system prompt，请将他翻译成英文，并且保证达到同样的system prompt含义"
    # # sys_prompt = "你是一个翻译助手，下面是一个英文写的system prompt，请将他翻译成中文，并且保证达到同样的system prompt含义"
    # input_text = read_file("cfg/system_prompt_en.txt")
    # # input_text = "开始推理！"

    sys_prompt = "你是一个翻译助手，请把下面的函数描述翻译成英语"
    input_text = "[函数列表]中description字段是函数或参数的详细描述，调用时需要认真查看，遵循里面定义的规则；required字段列出的是必填参数，如果用户任务描述没有提供足够的信息，需要再次追问，required字段没有列出的参数是可以忽略的参数，不要再问。"

    sys_msg = SystemMessage(
        content=sys_prompt
    )

    # input_text = str_replace(input_show("请输入问题："))

    message = HumanMessage(
            content=input_text
    )

    # gptModel = gpt35Model   #gpt35Model gpt4Model
    gptModel = gpt4Model   #gpt35Model gpt4Model
    print("***********************gpt***********************************")

    msgs_list = [sys_msg,message]
    rt = gptModel(msgs_list)
    print_rt(rt)
