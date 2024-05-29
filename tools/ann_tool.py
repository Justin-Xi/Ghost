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
from langchain_core.utils.function_calling import convert_to_openai_function

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
    assert msg.finish_reason == 'stop'
    return {"role": "assistant", "content":msg.message.content}

def getstr_ai_rt_tool(msg):
    if msg.finish_reason == 'content_filter':
        print("error content filter!")
        return None
    assert msg.finish_reason == 'stop'
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
    assert msg.finish_reason == 'stop'
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
    return text.replace("\"", "'").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("/", " ").replace("\b", " ").replace("\f", " ")

def gen_user_prompt_function(model_name, is_english, messages):
    model_name = "gpt4turbo"    # only gpt4 can do

    if model_name == "gpt4turbo":
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
def func_call_rt(name, model_name, is_english, messages):
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
    elif name == 'ScheduleCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The schedule has been created\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"日程已创建\"}]}"
    elif name == 'TodoCreate':
        if is_english:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"The todo has been created\"}]}"
        else:
            return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \"待办已创建\"}]}"

    assert False
    return name, "Done"

def gpt_chat(messages, is_english, model_name, need_check = False):

    if model_name == "gpt4turbo":
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
        func_msg = make_msgs_user(func_call_rt(ai_json['Action'][0]['name'], model_name, is_english, messages))
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
        rt, messages = gpt_chat_with_try(messages, is_english, "gpt4turbo", need_check = False, try_times = 3)
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
    model_name = "gpt4turbo"
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
            _,value = func_call_rt(ai_json['Action'][0]['name'], model_name, is_english, messages)
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
sys_bt_pad = 30

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
        return "创建便签","cyan"
    elif name == "ScheduleCreate":
        return "创建日程","orange"
    elif name == "TodoCreate":
        return "创建待办","olive"
    else:
        assert False
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

def ai_func_chdwnd_msg(frame_chd, json_vl, text_map, text_key, func_para):
    func_para_list, func_para_type, func_para_len =  list(zip(*func_para))
    func_name, label_color = get_func_name(json_vl['name'])
    tk_label = tk.Label(frame_chd, text= func_name + ":" + json_vl['name'], foreground=label_color)
    tk_label.pack(side=tk.LEFT)
    if 'parameters' in json_vl:
        paras = copy.deepcopy(json_vl['parameters'])
        for k in paras:
            if k not in func_para_list:
                del json_vl['parameters'][k]
                global need_save
                need_save = True
                print("发现多余参数：", k)

    chd_text_width = 15
    for idx,k in enumerate(func_para_list):
        tk_label = tk.Label(frame_chd, text=k)
        tk_label.pack(side=tk.LEFT, padx=5)

        tk_text = tk.Text(frame_chd, width=chd_text_width * func_para_len[idx], height=2)
        tk_text.pack(side=tk.LEFT, padx=text_pad, pady=text_pad, ipadx=text_pad, ipady=text_pad)
        tk_text.bind("<Key>", on_text_change)
        text_map[text_key + "_" + k] = tk_text
        if 'parameters' in json_vl and k in json_vl['parameters']:
            if func_para_type[idx] is list:
                tk_text.insert('insert', list_to_str(json_vl['parameters'][k]))
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
            else:
                para_map[k] = value_cha
    func_map['parameters'] = para_map
    return json.dumps([func_map], ensure_ascii=False)

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

    tk_label = tk.Label(frame_chd2, text='Action', width=label_width)
    tk_label.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)

    frame_chd22 = tk.Frame(frame_chd2)
    frame_chd22.pack(side=tk.LEFT, padx=5, pady=5, ipadx=5)
    json_func = json_vl['Action'][0]
    if len(json_vl['Action']) > 1:
        print("warning! 函数列表中有多个函数，多余的部分被忽略了", json_vl)
    if json_func['name'] == 'ImSendMsg':
        ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+json_func['name'], [['App',str,1],['Receiver',list,2],['Msg',str,4]]) # 类型 #文本框长度
    elif json_func['name'] == 'ImReadMsg':
        ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+json_func['name'], [["App",str,1],["Sender",list,2],["Type",str,1],["Time",list,2],['Msg',str,3]])
    elif json_func['name'] == 'NoteCreate':
        ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+json_func['name'], [["Msg",str,6]])
    elif json_func['name'] == 'ScheduleCreate':
        ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+json_func['name'], [["Time",list,2],["Msg",str,6]])
    elif json_func['name'] == 'TodoCreate':
        ai_func_chdwnd_msg(frame_chd22, json_func, text_map, text_key+"_"+json_func['name'], [["Time",list,2],["Msg",str,6]])
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

    json_func = json_vl['Action'][0]
    if json_func['name'] == 'ImSendMsg':
        action_chg = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+json_func['name'], [['App',str,1],['Receiver',list,2],['Msg',str,4]]) # 类型 #文本框长度
    elif json_func['name'] == 'ImReadMsg':
        action_chg = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+json_func['name'], [["App",str,1],["Sender",list,2],["Type",str,1],["Time",list,2],['Msg',str,4]])
    elif json_func['name'] == 'NoteCreate':
        action_chg = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+json_func['name'], [["Msg",str,6]])
    elif json_func['name'] == 'ScheduleCreate':
        action_chg = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+json_func['name'], [["Time",list,2],["Msg",str,6]])
    elif json_func['name'] == 'TodoCreate':
        action_chg = merge_ai_func_chdwnd_msg(json_func, text_map, text_key+"_"+json_func['name'], [["Time",list,2],["Msg",str,6]])
    else:
        assert False
        action_chg = get_text_value(text_map[text_key + "_" + "Action"])
    return merge_ai_action(thought_chg, action_chg)

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
        assert False
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

    button = tk.Button(frame_chd, text='删除', command=bt_page_del)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='保存', command=bt_page_save)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    # button = tk.Button(frame_chd, text='重置', command=bt_page_reset)
    # button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='重新生成', command=bt_page_regen)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

    button = tk.Button(frame_chd, text='手动生成', command=bt_page_manual_gen)
    button.pack(side=tk.LEFT, padx=sys_bt_pad, pady=bt_pady, ipadx=bt_ipadx)

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

def edit_a_line(root, idx, list_num, json_line):
    rt = []
    rt2 = []
    text_map = {}
    text_map2 = {}
    title = f"Ghost标注工具：{idx}/{list_num}条"
    root.title(title)

    pages_wnd(root, rt, rt2)

    # if 'system' in json_line:
    #     sys_wnd(root, json_line['system'])

    if 'conversations' in json_line:
        for idx, vl in enumerate(json_line['conversations']):
            text_key = str(idx) + "_" + vl['from']
            if vl['from'] == 'gpt':
                json_vl = cvt_ai_msg_to_json(vl['value'])
                if json_vl is None:
                    print("json解析错误：", vl['value'])
                    continue
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

    global need_save
    global is_manual_gening
    if is_manual_gening:
        manual_gen_json = manual_gening_wnd(root, json_line, rt, rt2, text_map2)
    root.mainloop()
    if len(rt) == 0:
        return None,None
    if is_manual_gening:
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
            save_text_to_json(json_line, text_map)
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
def funcs(custom_tools):
    im_send_msg = custom_tools.ImSendMsgTool()
    im_read_msg = custom_tools.ImReadMsgTool()
    note_create = custom_tools.NoteCreateTool()
    schedule_create = custom_tools.ScheduleCreateTool()
    todo_create = custom_tools.TodoCreateTool()

    tools = [
        im_send_msg,
        im_read_msg,
        note_create,
        schedule_create,
        todo_create,
    ]
    return tools

def cvt_to_openai_function(t):
    t2 = convert_to_openai_function(t)
    t3 = copy.deepcopy(t2)
    if 'optional_para' in vars(t) and 'parameters' in t2 and 'required' in t2['parameters']:
        for para in t2['parameters']['required']:
            if para in t.optional_para:
                t3['parameters']['required'].remove(para)
    return t3

def funcs_json(custom_tools):
    tools = funcs(custom_tools)
    functions = [cvt_to_openai_function(t) for t in tools]
    return functions

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
    model_name = "gpt4turbo"    # only gpt4 can do

    if model_name == "gpt4turbo":
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
            rt, messages = gpt_chat_with_try(messages, is_english, "gpt4turbo", need_check = False, try_times = 3)
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

if __name__ == '__main__':
    print("====================标注工具===2024.05.28============================")
    input_file = open_file()
    # input_file = r"D:\Dataset_llm\dataset_llama3_val/ghost_user_llm_val_dataset_169.json"
    # input_file = r"D:\Dataset_llm\dataset_llama3_val/ghost_user_llm_test_dataset_2_watch_msg_pos.csv"
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