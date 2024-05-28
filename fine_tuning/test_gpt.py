import json
import os
import random

from openai import AzureOpenAI
import tool_funcs
from json import dumps as json_dumps
from langchain_core.utils.function_calling import convert_to_openai_function
from utils.input_wnd import input_show
from auto_check import check_result

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

def gpt_chat(input_text, sys_prompt, model_name, need_check = False):

    if model_name == "gpt35":
        import tools4dataset_zh as custom_tools
        # import tools4dataset_lite as custom_tools
        print("***********************gpt***********************************")
        api_key = "1b35094b9d7841d083386c76a06d2cff"
        azure_endpoint = "https://loox-northcentralus.openai.azure.com/"
    else:
        import tools4dataset_lite as custom_tools
        print("=======================微调模型测试===============================", model_name)
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    tools = tool_funcs.funcs(custom_tools)
    functions=[convert_to_openai_function(t) for t in tools]

    if model_name != "gpt35":
        tool_funcs.del_func_paras(functions)

    # funcs_json = json_dumps(functions)
    # functions = None

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
        func_msg = make_msgs_func(func_call_rt(msg.message.function_call.name))
        add_msgs_func(messages, func_msg)
        response = client.chat.completions.create(model=model_name, messages=messages, functions=functions) #,temperature=temperature
        msg = response.choices[0]
        add_msgs_ai(messages, msg)

    if need_check:
        check_result(messages)
    return messages

def func_call_rt(name):
    if name == "ImReadMsg":
        return name, "李四说你好"
        # return name, "张三说你好"
        # return name, str_replace(input_show("请输入看到的消息"))
    elif name == "LocalOrder":
        return name, "总花费：100元，凉拌菜一份"
    return name, "Done"

if __name__ == '__main__':
    sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。如果需要总结，尽量简洁，30字以内。"
    # sys_prompt = "你的角色是Ghost个人助理"
    # sys_prompt = ""


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
    # input_text = "我老婆微信跟我发的会议日程转发给赵经理" #!!!
    # input_text = "用微信告诉李四今晚在全聚德吃好吃的"

    # 看消息转发
    # input_text = "看看我微信上的未读消息，发给高老师"
    # input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发" #！！！
    input_text = "看一下我钉钉上的未读消息，总结一下发给孙总"
    # input_text = "看一下我钉钉上的未读消息，总结一下飞书发给孙总" #！！！
    # input_text = "看一下高通跟我发的昨天的消息，飞书发给孙总" #！！！
    # input_text = "看一下微信上高老师、杨老师跟我发的昨天的消息，飞书发给孙总、伍哥" #！！！

    # 综合类型
    # input_text = "给高老师发个微信说明天下午3点有个会然后查看一下我微信上的未读消息"
    # input_text = "看看这一周我吃午饭花了多少钱，把结果微信发给我媳妇"
    # input_text = "看看我飞书上有啥未读消息，跟高老师说明天晚上一起去看五道口电影" #！！！
    # input_text = "看看我飞书上有啥未读消息，跟高老师说明天晚上一起去看电影"
    # input_text = "看看我飞书上有啥未读消息，跟高老师说明天一起去公司"


    # input_text = "为什么天空是蓝色的，用科学的方式给我解释一下"
    # input_text = "把我在故宫玩的照片分享到朋友圈里，并写一段精彩的描述"
    # input_text = "创建一个日程，周日老爸过生日，提前一天提醒我"
    # input_text = "帮我定一个酒店，今天晚上的，在王府井附近，便宜一点的"
    # input_text = "帮我查一下GPT3.5微调的经验，优先找论文和文献"
    # input_text = "帮我点个外卖30分钟能到的，汉堡或者披萨，一人份的"
    # input_text = "微信帮我跟张三发个消息，告诉他明天晚上一起吃饭"

    # input_text = "3+5等于几"
    # input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发"
    # input_text = "为啥天空是蓝色的"
    # input_text = "今天是2020-3-1 10:00:00 ，请问2天前是几号？"
    # input_text = "我有三个苹果五个香蕉，吃了一个苹果，还剩几个香蕉？"
    # input_text = "床前明月光,疑是地上霜。举头望明月,低头思故乡。把这首诗翻译成英文"
    # input_text = "我用GPT3.5做微调，能力退化了，你知道是什么原因导致的吗？"
    # input_text = "一个班级40个人，5个班级多少人"
    # input_text = "你多大了？"

    # input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发" #！！！

    # input_text = "看看这几天我吃饭花了多少钱"
    # input_text = "点个KFC的外卖"
    # input_text = "看看这几天我吃饭花了多少钱，要是不到20块钱就点个KFC的外卖，超过20就不要点了"    # gpt4对，gpt35错
    #
    # input_text = "看看我这周的菜单上有水煮鱼么，有的话就在美团上再帮我点一份，没有的话就不要点"   #gpt4错，gpt35错

    # input_text = "请查看一下我的未读消息，如果有关于项目汇报的内容，请帮我转发给王经理。"
    input_text = "看看有没有新消息，如果是关于晚餐的安排，请告诉我，否则转发给小明处理。"
    # input_text = "检查一下我的消息盒子，如果有重要文件请帮我转发给研发部同事。"
    # input_text = "帮我查看一下未读消息，如果发现与下周会议相关的信息，请转交给行政助理处理。"
    # input_text = "请帮我查收一下未读消息，如果有关于客户投诉的内容，请转发给客服部门。"

    # gpt_chat(input_text, sys_prompt, "gpt4turbo")
    gpt_chat(input_text, sys_prompt, "gpt35")
    # gpt_chat(input_text, sys_prompt, "test_029")
    # gpt_chat(input_text, sys_prompt, "test_034")
    # gpt_chat(input_text, sys_prompt, "test_037")
    # gpt_chat(input_text, sys_prompt, "test_036")
