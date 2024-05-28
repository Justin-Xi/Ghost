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
##########################################################################
self_model = False
sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。如果需要总结，尽量简洁，30字以内。"

# 看消息类型
# input_text = "在微信上帮我看看我的未读消息"
# input_text = "查看一下微信李四的未读消息，把这些消息总结一下飞书发给张三"
# input_text = "看看我飞书上从昨天晚上都现在有哪些未读消息总结一下发到我微信上"

# 发消息类型
# input_text = "给高老师发个微信说明天下午3点有个会"
# input_text = "在飞书上通知赵六，跟他说让他预约一下会议室，后天需要开会，让他跟我一起去"
# input_text = "发个消息给贾扬清让他加我的微信"
# input_text = "给贾扬清发个消息说让他加我的微信"
# input_text = "跟伍哥说我想跟他一起去看电影"
# input_text = "我老婆微信跟我发的会议日程转发给赵经理"
# input_text = "用微信告诉李四今晚在全聚德吃好吃的"
input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发"  # ！！！

# 综合类型
# input_text = "给高老师发个微信说明天下午3点有个会然后查看一下我微信上的未读消息"
# input_text = "看看这一周我吃午饭花了多少钱，把结果微信发给我媳妇"


# input_text = "为什么天空是蓝色的，用科学的方式给我解释一下"
# input_text = "把我在故宫玩的照片分享到朋友圈里，并写一段精彩的描述"
# input_text = "创建一个日程，周日老爸过生日，提前一天提醒我"
# input_text = "帮我定一个酒店，今天晚上的，在王府井附近，便宜一点的"
# input_text = "帮我查一下GPT3.5微调的经验，优先找论文和文献"
# input_text = "帮我点个外卖30分钟能到的，汉堡或者披萨，一人份的"

#common
# input_text = "3+5等于几"
# input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发"
# input_text = "为啥天空是蓝色的"
# input_text = "今天是2020-3-1 10:00:00 ，请问2天前是几号？"
# input_text = "我有三个苹果五个香蕉，吃了一个苹果，还剩几个香蕉？"
# input_text = "床前明月光,疑是地上霜。举头望明月,低头思故乡。把这首诗翻译成英文"
# input_text = "我用GPT3.5做微调，能力退化了，你知道是什么原因导致的吗？"
# input_text = "一个班级40个人，5个班级多少人"
# input_text = "你多大了？"

# test_model_name = "test_004"
# test_model_name = "test_004_4batch"
# test_model_name = "test_007"
# test_model_name = "test_007_bc4"
# test_model_name = "test_007_bc8"
test_model_name = "test_008"
# test_model_name = "test_009"

##########################################################################

if self_model:
    # import tools4dataset as custom_tools
    import tools4dataset_lite as custom_tools
    os.environ['AZURE_OPENAI_API_KEY'] = "a7d194b6355e4b5b83a47979fe20d245"
    os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-eastus2.openai.azure.com/"
else:
    import tools4dataset_zh as custom_tools
    os.environ['AZURE_OPENAI_API_KEY'] = "1b35094b9d7841d083386c76a06d2cff"
    os.environ['AZURE_OPENAI_ENDPOINT'] = "https://loox-northcentralus.openai.azure.com/"


testModel = AzureChatOpenAI(
    deployment_name=test_model_name, openai_api_version="2024-02-15-preview"
)

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

def str_replace(text):
    return text.replace("\"", "'").replace("\n", "；").replace("\t", " ")

def func_call_rt(name):
    if name == "ImReadMsg":
        return str_replace(input_show("请输入看到的消息"))
    return "Done"

def print_rt(rt):
    if 'function_call' in rt.additional_kwargs:
        arguments = rt.additional_kwargs['function_call']['arguments']
        arguments = arguments.replace("\"", "\\\"").replace("\n", " ").replace("\t", " ")
        text = "{\"name\": \"" + rt.additional_kwargs['function_call']['name'] + "\", \"arguments\":\"" + arguments + "\"}"
        print(text)
    else:
        print(rt.content)

def getstr_ai_func_call(msg):
    assert msg.type == "ai"
    assert 'function_call' in msg.additional_kwargs
    arguments = msg.additional_kwargs['function_call']['arguments']
    arguments = arguments.replace("\"", "\\\"").replace("\n", " ").replace("\t", " ")
    text = "{\"name\": \"" + msg.additional_kwargs['function_call']['name'] + "\", \"arguments\":\"" + arguments + "\"}"
    all_text = "{\"role\": \"assistant\", \"function_call\":" + text + "},"
    return all_text

def getstr_function(msg):
    assert msg.type == "function"
    text = "{\"role\": \"function\", \"name\": \""+ msg.name +"\", \"content\": \""+ str_replace(msg.content) +"\"},"
    return text

def getstr_ai_no_func(msg):
    assert msg.type == "ai"
    assert 'function_call' not in msg.additional_kwargs
    text = "{\"role\": \"assistant\", \"content\": \""+ str_replace(msg.content) +"\"}"
    return text

def write_msgs(msgs_list):
    assert msgs_list[0].type == "system"
    assert msgs_list[1].type == "human"
    assert len(msgs_list) > 2
    idx = 2
    text1 = ""
    while 'function_call' in msgs_list[idx].additional_kwargs:
        assert idx+3 <= len(msgs_list)
        assert msgs_list[idx+1].type == "function"
        text1 += getstr_ai_func_call(msgs_list[idx])
        text1 += getstr_function(msgs_list[idx+1])
        idx += 2
    assert idx+1 == len(msgs_list)
    text2 = getstr_ai_no_func(msgs_list[idx])
    text = text1 + "\t" + text2
    with open("D://output.txt", 'w',encoding='utf-8') as f:
        f.write(text)
    return

def add_msgs(msgs_list, msg):
    msgs_list += [msg]

    log_text = str(len(msgs_list)-2) + ":"
    if msg.type == "ai":
        if 'function_call' in msg.additional_kwargs:
            log_text += getstr_ai_func_call(msg)
        else:
            log_text += getstr_ai_no_func(msg)
    elif msg.type == "function":
        log_text += getstr_function(msg)
    else:
        assert False
    print(log_text)

if __name__ == '__main__':

    sys_msg = SystemMessage(
        content=sys_prompt
    )

    # input_text = str_replace(input_show("请输入问题："))

    message = HumanMessage(
            content=str_replace(input_text)
    )

    tools = tool_funcs.funcs(custom_tools)
    functions=[convert_to_openai_function(t) for t in tools]

    if self_model:
        tool_funcs.del_func_paras(functions)
        gptModel = testModel #
        print("=======================微调模型测试===============================", test_model_name)
    else:
        gptModel = gpt35Model   #gpt35Model gpt4Model
        print("***********************gpt***********************************")

    print("0:", input_text)
    msgs_list = [sys_msg,message]
    rt = gptModel(msgs_list, functions=functions)
    # rt = gptModel(msgs_list)
    add_msgs(msgs_list,rt)
    # print_rt(rt)

    while 'function_call' in rt.additional_kwargs:
        func_msg = FunctionMessage(name=rt.additional_kwargs['function_call']['name'], content=func_call_rt(rt.additional_kwargs['function_call']['name']))
        add_msgs(msgs_list, func_msg)
        rt = gptModel(msgs_list, functions=functions)
        add_msgs(msgs_list, rt)
        # print_rt(rt)

    write_msgs(msgs_list)
    print("")

    # with open("C://output.json", 'w',encoding='utf-8') as f:
    #     f.write(text)

