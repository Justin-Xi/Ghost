import copy
import json
# from cvt.cvt_llama3_from_json import gpt_chat_json_to_json
# from evaluation.ghost_evaluation import *
import shutil
import tkinter as tk
import os
from tkinter import filedialog
from openai import AzureOpenAI
import binascii
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
from datetime import datetime
import csv
import tools4dataset_zh as custom_tools_zh
import tools4dataset_en as custom_tools_en
from tool_funcs import *
from langchain_core.utils.function_calling import convert_to_openai_function

gpt_model_name = "gpt4-32k" # gpt4-32k gpt4turbo

#######################################为了不依赖任何文件把函数都粘过来了#######################################################


def encrypt(data):
    # 参数key: 秘钥，要求是bytes类型，并且长度必须是16、24或32 bytes，因为秘钥的长度可以为：128位、192位、256位
    # 参数mode: 加密的模式，有ECB、CBC等等，最常用的是CBC
    # 参数iv: 初始向量，是CBC加密模式需要的初始向量，类似于加密算法中的盐
    # 创建用于加密的AES对象
    cipher1 = AES.new(key, AES.MODE_CBC, iv)
    # 使用对象进行加密，加密的时候，需要使用pad对数据进行填充，因为加密的数据要求必须是能被128整除
    # pad参数内容，第一个是待填充的数据，第二个是填充成多大的数据，需要填充成128位即16bytes
    ct = cipher1.encrypt(pad(data, 16))
    # 将加密后的结果（二进制）转换成十六进制的或者其它形式
    ct_hex = binascii.b2a_hex(ct)
    return ct_hex


def decrypt(ct_hex):
    # 创建用于解密的AES对象
    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    # 将十六进制的数据转换成二进制
    hex_data = binascii.a2b_hex(ct_hex)
    # 解密完成后，需要对数据进行取消填充，获取原来的数据
    pt = unpad(cipher2.decrypt(hex_data), 16)
    return pt


key = b"TinRdLne20240516@)@$)%!^"
iv = b"v9dl4dfkvorvisl4"

def encrypt_str(text):
    texts_byte = text.encode('utf-8')
    enc_data = encrypt(texts_byte)
    return enc_data

def decrypt_str(data):
    dec_data = decrypt(data)
    text = dec_data.decode('utf-8')
    return text

def split_file_ex(file_name):
    pos = file_name.rfind('.')
    if pos < 0:
        return file_name,""
    return file_name[:pos],file_name[pos+1:]


def encrypt_file(file_name, out_file = None, ext=".cbin"):
    with open(file_name, 'r', encoding='utf-8') as f:
        texts_json = f.read()
    enc_data = encrypt_str(texts_json)
    if out_file is None:
        file_out,_ = split_file_ex(file_name)
        file_out += ext
    else:
        file_out = out_file
    with open(file_out, 'wb') as f:
        f.write(enc_data)
    return file_out


def decrypt_file(file_name, out_file = None, ext=".json"):
    with open(file_name, 'rb') as f:
        enc_data = f.read()
    dec_text = decrypt_str(enc_data)
    if out_file is None:
        file_out,_ = split_file_ex(file_name)
        file_out += "_decry" + ext
    else:
        file_out = out_file
    with open(file_out, 'w', encoding='utf-8') as f:
        f.write(dec_text)
    return file_out

def open_file_auto(file_name, crypt_ext=".cbin", json_ext=".json"):
    if not os.path.exists(file_name):
        print("文件不存在：", file_name)
        return ""
    if file_name.endswith(crypt_ext):
        with open(file_name, 'rb') as f:
            enc_data = f.read()
        dec_text = decrypt_str(enc_data)
        return dec_text
    elif file_name.endswith(json_ext):
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read()

    print("未知的文件类型：", file_name)
    return ""

def save_file_crypt(texts_json, file_name):
    enc_data = encrypt_str(texts_json)
    with open(file_name, 'wb') as f:
        f.write(enc_data)

def encrypt_path(path_name, out_path, crypt_ext=".cbin", json_ext=".json"):
    os.makedirs(out_path, exist_ok=True)
    for parent, dirnames, filenames in os.walk(path_name):
        for filename in filenames:  #
            if filename.endswith(json_ext):
                out_file,_ = split_file_ex(filename)
                encrypt_file(os.path.join(parent, filename), os.path.join(out_path, out_file+crypt_ext), ext=crypt_ext)
                print("encrypt:",os.path.join(parent, filename))

def decrypt_path(path_name, out_path, crypt_ext=".cbin", json_ext=".json"):
    os.makedirs(out_path, exist_ok=True)
    for parent, dirnames, filenames in os.walk(path_name):
        for filename in filenames:  #
            if filename.endswith(crypt_ext):
                out_file,_ = split_file_ex(filename)
                decrypt_file(os.path.join(parent, filename), os.path.join(out_path, out_file+json_ext), ext=json_ext)
                print("decrypt:",os.path.join(parent, filename))

##########################################################################################################################

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def write_log(filename, text):
    with open(filename, 'a', encoding='utf-8') as f:
        print(text)
        f.write(text + "\n")


def str_to_json(text):
    try:
        js_value = json.loads(text)
        return js_value
    except Exception as e:
        print("str_to_json json error:", e)
        return None

def cvt_one_msg(line, keyword_list):
    for kwd in keyword_list:
        if line.startswith(kwd):
            key = line[:len(kwd)][2:-3] #remove <| |>:
            value = line[len(kwd):].strip()
            if key == "Action" or key == "Observation": #json
                try:
                    js_value = json.loads(value)
                    return key, js_value
                except Exception as e:
                    print("cvt_one_msg json error:", value)
                    return key, None
            else:
                return key, value
    print("cvt_one_msg json ignore:", line)
    return None, None

def cvt_ai_msg_to_json(text):
    keyword_list = ["<|Task|>:","<|Thought|>:","<|Action|>:","<|Observation|>:","<|Final_Answer|>:"]
    spe_flag = "<#|#|#>"
    # assert text.find(spe_flag) < 0
    text = text.replace(spe_flag, "<#| |#>")
    for kwd in keyword_list:
        text = text.replace(kwd, spe_flag+kwd)
    lines = text.split(spe_flag)
    jsons = {}
    for line in lines:
        if line.strip() == "":
            continue
        key, value = cvt_one_msg(line, keyword_list)
        if key is None:
            continue
        if value is None:
            return None
        jsons[key] = value
    return jsons

def getstr_ai_rt(msg):
    if msg.finish_reason == 'content_filter':
        return {"role": "assistant", "content": "content filter"}
    # assert msg.finish_reason == 'stop'
    return {"role": "assistant", "content":msg.message.content}

def getstr_ai_rt_tool(msg):
    if msg.finish_reason == 'content_filter':
        print("error content filter!")
        return None
    # assert msg.finish_reason == 'stop'
    return {'from': 'gpt', 'value':msg.message.content}

def print_content(text):
    text = text.replace("<|Action|>:","\n\t\t<|Action|>:").replace("<|Final_Answer|>:","\n\t\t<|Final_Answer|>:").replace("<|Thought|>:","\n\t\t<|Thought|>:")
    print(text)

def add_msgs_ai(msgs_list, msg, ai_type, ai_json):
    log_text = "==" + str(len(msgs_list)) + "==" + ai_type + ":"
    if ai_type == 'func_call':
        rt = getstr_ai_rt(msg)
        log_text += rt["content"]
    else:
        rt = getstr_ai_rt(msg)
        log_text += rt["content"]
    msgs_list += [rt]
    print_content(log_text)

def add_msgs_user(msgs_list, msg):
    log_text = "==" + str(len(msgs_list)) + "==user:"
    log_text += str(msg)
    msgs_list += [msg]
    print(log_text)

def make_msgs_user(para):
    name, text = para
    return {"role": "user", "content": text}

def to_sharegpt_format(messages):
    gpt_msgs = {}
    conversations = []
    for msg in messages:
        if msg['role'] == 'system':
            gpt_msgs['system'] = msg['content']
        elif msg['role'] == 'user':
            value = {"from": "human", "value": msg['content']}
            # assert len(conversations) % 2 == 0
            conversations.append(value)
        elif msg['role'] == 'assistant':
            value = {"from": "gpt", "value": msg['content']}
            # assert len(conversations) % 2 == 1
            # assert conversations[-1]["from"] == "human"
            conversations.append(value)

    # assert len(conversations) % 2 == 0
    if conversations is not None:
        gpt_msgs['conversations'] = conversations
    return gpt_msgs


def safe_chat_create_with_retry(client, model, messages, retry_times=2):
    for i in range(retry_times):
        try:
            response = client.chat.completions.create(model=model, messages=messages)
            msg = response.choices[0]
            if msg.finish_reason == 'content_filter':
                print("error!content_filter 1!")
                continue
            return msg
        except Exception as e:
            print("error!content_filter 2!")
            continue
    return None

def get_ai_msg_type(msg):
    if msg.finish_reason == 'content_filter':
        print("触发了奇怪的敏感词汇，请重试或换个说法！")
        return 'error',None
    # assert msg.finish_reason == 'stop'
    text = msg.message.content
    ai_json = cvt_ai_msg_to_json(text)
    if ai_json is None:
        print("json 解析错误！")
        return 'error',None
    if 'Task' in ai_json or 'Observation' in ai_json:
        print("error ai msg:", text)
        return "error", ai_json
    elif 'Thought' in ai_json and 'Action' in ai_json:
        return "func_call", ai_json
    elif 'Thought' in ai_json and 'Final_Answer' in ai_json:
        return "final", ai_json
    else:
        print("error ai msg:", text)
        return "error", ai_json

def get_user_msg(messages):
    for msg in messages:
        if msg['role'] == 'user':
            return msg['content']

    assert False
    return ""

def str_replace(text):
    if text is not None:
        return text.replace("\"", "'").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("/", " ").replace("\b", " ").replace("\f", " ")
    else:
        print("Error: text is None")
        return ""
    # return text.replace("\"", "'").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("/", " ").replace("\b", " ").replace("\f", " ")

def gen_user_prompt_function(model_name, is_english, messages):
    model_name = gpt_model_name    # only gpt4 can do

    if model_name == gpt_model_name:
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    if is_english:
        sys_prompt = "You are a messaging application simulator, simulating IM tools like whatsapp, generating one or two seen messages, not too long, such as  \"John says hello\" Do not copy the answer verbatim, return a creative response, it can be daily life content, work content, etc. Only output the message that IM should output, do not output other content, such as system prompts, apologies, unable to provide service, etc., do not output the operations that should be performed. Note: It's just a simulation, there's no need to actually query, the output content doesn't need to be real."
    else:
        sys_prompt = "你是一个消息应用程序模拟器，模拟whatsapp这样的IM工具，生成一条或两条看到的消息，不要太长，如“张三说你好”，不要照抄答案，要返回有创意的回答，可以是日常生活内容、工作内容等。只输出IM应该输出的消息，不要输出其他内容，如系统提示、对不起、不能提供服务等，不要输出应该进行的操作。注意：只是模拟，不需要真正的去查询，输出的内容不需要是真实的。"
    # if random.randint(0,1) == 0:
    #     print("符合条件回答")
    #     sys_prompt += "如果消息中包含一个条件操作，你要生成一个符合这个条件的回答。"
    # elif random.randint(0,1) == 0:
    #     print("不符合条件回答")
    #     sys_prompt += "如果消息中包含一个条件操作，你要生成一个不符合这个条件的回答。"
    # else:
    #     print("无关回答")
    #     sys_prompt += "如果消息中包含一个条件操作，你要生成一个跟这个条件完全无关的回答。"

    input_text = get_user_msg(messages)

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages)
    msg = response.choices[0]
    print(msg.message.content)
    return str_replace(msg.message.content)


def gen_ai_function(model_name, is_english, action):
    model_name = gpt_model_name    # only gpt4 can do

    if model_name == gpt_model_name:
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    if is_english:
        sys_prompt = "You are an AI generation assistant that helps users generate content. The generated content should be as short as possible, within 100 words."
    else:
        sys_prompt = "你是一个AI生成助手，帮用户生成内容，生成内容尽量简短，100字以内。"

    # input_text = get_user_msg(messages)
    input_text = ""
    if 'parameters' in action and 'Msg' in action['parameters']:
        input_text = action['parameters']['Msg']

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages)
    msg = response.choices[0]
    print(msg.message.content)
    return str_replace(msg.message.content)

def network_search_function(model_name, is_english, action):
    model_name = gpt_model_name    # only gpt4 can do

    if model_name == gpt_model_name:
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    if is_english:
        sys_prompt = "You are a web search simulator that helps users generate web search content that is as short as possible and within 100 words."
    else:
        sys_prompt = "你是网络搜索模拟器，帮用户生成网络搜索内容，内容尽量简短，100字以内。"

    # input_text = get_user_msg(messages)
    input_text = ""
    if 'parameters' in action and 'Msg' in action['parameters']:
        input_text = action['parameters']['Msg']

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages)
    msg = response.choices[0]
    print(msg.message.content)
    return str_replace(msg.message.content)

def message_search_function(model_name, is_english, action):
    model_name = gpt_model_name    # only gpt4 can do

    if model_name == gpt_model_name:
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    if is_english:
        sys_prompt = "You are a web search simulator that helps users generate web search content that is as short as possible and within 100 words."
    else:
        sys_prompt = "你是用户信息读取或搜索模拟器，帮用户生成聊天消息,聊天消息中可能包括图片、视频、语音、路线信息等，需要模拟出这些内容，并给出ID，模拟尽量真实，内容尽量简短，100字以内，不能出现‘模拟内容’等字样。ID格式为：ID=xxxxx-xxxxx-xxxxx-xxxxx,xxxxx是随机的字母或数字"

    # input_text = get_user_msg(messages)
    input_text = ""
    if 'parameters' in action:
        input_text = "要求的读取或搜索条件如下,根据这些条件生成模拟内容：" + json.dumps(action['parameters'], ensure_ascii=False)

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    response = client.chat.completions.create( model=model_name, messages=messages)
    msg = response.choices[0]
    print(msg.message.content)
    return str_replace(msg.message.content)

def func_call_rt(action, model_name, is_english, messages):
    name = action['name']
    if name == "ImReadMsg":
        value = gen_user_prompt_function(model_name, is_english, messages)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == 'ImSendMsg':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The message has been sent\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"消息已发送\"}]}"
    elif name == 'NoteCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The note has been created\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"便签已创建\"}]}"
    elif name == 'NoteModify':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The note has been modified\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"便签已修改\"}]}"
    elif name == 'NoteDelete':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The note has been deleted\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"便签已删除\"}]}"
    elif name == 'ScheduleCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The schedule has been created\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"日程已创建\"}]}"
    elif name == 'ScheduleModify':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The schedule has been modified\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"日程已修改\"}]}"
    elif name == 'ScheduleDelete':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The schedule has been deleted\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"日程已删除\"}]}"
    elif name == 'TodoCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The todo has been created\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"待办已创建\"}]}"
    elif name == 'TodoModify':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The todo has been modified\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"待办已修改\"}]}"
    elif name == 'TodoDelete':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The todo has been deleted\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"待办已删除\"}]}"
    elif name == "AIGenerate":
        value = gen_ai_function(model_name, is_english, action)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == "NetworkSearch":
        value = network_search_function(model_name, is_english, action)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == "MessageSearch":
        value = message_search_function(model_name, is_english, action)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == 'ContactCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"Contact created successfully\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"联系人已创建\"}]}"
    else:
        print("NotImplementedError:The function for action name '{}' is not implemented.".format(name))
        return name, "UnDone"

def gpt_chat(messages, is_english, model_name, need_check = False):

    if model_name == gpt_model_name:
        print("******gpt4******")
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    msg = safe_chat_create_with_retry(client, model=model_name, messages=messages, retry_times=2)
    if msg is None:
        return False, messages
    ai_type, ai_json = get_ai_msg_type(msg)
    add_msgs_ai(messages, msg, ai_type, ai_json)

    while ai_type == "func_call":
        # ai_json['Action']=[]
        if 'Action' in ai_json and ai_json['Action']:
            func_msg = make_msgs_user(func_call_rt(ai_json['Action'][0], model_name, is_english, messages))
            if 'UnDone' in func_msg['content']:
                return False, messages
            add_msgs_user(messages, func_msg)
            # response = client.chat.completions.create(model=model_name, messages=messages, functions=functions) #,temperature=temperature
            msg = safe_chat_create_with_retry(client, model=model_name, messages=messages, retry_times=2)
            if msg is None:
                return False, messages
            ai_type, ai_json = get_ai_msg_type(msg)
            add_msgs_ai(messages, msg, ai_type, ai_json)

    if ai_type != "final":
        return False, messages

    return True, messages

def gpt_chat_with_try(messages, is_english, model_name, need_check = False, try_times = 3):
    for i in range(try_times):
        rt, messages = gpt_chat(messages, is_english, model_name, need_check)
        if rt:
            return True, messages
        print("============error try================", i, "============================")

    return False, messages

def gpt_chat_json_to_json(json_line):
    sys_prompt = json_line['system']
    messages = [
        {"role": "system", "content": sys_prompt},
    ]
    row_num = len(json_line['conversations'])
    if len(json_line['conversations']) > 0:
        user_prompt = json_line['conversations'][0]
        assert user_prompt['from'] == 'human'
        input_text = user_prompt['value']
        func_msg = make_msgs_user(("human", input_text))
        add_msgs_user(messages, func_msg)
        is_english = sys_prompt.startswith("You are a tool invocation expert. ")
        rt, messages = gpt_chat_with_try(messages, is_english, gpt_model_name, need_check = False, try_times = 3)
        if not rt:
            print("=======error==============")
    messages = to_sharegpt_format(messages)
    return messages

def cvt_json_to_msg_json(json_line):
    sys_prompt = json_line['system']
    messages = [
        {"role": "system", "content": sys_prompt},
    ]
    for msg in json_line['conversations']:
        if msg['from'] == 'human':
            messages.append({"role": "user", "content": msg['value']})
        elif msg['from'] == 'gpt':
            messages.append({"role": "assistant", "content": msg['value']})
        else:
            assert False
    return messages

def gpt_chat_json_to_json_one_step(json_line):
    messages = cvt_json_to_msg_json(json_line)
    if len(messages) <= 1:
        print("错误的json格式", json_line)
        return None
    last_msg = messages[-1]
    model_name = gpt_model_name
    if last_msg['role'] == 'user':
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
        client = AzureOpenAI(
            api_key=api_key,
            api_version="2024-02-15-preview",
            azure_endpoint=azure_endpoint
        )
        msg = safe_chat_create_with_retry(client, model=model_name, messages=messages, retry_times=2)
        if msg is None:
            print("GPT返回错误！", json_line)
            return None
        ai_json = getstr_ai_rt_tool(msg)
        return ai_json
    elif last_msg['role'] == 'assistant':
        is_english = messages[0]['content'].startswith("You are a tool invocation expert. ")
        ai_json = cvt_ai_msg_to_json(last_msg['content'])
        if 'Final_Answer' in ai_json:
            return {"from": "human", "value": "<|Task|>: "}
        elif 'Action' in ai_json:
            _,value = func_call_rt(ai_json['Action'][0], model_name, is_english, messages)
            return {"from": "human", "value":value}
        else:
            print("GPT返回错误！", json_line)
            return None
    else:
        assert False
        return None

##############################################################################################
text_pad = 5
bt_pad = 20
label_width = 10
text_width = 200
text_height = 2
sys_bt_pad = 25

need_save = False


def on_text_change(event):
    global need_save
    need_save = True


def sys_wnd(root, text):
    frame = tk.LabelFrame(root,text="system prompt")
    frame.pack(padx=text_pad, pady=text_pad)

    tk_label = tk.Label(frame, text='System', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame, width=text_width, height=3)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.insert('insert', text)
    # scroll = tk.Scrollbar(frame)
    # scroll.config(command=tk_text.yview)
    # scroll.pack(side=tk.RIGHT, fill=tk.Y)
    # tk_text.config(yscrollcommand=scroll.set)
    return

def get_func_name(name):
    if name == "ImSendMsg":
        return "发送消息","blue"
    elif name == "ImReadMsg":
        return "看消息","green"
    elif name == "NoteCreate":
        return "创建便签","orange"
    elif name == "NoteModify":
        return "修改便签","green"
    elif name == "NoteDelete":
        return "删除便签","blue"
    elif name == "ScheduleCreate":
        return "创建日程","orange"
    elif name == "ScheduleModify":
        return "修改日程","green"
    elif name == "ScheduleDelete":
        return "删除日程","blue"
    elif name == "TodoCreate":
        return "创建待办","orange"
    elif name == "TodoModify":
        return "修改待办","green"
    elif name == "TodoDelete":
        return "删除待办","blue"
    elif name == "AIGenerate":
        return "AI内容生成","#22ff00"
    elif name == "NetworkSearch":
        return "网络搜索","#22aa22"
    elif name == "MessageSearch":
        return "消息搜索","#22dd22"
    elif name == "ContactCreate":
        return "创建联系人","orange"
    else:
        print("未知的函数名：", name)
        return "","#00ff00"

def list_to_str(json_x):
    # assert isinstance(json_x, list)
    if not isinstance(json_x,list):
        assert isinstance(json_x,str)
        return json_x

    text = ""
    for js in json_x:
        if text != "":
            text += ","
        text += js
    return text

def str_to_list(text):
    text = text.replace("，",",")
    str_list = text.split(",")
    str_list2 = []
    for s in str_list:
        s = s.strip()
        if len(s) > 0:
            str_list2.append(s)
    return str_list2

def ai_func_chdwnd_msg(frame_chd, json_vl, text_map, text_key, func_para, name_ex = ""):
    frame_chd1 = tk.Frame(frame_chd)
    frame_chd1.pack()
    func_para_list, func_para_type, func_para_len =  list(zip(*func_para))
    func_name, label_color = get_func_name(json_vl['name'])
    tk_label = tk.Label(frame_chd1, text= func_name + ":" + json_vl['name'] + ":" + name_ex, foreground=label_color)
    tk_label.pack()
    if 'parameters' in json_vl:
        paras = copy.deepcopy(json_vl['parameters'])
        for k in paras:
            if k not in func_para_list:
                del json_vl['parameters'][k]
                global need_save
                need_save = True
                print("发现多余参数：", k)

    frame_chd1 = tk.Frame(frame_chd)
    frame_chd1.pack()

    chd_text_width = 15
    for idx,k in enumerate(func_para_list):
        if idx == 6:
            frame_chd1 = tk.Frame(frame_chd)
            frame_chd1.pack()
        frame_chd2 = tk.Frame(frame_chd1)
        frame_chd2.pack(side=tk.LEFT)

        tk_label = tk.Label(frame_chd2, text=k)
        tk_label.pack(padx=5)

        tk_text = tk.Text(frame_chd2, width=chd_text_width * func_para_len[idx], height=2)
        tk_text.pack(padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
        tk_text.bind("<Key>", on_text_change)
        text_map[text_key + "_" + k] = tk_text
        if 'parameters' in json_vl and k in json_vl['parameters']:
            if func_para_type[idx] is list:
                tk_text.insert('insert', list_to_str(json_vl['parameters'][k]))
            elif func_para_type[idx] is bool:
                tk_text.insert('insert', str(json_vl['parameters'][k]))
            else:
                # assert isinstance(json_vl['parameters'][k], str)
                tk_text.insert('insert', json_vl['parameters'][k])

def merge_ai_func_chdwnd_msg(json_vl, text_map, text_key, func_para):
    func_para_list, func_para_type, _ =  list(zip(*func_para))
    func_map = {}
    func_map['name'] = json_vl['name']
    para_map = {}
    for idx,k in enumerate(func_para_list):
        value_cha = get_text_value(text_map[text_key + "_" + k])
        if len(value_cha) > 0:
            if func_para_type[idx] is list:
                para_map[k] = str_to_list(value_cha)
            elif func_para_type[idx] is bool:
                para_map[k] = value_cha.lower() == "true"
            else:
                para_map[k] = value_cha
    func_map['parameters'] = para_map
    return func_map

def get_dict_para(json_func, para_name):
    json_new = {}
    if 'parameters' in json_func and para_name in json_func['parameters']:
        json_new['name'] = json_func['name']
        json_new['parameters'] = json_func['parameters'][para_name]
        return json_new
    else:
        return None

def get_merge_para(json_list):
    if len(json_list) == 0:
        return None
    json_new = {}
    for js in json_list:
    # if 'parameters' in json_list[0]:
        json_new['name'] = json_list[js]['name']
        if 'parameters' not in json_new:
            json_new['parameters'] = {}
        json_new['parameters'][js] = json_list[js]['parameters']
    return json_new

def ai_func_wnd(root, json_vl, text_map, text_key):
    frame = tk.LabelFrame(root,text="ai action")
    frame.pack(padx=text_pad, pady=text_pad)
    frame_chd1 = tk.Frame(frame)
    frame_chd1.pack()
    frame_chd2 = tk.Frame(frame)
    frame_chd2.pack(side=tk.LEFT)
    tk_label = tk.Label(frame_chd1, text='Thought', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame_chd1, width=text_width, height=text_height)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    if 'Thought' in json_vl:
        tk_text.insert('insert', json_vl['Thought'])
    text_map[text_key+"_"+"Thought"] = tk_text

    # tk_label = tk.Label(frame_chd2, text='Action', width=label_width)
    # tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    # if len(json_vl['Action']) > 1:
    #     print("warning! 函数列表中有多个函数，多余的部分被忽略了", json_vl)
    for idx,json_func in enumerate(json_vl['Action']):
        frame_chd22 = tk.Frame(frame_chd2)
        frame_chd22.pack(padx=5, pady=5, ipadx=5)
        if json_func['name'] == 'ImSendMsg':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [['App',str,1],['Receiver',list,2],['Msg',str,4],["Time",list,1],["Location",list,1]]) # 类型 #文本框长度
        elif json_func['name'] == 'ImReadMsg':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["App",str,1],["Sender",list,2],["Type",str,1],["Time",list,2],['Msg',str,3]])
        elif json_func['name'] == 'NoteCreate':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
        elif json_func['name'] == 'NoteModify':
            para_chdname = 'QueryCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]],"查询条件")
            else:
                print("参数未找到", para_chdname)
            para_chdname = 'NewContent'
            json_change = get_dict_para(json_func, para_chdname)
            if json_change is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_change, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]], "修改内容")
            else:
                print("参数未找到", para_chdname)
        elif json_func['name'] == 'NoteDelete':
            para_chdname = 'DeleteCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]],"删除条件")
            else:
                print("参数未找到", para_chdname)
        elif json_func['name'] == 'ScheduleCreate':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4], ["Recurring", str, 1], ["Favorite", bool, 1], ["Pin", bool, 1], ["ReminderTime", list, 1],
                ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1], ["Url", str, 1], ["AttachmentID", str, 1], ["Account", str, 1], ["Group", str, 1]])
        elif json_func['name'] == 'ScheduleModify':
            para_chdname = 'QueryCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4], ["Recurring", str, 1],
                                    ["Favorite", bool, 1], ["Pin", bool, 1], ["ReminderTime", list, 1],
                                    ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1], ["Url", str, 1],
                                    ["AttachmentID", str, 1], ["Account", str, 1], ["Group", str, 1]],"查询条件")
            else:
                print("参数未找到", para_chdname)
            para_chdname = 'NewContent'
            json_change = get_dict_para(json_func, para_chdname)
            if json_change is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_change, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4], ["Recurring", str, 1],
                                    ["Favorite", bool, 1], ["Pin", bool, 1], ["ReminderTime", list, 1],
                                    ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1], ["Url", str, 1],
                                    ["AttachmentID", str, 1], ["Account", str, 1], ["Group", str, 1]], "修改内容")
            else:
                print("参数未找到", para_chdname)
        elif json_func['name'] == 'ScheduleDelete':
            para_chdname = 'DeleteCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4], ["Recurring", str, 1],
                                    ["Favorite", bool, 1], ["Pin", bool, 1], ["ReminderTime", list, 1],
                                    ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1], ["Url", str, 1],
                                    ["AttachmentID", str, 1], ["Account", str, 1], ["Group", str, 1]],"删除条件")
            else:
                print("参数未找到", para_chdname)


        elif json_func['name'] == 'TodoCreate':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                               [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
        elif json_func['name'] == 'TodoModify':
            para_chdname = 'QueryCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]],"查询条件")
            else:
                print("参数未找到", para_chdname)
            para_chdname = 'NewContent'
            json_change = get_dict_para(json_func, para_chdname)
            if json_change is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_change, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]], "修改内容")
            else:
                print("参数未找到", para_chdname)
        elif json_func['name'] == 'TodoDelete':
            para_chdname = 'DeleteCondition'
            json_query = get_dict_para(json_func, para_chdname)
            if json_query is not None:
                frame_chd22 = tk.Frame(frame_chd2)
                frame_chd22.pack()
                ai_func_chdwnd_msg(frame_chd22, json_query, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname,
                                   [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]],"删除条件")
            else:
                print("参数未找到", para_chdname)
        elif json_func['name'] == 'AIGenerate':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Msg",str,6]])
        elif json_func['name'] == 'NetworkSearch':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Msg",str,6]])
        elif json_func['name'] == 'MessageSearch':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                               [["App",str,1],["SearchCondition",str,3],["Sender",list,2],["Sign",str,1],["Time",list,2],["Type",str,1],["Length",str,1],["Favorite",bool,1],["Pin",bool,1],["At",bool,1]])
        elif json_func['name'] == 'ContactCreate':
            ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                               [["first_name", str, 1], ["middle_name", str, 1], ["last_name", str, 1], ["contact_avatar", str, 1],
                                ["phone_number", str, 1], ["email", str, 2], ["iMessage", str, 1], ["WhatsApp", str, 1], ["Facebook_Messenger", str, 1],
                                ["MicrosoftTeams", str, 1], ["Google_Chat", str, 1], ["Slack", str, 1], ["birthday", str, 1], ["address", str, 3],
                                ["company", str, 1], ["note", str, 4], ["URL", str, 2], ["custom_fields", str, 3]])
        else:
            assert False
            tk_text = tk.Text(frame_chd2, width=text_width, height=text_height)
            tk_text.bind("<Key>", on_text_change)
            tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
            tk_text.insert('insert', json_vl['Action'])
            text_map[text_key+"_"+"Action"] = tk_text
    return
def merge_ai_func(json_vl, text_map, text_key):
    thought_chg = get_text_value(text_map[text_key+"_"+"Thought"])

    action_chg = []
    for idx,json_func in enumerate(json_vl['Action']):
        if json_func['name'] == 'ImSendMsg':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [['App',str,1],['Receiver',list,2],['Msg',str,4],["Time",list,1],["Location",list,1]])) # 类型 #文本框长度
        elif json_func['name'] == 'ImReadMsg':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["App",str,1],["Sender",list,2],["Type",str,1],["Time",list,2],['Msg',str,4]]))
        elif json_func['name'] == 'NoteCreate':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                                                       [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]]))
        elif json_func['name'] == 'NoteModify':
            para_chdname1 = 'QueryCondition'
            para_chdname2 = 'NewContent'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1,
                                                  [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_change = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname2,
                                                   [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_chg = get_merge_para({para_chdname1:json_query, para_chdname2:json_change})
            if json_chg is None:
                print("参数合并失败", json_query, json_change)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'NoteDelete':
            para_chdname1 = 'DeleteCondition'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1,
                                                  [["Msg",str,5],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_chg = get_merge_para({para_chdname1:json_query})
            if json_chg is None:
                print("参数合并失败", json_query)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'ScheduleCreate':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                    [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Favorite",bool,1],["Pin",bool,1],["ReminderTime",list,1],
                    ["Location",str,1],["Attendees",list,1],["FullDay",bool,1],["Url",str,1],["AttachmentID",str,1],["Account",str,1],["Group",str,1]]))
        elif json_func['name'] == 'ScheduleModify':
            para_chdname1 = 'QueryCondition'
            para_chdname2 = 'NewContent'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1,
                                                  [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4],
                                                   ["Recurring", str, 1], ["Favorite", bool, 1], ["Pin", bool, 1],
                                                   ["ReminderTime", list, 1],
                                                   ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1],
                                                   ["Url", str, 1], ["AttachmentID", str, 1], ["Account", str, 1],
                                                   ["Group", str, 1]]
                                                  )
            json_change = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname2,
                                                   [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4],
                                                    ["Recurring", str, 1], ["Favorite", bool, 1], ["Pin", bool, 1],
                                                    ["ReminderTime", list, 1],
                                                    ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1],
                                                    ["Url", str, 1], ["AttachmentID", str, 1], ["Account", str, 1],
                                                    ["Group", str, 1]])
            json_chg = get_merge_para({para_chdname1:json_query, para_chdname2:json_change})
            if json_chg is None:
                print("参数合并失败", json_query, json_change)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'ScheduleDelete':
            para_chdname1 = 'DeleteCondition'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1,
                                                  [["Time", list, 2], ["Msg", str, 4], ["Note", str, 4],
                                                   ["Recurring", str, 1], ["Favorite", bool, 1], ["Pin", bool, 1],
                                                   ["ReminderTime", list, 1],
                                                   ["Location", str, 1], ["Attendees", list, 1], ["FullDay", bool, 1],
                                                   ["Url", str, 1], ["AttachmentID", str, 1], ["Account", str, 1],
                                                   ["Group", str, 1]])
            json_chg = get_merge_para({para_chdname1:json_query})
            if json_chg is None:
                print("参数合并失败", json_query)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'TodoCreate':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]]))
        elif json_func['name'] == 'TodoModify':
            para_chdname1 = 'QueryCondition'
            para_chdname2 = 'NewContent'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1, [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_change = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname2, [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_chg = get_merge_para({para_chdname1:json_query, para_chdname2:json_change})
            if json_chg is None:
                print("参数合并失败", json_query, json_change)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'TodoDelete':
            para_chdname1 = 'DeleteCondition'
            json_query = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'] + para_chdname1, [["Time",list,2],["Msg",str,4],["Note",str,4],["Recurring",str,1],["Folder",str,1],["Favorite",bool,1],["Pin",bool,1]])
            json_chg = get_merge_para({para_chdname1:json_query})
            if json_chg is None:
                print("参数合并失败", json_query)
                continue
            action_chg.append(json_chg)
        elif json_func['name'] == 'AIGenerate':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Msg",str,6]]))
        elif json_func['name'] == 'NetworkSearch':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'], [["Msg",str,6]]))
        elif json_func['name'] == 'MessageSearch':
            action_chg.append(merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+str(idx)+"_"+json_func['name'],
                                                       [["App",str,1],["SearchCondition",str,3],["Sender",list,2],["Sign",str,1],["Time",list,2],["Type",str,1],["Length",str,1],["Favorite",bool,1],["Pin",bool,1],["At",bool,1]]))
        elif json_func['name'] == 'ContactCreate':
            action_chg.append(
                merge_ai_func_chdwnd_msg(json_func, text_map, text_key + "_" + str(idx) + "_" + json_func['name'],
                                         [["first_name", str, 1], ["middle_name", str, 1], ["last_name", str, 1],
                                          ["contact_avatar", str, 1], ["phone_number", str, 1], ["email", str, 2],
                                          ["iMessage", str, 1], ["WhatsApp", str, 1], ["Facebook_Messenger", str, 1],
                                          ["MicrosoftTeams", str, 1], ["Google_Chat", str, 1], ["Slack", str, 1],
                                          ["birthday", str, 1], ["address", str, 3], ["company", str, 1],
                                          ["note", str, 4], ["URL", str, 2], ["custom_fields", str, 3]]))
        else:
            assert False
            action_chg = get_text_value(text_map[text_key + "_" + "Action"])
    return merge_ai_action(thought_chg, json.dumps(action_chg, ensure_ascii=False))

def ai_answer_wnd(root, json_vl, text_map, text_key):
    frame = tk.LabelFrame(root,text="ai final answer")
    frame.pack(padx=text_pad, pady=text_pad)
    frame_chd1 = tk.Frame(frame)
    frame_chd1.pack()
    frame_chd2 = tk.Frame(frame)
    frame_chd2.pack()
    tk_label = tk.Label(frame_chd1, text='Thought', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame_chd1, width=text_width, height=text_height)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    if 'Thought' in json_vl:
        tk_text.insert('insert', json_vl['Thought'])
    text_map[text_key+"_"+"Thought"] = tk_text

    tk_label = tk.Label(frame_chd2, text='Final_Answer', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame_chd2, width=text_width, height=text_height+1)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    if 'Final_Answer' in json_vl:
        tk_text.insert('insert', json_vl['Final_Answer'])
    text_map[text_key+"_"+"Final_Answer"] = tk_text
    return

def split_user_prompt(text):
    text = text.strip()
    user_flag = '<|Task|>:'
    tool_flag = '<|Observation|>:'
    if text.startswith(user_flag):
        return "user", text[len(user_flag):].strip()
    elif text.startswith(tool_flag):
        return "tool", text[len(tool_flag):].strip()
    else:
        return "error",""

def merge_user_prompt(type, text):
    user_flag = '<|Task|>:'
    tool_flag = '<|Observation|>:'
    if type == "user":
        return user_flag + " " + text
    elif type == "tool":
        return tool_flag + " " + text
    else:
        print("merge_user_prompt error!")
    return ""

def merge_final_answer(thought, final_answer):
    thought_flag = '<|Thought|>:'
    final_answer_flag = '<|Final_Answer|>:'
    return thought_flag + " " + thought + "\n" + final_answer_flag + " " + final_answer

def merge_ai_action(thought, action):
    thought_flag = '<|Thought|>:'
    action_flag = '<|Action|>:'
    return thought_flag + " " + thought + "\n" + action_flag + " " + action

def user_wnd(root, text, text_map, text_key):
    frame = tk.LabelFrame(root,text="user prompt")
    frame.pack(padx=text_pad, pady=text_pad)
    tk_label = tk.Label(frame, text='User', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame, width=text_width, height=text_height)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    tk_text.insert('insert', text)
    text_map[text_key] = tk_text
    return

def merge_tool_wnd(text_map, text_key):
    js_value = {}
    key_name = 'code'
    text_chg = get_text_value(text_map[text_key + "_" + key_name])
    if text_chg.isnumeric():
        js_value[key_name] = int(text_chg)
    else:
        print("error!只能是数字类型!", text_chg)
        js_value[key_name] = 200

    key_name = 'message'
    text_chg = get_text_value(text_map[text_key + "_" + key_name])
    js_value[key_name] = text_chg

    key_name = 'content'
    text_chg = get_text_value(text_map[text_key + "_" + key_name])
    js_value['response'] = [{key_name:text_chg}]
    return json.dumps(js_value, ensure_ascii=False)

def tool_wnd(root, text, text_map, text_key):
    js_value = json.loads(text)

    frame = tk.LabelFrame(root,text="Observation")
    frame.pack(padx=text_pad, pady=text_pad)
    tk_label = tk.Label(frame, text='Observation', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    chd_text_width = 15

    key_name = 'code'
    tk_label = tk.Label(frame, text=key_name, width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame, width=chd_text_width, height=2)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    tk_text.insert('insert', js_value[key_name])
    text_map[text_key+"_"+key_name] = tk_text

    key_name = 'message'
    tk_label = tk.Label(frame, text=key_name, width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame, width=chd_text_width * 2, height=2)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    tk_text.insert('insert', js_value[key_name])
    text_map[text_key+"_"+key_name] = tk_text

    key_name = 'content'
    tk_label = tk.Label(frame, text=key_name, width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    tk_text = tk.Text(frame, width=chd_text_width * 7, height=2)
    tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
    tk_text.bind("<Key>", on_text_change)
    tk_text.insert('insert', js_value['response'][0][key_name])
    text_map[text_key+"_"+key_name] = tk_text
    return

def pages_wnd(root, rt, rt2):
    def bt_page_last():
        rt.append('last')
        root.quit()
        # root.destroy()
    def bt_page_next():
        rt.append('next')
        root.quit()

    def bt_page_save():
        rt.append('save')
        root.quit()

    def bt_page_del():
        rt.append('del')
        root.quit()

    def bt_page_reset():
        rt.append('reset')
        root.quit()
    def bt_page_regen():
        rt.append('regen')
        root.quit()
    def bt_page_manual_gen():
        rt.append('manual_gen')
        root.quit()
    def bt_page_goto():
        rt.append('goto')
        text = get_text_value(tk_text)
        rt2.append(text)
        root.quit()

    frame_chd = tk.Frame(root)
    frame_chd.pack()

    bt_pady = 15
    bt_ipadx = 40
    button = tk.Button(frame_chd, text='上一条', command=bt_page_last)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='下一条', command=bt_page_next)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='保存', command=bt_page_save)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    # button = tk.Button(frame_chd, text='重置', command=bt_page_reset)
    # button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='重新生成', command=bt_page_regen)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='手动生成', command=bt_page_manual_gen)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='删除', command=bt_page_del)
    button.pack(side=tk.LEFT, padx=sys_bt_pad + 30, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='跳转', command=bt_page_goto)
    button.pack(side=tk.RIGHT, padx=20, pady=bt_pady, ipadx=10)

    tk_text = tk.Text(frame_chd, width=30, height=2)
    tk_text.pack(side=tk.RIGHT, padx=5, pady=bt_pady, ipadx=20)

    tk_label = tk.Label(frame_chd, text='', width=10)
    tk_label.pack(side=tk.RIGHT, padx=5, pady=5, ipadx=5)


def create_sub_window(root, title="子窗口"):
    # 创建子窗口
    sub_window = tk.Toplevel(root)
    # 设置子窗口的标题
    sub_window.title(title)
    sub_window.attributes("-topmost", True)
    sub_window.grab_set()
    # 在子窗口中添加一个标签
    return sub_window

def manual_gening_wnd(root, json_line, rt, rt2, text_map):
    # root = create_sub_window(root, title="单步生成")
    vl = gpt_chat_json_to_json_one_step(json_line)
    if vl is not None:
        text_key = vl['from']
        if vl['from'] == 'gpt':
            json_vl = cvt_ai_msg_to_json(vl['value'])
            if json_vl is None:
                print("json解析错误：", vl['value'])
            if 'Action' in json_vl:
                text_key += "_ai_action"
                ai_func_wnd(root, json_vl, text_map, text_key)
            else:
                text_key += "_ai_answer"
                ai_answer_wnd(root, json_vl, text_map, text_key)
        elif vl['from'] == 'human':
            type, text = split_user_prompt(vl['value'])
            text_key += "_" + type
            if type == "user":
                user_wnd(root, text, text_map, text_key)
            elif type == "tool":
                tool_wnd(root, text, text_map, text_key)
            else:
                print("error user prompt:", vl['value'])

    def bt_page_next():
        rt.append('manual_gen_next')
        root.quit()
    def bt_page_retry():
        rt.append('manual_gen_retry')
        root.quit()
    def bt_page_done():
        rt.append('manual_gen_done')
        root.quit()

    frame_chd = tk.Frame(root)
    frame_chd.pack()

    bt_pady = 15
    bt_ipadx = 40
    button = tk.Button(frame_chd, text='下一步', command=bt_page_next)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='重生单步', command=bt_page_retry)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='完成', command=bt_page_done)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    return vl

def clear_all_components(root):
    for widget in root.winfo_children():
        widget.destroy()

def wnd_add_scrollbar(root):
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox('all'))
    frame = tk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True)
    scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    canvas = tk.Canvas(frame, bg='white')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=canvas.yview)
    canvas_frame = tk.Frame(canvas)
    canvas.create_window(0, 0, anchor='nw', window=canvas_frame)
    tk.Label(canvas_frame, text=f"Label {1}")
    canvas_frame.bind('<Configure>', on_frame_configure)
    return canvas_frame

def edit_a_line(root, idx, list_num, json_line):
    rt = []
    rt2 = []
    text_map = {}
    text_map2 = {}
    title = f"Ghost标注工具：{idx}/{list_num}条"
    root.title(title)
    root.state("zoomed")
    root2 = wnd_add_scrollbar(root)


    pages_wnd(root2, rt, rt2)

    # if 'system' in json_line:
    #     sys_wnd(root2, json_line['system'])

    if 'conversations' in json_line:
        for idx, vl in enumerate(json_line['conversations']):
            if vl is None or 'from' not in vl or 'value' not in vl:
                print("json解析错误：", vl)
                continue
            text_key = str(idx) + "_" + vl['from']
            if vl['from'] == 'gpt':
                json_vl = cvt_ai_msg_to_json(vl['value'])
                if json_vl is None:
                    print("json解析错误：", vl['value'])
                    continue
                if 'Action' in json_vl:
                    text_key += "_ai_action"
                    ai_func_wnd(root2, json_vl, text_map, text_key)
                else:
                    text_key += "_ai_answer"
                    ai_answer_wnd(root2, json_vl, text_map, text_key)
            elif vl['from'] == 'human':
                type, text = split_user_prompt(vl['value'])
                text_key += "_" + type
                if type == "user":
                    user_wnd(root2, text, text_map, text_key)
                elif type == "tool":
                    tool_wnd(root2, text, text_map, text_key)
                else:
                    print("error user prompt:", vl['value'])

    global need_save
    global is_manual_gening
    if is_manual_gening:
        manual_gen_json = manual_gening_wnd(root2, json_line, rt, rt2, text_map2)
    root.mainloop()
    if len(rt) == 0:
        return None,None
    if is_manual_gening:
        if need_save:   # 修复单步生成错误后，修改content内容不能保存的bug，不敢改之前逻辑，加这里不知道对不对。
            try:
                save_text_to_json(json_line, text_map)
            except Exception as e:
                print("error! save_text_to_json error json")

        if rt[0] == 'manual_gen_next':
            save_text_to_json_manual_gen(json_line, text_map2, manual_gen_json)
            need_save = True
        elif rt[0] == 'manual_gen_retry':
            pass
        else:   # 'manual_gen_done' or other
            save_text_to_json_manual_gen(json_line, text_map2, manual_gen_json)
            is_manual_gening = False
            need_save = True
    elif need_save:
        if rt[0] == 'next' or rt[0] == 'last'  or rt[0] == 'save'  or rt[0] == 'regen'  or rt[0] == 'manual_gen':
            try:
                save_text_to_json(json_line, text_map)
            except Exception as e:
                print("error! save_text_to_json error json")
        else:
            need_save = False
    clear_all_components(root)
    return rt[0],rt2

def get_text_value(text_edit):
    text = text_edit.get('0.0', 'end')
    if len(text) > 0 and text[-1] == "\n":
        text = text[:-1]
    return text.strip()

def save_text_to_json_manual_gen(json_line, text_map, vl):
    if vl is None or 'from' not in vl or 'value' not in vl:
        print("无效的json格式：", vl)
        return
    if 'conversations' in json_line:
        global need_save
        if need_save:
            text_key = vl['from']
            if vl['from'] == 'gpt':
                json_vl = cvt_ai_msg_to_json(vl['value'])
                if 'Action' in json_vl:
                    text_key += "_ai_action"
                    vl_chg = merge_ai_func(json_vl, text_map, text_key)
                    vl['value'] = vl_chg
                else:
                    text_key += "_ai_answer"
                    thought_chg = get_text_value(text_map[text_key+"_"+"Thought"])
                    final_answer_chg = get_text_value(text_map[text_key+"_"+"Final_Answer"])
                    vl_chg = merge_final_answer(thought_chg, final_answer_chg)
                    vl['value'] = vl_chg
            elif vl['from'] == 'human':
                type, text = split_user_prompt(vl['value'])
                text_key += "_" + type
                if type == "user":
                    text_chg = get_text_value(text_map[text_key])
                    vl_chg = merge_user_prompt(type, text_chg)
                    vl['value'] = vl_chg
                elif type == "tool":
                    text_chg = merge_tool_wnd(text_map, text_key)
                    vl_chg = merge_user_prompt(type, text_chg)
                    vl['value'] = vl_chg
                else:
                    print("error user prompt:", vl['value'])
                    return
        json_line['conversations'].append(vl)


def save_text_to_json(json_line, text_map):
    if 'conversations' in json_line:
        for idx, vl in enumerate(json_line['conversations']):
            text_key = str(idx) + "_" + vl['from']
            if vl['from'] == 'gpt':
                json_vl = cvt_ai_msg_to_json(vl['value'])
                if 'Action' in json_vl:
                    text_key += "_ai_action"
                    vl_chg = merge_ai_func(json_vl, text_map, text_key)
                    vl['value'] = vl_chg
                else:
                    text_key += "_ai_answer"
                    thought_chg = get_text_value(text_map[text_key+"_"+"Thought"])
                    final_answer_chg = get_text_value(text_map[text_key+"_"+"Final_Answer"])
                    vl_chg = merge_final_answer(thought_chg, final_answer_chg)
                    vl['value'] = vl_chg
            elif vl['from'] == 'human':
                type, text = split_user_prompt(vl['value'])
                text_key += "_" + type
                if type == "user":
                    text_chg = get_text_value(text_map[text_key])
                    vl_chg = merge_user_prompt(type, text_chg)
                    vl['value'] = vl_chg
                elif type == "tool":
                    text_chg = merge_tool_wnd(text_map, text_key)
                    vl_chg = merge_user_prompt(type, text_chg)
                    vl['value'] = vl_chg
                else:
                    print("error user prompt:", vl['value'])

def save_json(out_file, out_list):
    # bak first
    path, filename = os.path.split(out_file)
    bak_path = path + "/bak"
    for i in reversed(range(5)):
        from_file = bak_path + "/" + filename + ".bak" + str(i)
        to_file = bak_path + "/" + filename + ".bak" + str(i+1)
        if os.path.exists(from_file):
            shutil.copy(from_file, to_file)

    to_file = bak_path + "/" + filename + ".bak0"
    shutil.copy(out_file, to_file)

    texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
    save_file_crypt(texts_json, out_file)
    # with open(out_file, 'w', encoding='utf-8') as f:
    #     f.write(texts_json)
    global need_save
    need_save = False

def find_idx_by_str(json_all, now_idx, text):
    if len(text) == 0:
        return now_idx

    if text.isnumeric():
        return int(text)
    list_num = len(json_all)
    list_range = [i for i in range(now_idx, list_num)] + [i for i in range(0, now_idx)]
    for idx in list_range:
        json_line = json_all[idx]
        if 'conversations' in json_line and len(json_line['conversations']) > 0 and json_line['conversations'][0]['from'] == 'human':
            user_text = json_line['conversations'][0]['value']
            if user_text.find(text) >= 0:
                return idx
    print("没有找到：", text)
    return now_idx


def open_file():
    filetypes = (
        ('cbin or csv files', (('*.cbin'),('*.json'),('*.csv'))),
        ('All files', '*.*')
    )
    filename = filedialog.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    print(filename)
    return filename

is_manual_gening = False
def manual_gen_init(json_line):
    if 'conversations' in json_line and len(json_line['conversations']) > 0:
        json_line['conversations'] = json_line['conversations'][:1]
        return True
    else:
        print("不完整的json格式：", json_line)
        return False

def main(input_file):
    path, filename = os.path.split(input_file)
    bak_path = path + "/bak"
    os.makedirs(bak_path, exist_ok=True)
    idx_file = bak_path + "/" + filename + ".log"
    out_file, _ = split_file_ex(input_file)
    out_file += ".cbin"
    text_pred = open_file_auto(input_file)
    global need_save

    json_all = str_to_json(text_pred)
    list_num = len(json_all)
    if list_num == 0:
        return
    root = tk.Tk()

    idx = 0 # 记录退出位置
    if os.path.isfile(idx_file):
        idx = int(read_file(idx_file))
        if idx >= list_num:
            idx = 0
    while True:
        write_file(idx_file, str(idx))

        json_line = json_all[idx]
        # need_save = False
        rt, rt2 = edit_a_line(root, idx, list_num, json_line)
        if rt is None:
            break
        print(rt)
        if need_save:
            save_json(out_file, json_all)
        if rt == 'next':
            idx += 1
            if idx >= list_num:
                idx = list_num - 1
                print("到结束了")
        elif rt == 'last':
            idx -= 1
            if idx < 0:
                idx = 0
                print("到开始了")
        elif rt == 'regen':
            json_line_chg = gpt_chat_json_to_json(json_line)
            json_all[idx] = json_line_chg
            need_save = True
        elif rt == 'manual_gen':
            # 一步一步生成，每步之后需要确认，工具回复弹出子窗口可以更改！！！
            manual_gen_init(json_all[idx])
            global is_manual_gening
            is_manual_gening = True
        elif rt == 'save':
            pass
        elif rt == 'goto':
            idx = find_idx_by_str(json_all, idx, rt2[0])
            if idx < 0:
                idx = 0
            if idx >= list_num:
                idx = list_num - 1
        elif rt == 'del':
            del json_all[idx]
            list_num = len(json_all)
            save_json(out_file, json_all)
            if idx >= list_num:
                idx = list_num - 1
        elif rt == 'reset':
            pass
        elif rt == 'manual_gen_next' or rt == 'manual_gen_retry' or rt == 'manual_gen_done':
            pass
        else:
            assert False

    if need_save:
        save_json(out_file, json_all)
    write_file(idx_file, str(idx))
#######################################################################################################################
def safe_chat_create(client, model, messages):
    try:
        response = client.chat.completions.create(model=model, messages=messages)
        msg = response.choices[0]
        if msg.finish_reason == 'content_filter':
            print("error!content_filter 1!")
            return ""
        return msg.message.content
    except Exception as e:
        print("error!content_filter 2!")
        return ""

def user_prompt_to_english(input_text):
    model_name = gpt_model_name    # only gpt4 can do

    if model_name == gpt_model_name:
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    # sys_prompt = "你是一个翻译助手，请把下面的用户指令译成英语，尽量口语化，可以使用网上常用的俚语，表现的像一个土生土长的美国人，如果有人名翻译成美国常用的人名"
    sys_prompt = "你是一个翻译助手，请把下面的内容译成英语，确保英文和中文表达了相同的含义，尽量使用普通口语，非常亲密朋友之间的口语，如果有人名翻译成美国常用的人名"

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    content = safe_chat_create(client, model=model_name, messages=messages)
    return str_replace(content)

#######################################################################################################################
def load_csv(filename):
    csv_reader = csv.reader(open(filename,encoding='utf-8-sig'))
    lines = []
    for idx,row in enumerate(csv_reader):
        # if len(row) != columns_num:
        #     print(idx, "warning=======invalid line================", filename, len(row))
        #     continue
        if len(row) == 1:
            lines.append(row[0])
        else:
            lines.append(row)
    return lines

def cvt_csv_to_json(input_file, radio_type, checkbox_mult_talk, checkbox_skip_invalid_line, checkbox_only_cvt, checkbox_save_whatever, begin_idx):
    sys_prompt_en = open_file_auto("./cfg/system_prompt_en.cbin")
    sys_prompt_zh = open_file_auto("./cfg/system_prompt_zh2.cbin")

    if checkbox_only_cvt > 0:
        checkbox_mult_talk = 0

    input_filename, _ = split_file_ex(input_file)
    output_crypt = input_filename + "_out_" + datetime.now().strftime("%Y%m%d_%H%M%S") +".cbin"
    input_filename += ".csv"
    to_json = True

    input_lines = load_csv(input_filename)
    out_list = []
    idx = 0
    while idx < len(input_lines):
        is_english = radio_type > 0
        lines = input_lines[idx]
        if idx < begin_idx:
            print(idx, "跳过行:", lines[0])
            idx += 1
            continue
        if checkbox_skip_invalid_line > 0 and lines[1] == '1':
            print(idx, "暂时不支持的类型:", lines[0])
            idx += 1
            continue
        row_num = len(lines) if checkbox_mult_talk > 0 else 1

        custom_tools = custom_tools_en if is_english else custom_tools_zh
        functions = funcs_json(custom_tools)
        funcs_js = json.dumps(functions, ensure_ascii=False)
        if is_english:
            sys_prompt = sys_prompt_en
            sys_prompt += "[Function List]=\"\"\"\n" + funcs_js + "\n\nBegin reasoning!"
        else:
            sys_prompt = sys_prompt_zh
            sys_prompt += "[函数列表]=\"\"\"\n" + funcs_js + "\n\n开始推理！"

        messages = [
            {"role": "system", "content": sys_prompt},
        ]

        error = False
        for row_idx in range(0, row_num, 2):
            input_text = lines[row_idx].strip()
            global test_input_text
            if test_input_text != "":
                input_text = test_input_text
                print("测试模式", input_text)
            if input_text == "":
                assert row_idx != 0
                continue

            if radio_type == 2:
                print("============================", idx, row_idx, "==========English==================")
                input_text = user_prompt_to_english(input_text)
                if input_text == "":
                    print("============================", idx, "==============error=====filter=========")
                    error = True
                    break
            else:
                print("============================", idx, row_idx, "============================")

            input_text = "<|Task|>:" + input_text
            func_msg = make_msgs_user(("human", input_text))
            add_msgs_user(messages, func_msg)

            if checkbox_only_cvt > 0:
                break
            rt, messages = gpt_chat_with_try(messages, is_english, gpt_model_name, need_check = False, try_times = 3)
            if not rt:
                print("============================", idx, "==============error==============")
                error = True
                break
        if error and checkbox_save_whatever == 0:
            box_rt = "skip"
            if box_rt == "skip":
                print("============================", idx, "==============skip==============")
                idx += 1
                continue
            elif box_rt == "retry":
                print("============================", idx, "==============retry==============")
                continue

        box_rt = "save"
        if box_rt == "skip":
            print("============================", idx, "==============skip==============")
            idx += 1
            continue
        elif box_rt == "retry":
            print("============================", idx, "==============retry==============")
            continue

        print("============================", idx, len(out_list),"==============save==============")
        assert box_rt == "save"
        messages = to_sharegpt_format(messages)
        out_list.append(messages)
        if to_json:
            texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
            save_file_crypt(texts_json, output_crypt)
        idx += 1

def cvt_wnd(input_file):
    def bt_cvt():
        rt.append('cvt')
        root.quit()

    rt = []
    root = tk.Tk()
    title = "用户指令转换器:csv-->json"
    root.title(title)

    frame = tk.LabelFrame(root,text="转换内容")
    frame.pack(padx=text_pad, pady=text_pad)
    tk_label = tk.Label(frame, text='文件:'+input_file)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    frame_chd = tk.Frame(root)
    frame_chd.pack()
    radio_type = tk.IntVar()
    frame = tk.LabelFrame(frame_chd,text="类型")
    frame.pack(side=tk.LEFT,padx=text_pad, pady=text_pad)
    radio = tk.Radiobutton(frame, text="中文",variable=radio_type,value=0)
    radio.pack(side=tk.LEFT)
    radio = tk.Radiobutton(frame, text="英文",variable=radio_type,value=1)
    radio.pack(side=tk.LEFT)
    radio = tk.Radiobutton(frame, text="中文转英文",variable=radio_type,value=2)
    radio.pack(side=tk.LEFT)

    frame = tk.LabelFrame(frame_chd,text="选项")
    frame.pack(side=tk.LEFT,padx=text_pad, pady=text_pad)
    checkbox_mult_talk = tk.IntVar()
    checkbox = tk.Checkbutton(frame, text="多轮对话", variable=checkbox_mult_talk)
    checkbox.pack(side=tk.LEFT)
    checkbox_skip_invalid_line = tk.IntVar()
    checkbox = tk.Checkbutton(frame, text="跳过第二列为1的行", variable=checkbox_skip_invalid_line)
    checkbox.pack(side=tk.LEFT)
    checkbox_only_cvt = tk.IntVar()
    checkbox = tk.Checkbutton(frame, text="仅转换格式", variable=checkbox_only_cvt)
    checkbox.pack(side=tk.LEFT)
    checkbox_save_whatever = tk.IntVar()
    checkbox = tk.Checkbutton(frame, text="错误行也保存", variable=checkbox_save_whatever)
    checkbox.pack(side=tk.LEFT)

    frame = tk.LabelFrame(frame_chd,text="开始行号")
    frame.pack(side=tk.LEFT,padx=text_pad, pady=text_pad)
    tk_text_begin_idx = tk.Entry(frame)
    tk_text_begin_idx.pack(padx=5, pady=5, ipadx=3, ipady=3)
    tk_text_begin_idx.insert('insert', "1")

    bt_pady = 15
    bt_ipadx = 60
    button = tk.Button(root, text='转换', command=bt_cvt)
    button.pack(padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx, ipady=5)
    root.mainloop()
    if len(rt) == 0:
        return
    tk_text_begin_idx = tk_text_begin_idx.get()
    begin_idx = 1
    if tk_text_begin_idx.isnumeric():
        begin_idx = int(tk_text_begin_idx)
    begin_idx -= 1
    if rt[0] == 'cvt':
        cvt_csv_to_json(input_file, radio_type.get(), checkbox_mult_talk.get(), checkbox_skip_invalid_line.get(), checkbox_only_cvt.get(), checkbox_save_whatever.get(), begin_idx)
    return


test_input_text = ""
# test_input_text = "先帮我新建一个打羽毛球的待办，再把之前有人给我发过路线帮我找一下然后放到备注里."  # 444444444444444
# test_input_text = "先帮我删除打羽毛球的待办."  # 444444444444444
# test_input_text = "帮我添加一个待办叫做个测试，再把这个待办改成哈哈哈，再删除这个待办"  # 444444444444444
# test_input_text = "帮我添加一个便签叫做个测试，再把这个便签改成哈哈哈，再删除这个便签"  # 444444444444444
# test_input_text = "帮我添加一个日程叫做个测试，再把这个日程改成哈哈哈，再删除这个日程"  # 444444444444444
# test_input_text = "Can you help me add a schedule for tomorrow afternoon at 2 pm for a test? Then change this schedule to hahaha and delete it"  # 444444444444444
# test_input_text = "Help me add a note called a test, change it to hahaha, and delete it"  # 444444444444444
# test_input_text = "Help me add a to-do called a test, change it to hahaha, and then delete it"  # 444444444444444
# test_input_text = "找一下上个月我和jerry在whatsapp里聊的和AI相关的记录，把字数超过100的消息找出来"  # 444444444444444
# test_input_text = "帮我看下上周在whatsapp的自驾游群里有哪些@我的消息"  # 444444444444444
# test_input_text = "给张三发个消息告诉他晚上一起吃饭，跟王立群和一家亲群发个消息说周日晚上一起看电影"  # 444444444444444
# test_input_text = "帮我添加两个便签一个叫明天晚上看电影，一个叫晚上回家吃饭，再把明天晚上看电影改成明天晚上跟张三一起看电影，把晚上回家吃饭改成跟李四一起晚上吃饭"
# test_input_text = "帮我添加一个便签叫明天晚上看电影，跟张三发个消息叫他一起去，哦，把这个便签改成明天晚上跟张三一起看电影吧"
# test_input_text = "帮我跟高老师发个消息跟他说明天别让他过来了，让他在家等我就可以了"
# test_input_text = "帮我新建一个每周六下午9点到10点打羽毛球的循环日程，参会人是我和whatsapp的常鹏程，到时候提前30分钟提醒我"
# test_input_text = "昨天晚上看了巴西队和阿根廷的足球赛，二比二平了，梅西都没有进球，有三个助攻，把这个消息通过WhatsApp发给高老师，问问他他觉得这场球踢的咋样，能不能做个简单的评价，另外告诉他明天晚上一起吃饭"
# test_input_text = "发个消息给高老师告诉他明天晚上一起看电影，哦对了，我忘了他去深圳了，给田老师发吧，问问他去不去"
# test_input_text = "帮我创建12个便签，第一个标题是1月，第二个是二月，第三个是三月，以此类推"
# test_input_text = "看到一篇新闻内容是：连日来，北方多地遭遇了今年以来影响范围最广、强度最强的高温天气过程。6月11日，京津冀、河南、山东等地部分地区出现了35—39℃的高温天气，局地达40—43.4℃，河北、山东、天津有6个国家站日最高气温突破6月极值。多地加大力度做好防暑降温工作，保障生产生活。把这个新闻总结一下发给高老师"
# test_input_text = "今天聚会吃饭花了331块钱，我结的账，跟高通还有田勇老师一起去的，我们三个AA，算一下他们每人应该付多少钱，跟他们发个WhatsApp消息，让他俩给我钱，尽量说的委婉一些呀"
# test_input_text = "当前时间2024-06-12 17:11:00，端午节为2024-06-05；定一个端午节上午9点的日程，打篮球，到时候提前一刻钟提醒我"
# test_input_text = "给张三发个WhatsApp消息让他说一个10以内的数、给李四发个微信消息让他说一个10以内的数、给王五发个邮件让他说一个10以内的数，然后等他们回消息，如果有人发5就跟他回消息说你赢了"
# test_input_text = "找一下我的日程、待办、便签有没有关于AI的内容，然后把他们总结到一起发给我"
# test_input_text = "看到一篇新闻内容是：连日来，北方多地遭遇了今年以来影响范围最广、强度最强的高温天气过程。6月11日，京津冀、河南、山东等地部分地区出现了35—39℃的高温天气，局地达40—43.4℃，河北、山东、天津有6个国家站日最高气温突破6月极值。多地加大力度做好防暑降温工作，保障生产生活。把这个新闻总结一下用WhatsApp发给高老师，问他一下，晚上要不要一起吃饭" #!!!
# test_input_text = "啊，你能新建一个名为Emma，中间名为Charlotte，姓为Watson的联系人吗？"

if __name__ == '__main__':
    print("====================标注工具===2024.06.18============================")
    input_file = open_file()
    # input_file = r"D:\Dataset_llm\dataset_llama3_val/ghost_user_llm_test_dataset_2_watch_msg_pos_asr_out_20240602_181314.json"
    # input_file = r"C:\Users\trl\Desktop\Sheet1.csv"
    # input_file = r"E:\Download/ghost_user_llm_test_dataset - 2_search_msg_pos.csv" #44444
    # input_file = r"E:\Download/ghost_user_llm_test_dataset - 2_search_msg_pos_out_20240607_155535.cbin" #44444
    if os.path.exists(input_file):
        if input_file.lower().endswith(".csv"):
            cvt_wnd(input_file)
        else:
            if input_file.lower().endswith(".json"):
                # json 文件先转成cbin文件再处理
                out_file, _ = split_file_ex(input_file)
                out_file += ".cbin"
                if os.path.exists(out_file):
                    print("json文件转换失败，cbin文件已存在！", input_file)
                else:
                    encrypt_file(input_file, out_file)
                input_file = out_file
            main(input_file)