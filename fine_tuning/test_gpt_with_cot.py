import json
import os
import random

from openai import AzureOpenAI
import tool_funcs
import json
from langchain_core.utils.function_calling import convert_to_openai_function
from utils.input_wnd import input_show
from auto_check import check_result
from fine_tuning.gen_user_prompt import gen_user_prompt_function

def str_replace(text):
    return text.replace("\"", "'").replace("\n", "；").replace("\t", " ")

def getstr_ai_rt(msg):
    if msg.finish_reason == 'content_filter':
        return {"role": "assistant", "content": "已完成！"}
    assert msg.finish_reason == 'stop'
    return {"role": "assistant", "content":msg.message.content}

def add_msgs_ai(msgs_list, msg, ai_type, ai_json):
    log_text = "==" + str(len(msgs_list)) + "==" + ai_type + ":"
    if ai_type == 'func_call':
        rt = getstr_ai_rt(msg)
        log_text += str(rt)
    else:
        rt = getstr_ai_rt(msg)
        log_text += str(rt)
    msgs_list += [rt]
    print(log_text)

def add_msgs_user(msgs_list, msg):
    log_text = "==" + str(len(msgs_list)) + "==user:"
    log_text += str(msg)
    msgs_list += [msg]
    print(log_text)



def make_msgs_user(para):
    name, text = para
    return {"role": "user", "content": text}

def cvt_one_msg(line, keyword_list):
    for kwd in keyword_list:
        if line.startswith(kwd):
            key = line[:len(kwd)][2:-3] #remove <| |>:
            value = line[len(kwd):]
            if key == "Action" or key == "Observation": #json
                js_value = json.loads(value)
                return key, js_value
            else:
                return key, value
    return None

def cvt_ai_msg_to_json(text):
    keyword_list = ["<|Task|>:","<|Thought|>:","<|Action|>:","<|Observation|>:","<|Final_Answer|>:"]
    spe_flag = "<#|#|#>"
    assert text.find(spe_flag) < 0
    text = text.replace(spe_flag, "")
    for kwd in keyword_list:
        text = text.replace(kwd, spe_flag+kwd)
    lines = text.split(spe_flag)
    jsons = {}
    for line in lines:
        if line == "":
            continue
        key, value = cvt_one_msg(line, keyword_list)
        jsons[key] = value
    return jsons

def get_ai_msg_type(msg):
    if msg.finish_reason == 'content_filter':
        print("触发了奇怪的敏感词汇，请重试或换个说法！")
        return 'error'
    assert msg.finish_reason == 'stop'
    text = msg.message.content
    ai_json = cvt_ai_msg_to_json(text)
    if 'Task' in ai_json or 'Observation' in ai_json:
        print("error ai msg:", ai_json)
        return "error", ai_json
    elif 'Thought' in ai_json and 'Action' in ai_json:
        return "func_call", ai_json
    elif 'Thought' in ai_json and 'Final_Answer' in ai_json:
        return "final", ai_json
    else:
        return "error", ai_json

def gpt_chat(input_text, sys_prompt, model_name, need_check = False):

    if model_name == "gpt35":
        import tools4dataset_zh as custom_tools
        # import tools4dataset_lite as custom_tools
        print("***********************gpt35***********************************")
        api_key = "1b35094b9d7841d083386c76a06d2cff"
        azure_endpoint = "https://loox-northcentralus.openai.azure.com/"
    elif model_name == "gpt4turbo":
        import tools4dataset_zh as custom_tools
        # import tools4dataset_lite as custom_tools
        print("***********************gpt4***********************************")
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
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

    # tools = tool_funcs.funcs(custom_tools)
    # functions=[convert_to_openai_function(t) for t in tools]
    functions = tool_funcs.funcs_json(custom_tools)

    # if model_name != "gpt35" and model_name != "gpt4turbo":
    #     tool_funcs.del_func_paras(functions)

    funcs_json = json.dumps(functions, ensure_ascii=False)
    # functions = None

    sys_prompt += "[函数列表]=\"\"\"\n" + funcs_json
    sys_prompt += "\n\n开始推理！"

    print("==1==user:", input_text)

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages)
    msg = response.choices[0]
    ai_type, ai_json = get_ai_msg_type(msg)
    add_msgs_ai(messages, msg, ai_type, ai_json)

    while ai_type == "func_call":
        func_msg = make_msgs_user(func_call_rt(ai_json['Action'][0]['name'], model_name, messages))
        add_msgs_user(messages, func_msg)
        response = client.chat.completions.create(model=model_name, messages=messages, functions=functions) #,temperature=temperature
        msg = response.choices[0]
        ai_type, ai_json = get_ai_msg_type(msg)
        add_msgs_ai(messages, msg, ai_type, ai_json)

    if ai_type != "final":
        return None

    if need_check:
        check_result(messages)
    return messages

def func_call_rt(name, model_name, messages):
    if name == "ImReadMsg":
        value = gen_user_prompt_function(model_name, messages)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == 'ImSendMsg':
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"消息已发送\"}]}"
    return name, "Done"

if __name__ == '__main__':
    # sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。在每一步调用function call时，加入思维链，描述当前处境和下一步行动的原因，并说明自己的下一步行动，思维过程放在content字段中。如果需要总结，尽量简洁，30字以内。"
    filename = "../cfg/system_prompt.txt"
    with open(filename, 'r', encoding='utf-8') as f:
        sys_prompt = f.read()

    # 看消息类型
    input_text = "在微信上帮我看看高老师昨天发给我的消息"
    # input_text = "给高老师发个微信"
    # input_text = "给高老师和李老板发个微信说明天下午3点有个会"
    # input_text = "在飞书上通知赵六，跟他说让他预约一下会议室，后天需要开会，让他跟我一起去"
    # input_text = "发个消息给贾扬清让他加我的微信"
    # input_text = "给贾扬清发个消息说让他加我的微信"
    # input_text = "跟伍哥说我想跟他一起去看电影"
    # input_text = "我老婆微信跟我发的会议日程转发给赵经理" #!!!
    # input_text = "用微信告诉李四今晚在全聚德吃好吃的"
    # input_text = "看看我微信上的未读消息，要是有张三发的消息就转发给高老师，没有的话就不发"


    input_text = "<|Task|>:" + input_text

    gpt_chat(input_text, sys_prompt, "gpt4turbo")
    # gpt_chat(input_text, sys_prompt, "gpt35")
