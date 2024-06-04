import os
import random
import csv
from openai import AzureOpenAI
import tool_funcs
import json
from utils.input_wnd import input_show
from fine_tuning.auto_check import check_result
from fine_tuning.gen_user_prompt import gen_user_prompt_function, user_prompt_to_english, gen_ai_function, network_search_function
from datetime import datetime
import tools4dataset_zh as custom_tools_zh
import tools4dataset_en as custom_tools_en
from utils.input_wnd import msg_box_3button, msg_box_2button

def str_replace(text):
    return text.replace("\"", "'").replace("\n", "；").replace("\t", " ")

def getstr_ai_rt(msg):
    if msg.finish_reason == 'content_filter':
        return {"role": "assistant", "content": "content filter"}
    assert msg.finish_reason == 'stop'
    return {"role": "assistant", "content":msg.message.content}

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

def cvt_one_msg(line, keyword_list):
    for kwd in keyword_list:
        if line.startswith(kwd):
            key = line[:len(kwd)][2:-3] #remove <| |>:
            value = line[len(kwd):]
            if key == "Action" or key == "Observation": #json
                try:
                    js_value = json.loads(value)
                    return key, js_value
                except Exception as e:
                    print("cvt_one_msg json error:", value)
                    return key, None
            else:
                return key, value
    return None, None

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
        if value is None:
            return None
        jsons[key] = value
    return jsons

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

def gpt_chat_with_try(messages, is_english, model_name, need_check = False, try_times = 3):
    for i in range(try_times):
        rt, messages = gpt_chat(messages, is_english, model_name, need_check)
        if rt:
            return True, messages
        print("============error try================", i, "============================")

    return False, messages

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
        if 'Action' not in ai_json or len(ai_json['Action']) == 0:
            return False, messages
        func_msg = make_msgs_user(func_call_rt(ai_json['Action'][0], model_name, is_english, messages))
        add_msgs_user(messages, func_msg)
        # response = client.chat.completions.create(model=model_name, messages=messages, functions=functions) #,temperature=temperature
        msg = safe_chat_create_with_retry(client, model=model_name, messages=messages, retry_times=2)
        if msg is None:
            return False, messages
        ai_type, ai_json = get_ai_msg_type(msg)
        add_msgs_ai(messages, msg, ai_type, ai_json)

    if ai_type != "final":
        return False, messages

    if need_check:
        check_result(messages)
    return True, messages

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
    elif name == "AIGenerate":
        value = gen_ai_function(model_name, is_english, action)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"
    elif name == "NetworkSearch":
        value = network_search_function(model_name, is_english, action)
        return name, " <|Observation|>: {\"code\": 200, \"message\":\"success\", \"response\": [{\"content\": \""+value+"\"}]}"

    assert False
    return name, "Done"

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

    assert len(conversations) % 2 == 0
    if conversations is not None:
        gpt_msgs['conversations'] = conversations
    return gpt_msgs

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        sys_prompt = f.read()
    return sys_prompt

def write_log(filename, input_txt_zh, input_txt_en):
    print("中文：", input_txt_zh)
    print("英文：", input_txt_en)
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(input_txt_zh + "\n")
        f.write(input_txt_en + "\n")

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

def add_null_line(input_lines):
    input_len = len(input_lines)
    for idx in reversed(range(input_len)):
        input_lines.insert(idx+1,[])

if __name__ == '__main__':
    # sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。在每一步调用function call时，加入思维链，描述当前处境和下一步行动的原因，并说明自己的下一步行动，思维过程放在content字段中。如果需要总结，尽量简洁，30字以内。"
    sys_prompt_en = read_file("../cfg/system_prompt_en.txt")
    sys_prompt_zh = read_file("../cfg/system_prompt_zh2.txt")
    select_wnd = True
    save_whatever = False

    # 1、名字，2、是否加行，纯中文的需要选True,3、多轮

    # 训练集
    # root_path = r"D:\Dataset_llm\dataset_llama3/"
    # input_filelist = [
    #     ["ghost_user_llm_train_dataset_2_watch_msg_neg", True, True],
    #     # ["ghost_user_llm_train_dataset_1_send_msg_neg", True, True],
    #     # ["ghost_user_llm_train_dataset_3_note_todo_schedule_pos", False,False],
    #     # ["ghost_user_llm_train_dataset_2_read_msg_pos", False,False],
    #     # ["ghost_user_llm_train_dataset_1_send_msg_pos", False,False],
    # ]

    # 测试集
    root_path = r"D:\Dataset_llm\dataset_llama3_val/"
    input_filelist = [
        ["ghost_user_llm_test_dataset_2_watch_msg_pos_asr", True, False],
        # ["ghost_user_llm_test_dataset_2_watch_msg_pos", True, False],
        # ["ghost_user_llm_test_dataset_2_watch_msg_pos_asr", True, False],
        # ["ghost_user_llm_test_dataset_3_note_todo_schedule_pos", True, False],
        # ["ghost_user_llm_test_dataset_1_send_msg_pos", True, False],
    ]
    have_chinese = True
    have_english = False

    #----------export-----------
    select_wnd = False
    save_whatever = True
    #---------------------------

    for input_filename, need_add, mult_round in input_filelist:
        input_filename = root_path + input_filename
        output_filename = input_filename + "_out.csv"
        output_json = input_filename + "_out_" + datetime.now().strftime("%Y%m%d_%H%M%S") +".json"
        input_filename += ".csv"
        to_json = True
        begin_idx = 0
        # begin_idx = (14-1)*2  # 4444

        input_lines = load_csv(input_filename)
        if need_add:
            add_null_line(input_lines) # 没有留英文的行，添加空行

        out_list = []
        idx = 0
        input_lines = input_lines[:1] #4444444
        while idx < len(input_lines):
            if idx < begin_idx:
                idx += 1
                continue
            if not have_chinese and idx % 2 == 0:
                idx += 1
                continue
            if not have_english and idx % 2 == 1:
                idx += 1
                continue
            is_english = (idx % 2 == 1)
            lines = input_lines[idx-1] if is_english else input_lines[idx]
            if lines[1] == '1':
                print(idx, "暂时不支持的类型:", lines[0])
                idx += 1
                continue
            row_num = len(lines) if mult_round else 1

            custom_tools = custom_tools_en if is_english else custom_tools_zh
            functions = tool_funcs.funcs_json(custom_tools)
            funcs_json = json.dumps(functions, ensure_ascii=False)
            if is_english:
                sys_prompt = sys_prompt_en
                sys_prompt += "[Function List]=\"\"\"\n" + funcs_json + "\n\nBegin reasoning!"
            else:
                sys_prompt = sys_prompt_zh
                sys_prompt += "[函数列表]=\"\"\"\n" + funcs_json + "\n\n开始推理！"

            messages = [
                {"role": "system", "content": sys_prompt},
            ]

            error = False
            for row_idx in range(0, row_num, 2):
                input_text_cn = input_text = lines[row_idx].strip()
                input_text = "等我到了全聚德王府井店之后给whatsapp的联系人张三发送消息，内容是我到了，你们可以出发了" #444444444444444
                input_text = "今天下午五点帮我给whatsapp的联系人steve发送一条消息，内容是今天下班之后一起去健身房撸铁吧" #444444444444444
                if input_text == "":
                    assert row_idx != 0
                    continue

                if is_english:
                    print("============================", idx, row_idx, "==========English==================")
                    input_text = user_prompt_to_english(input_text)
                    if input_text == "":
                        print("============================", idx, "==============error=====filter=========")
                        error = True
                        break
                    if row_idx == 0:
                        write_log("D:/user_task.txt",input_text_cn, input_text)
                else:
                    print("============================", idx, row_idx, "==========中文==================")

                input_text = "<|Task|>:" + input_text
                func_msg = make_msgs_user(("human", input_text))
                add_msgs_user(messages, func_msg)

                rt, messages = gpt_chat_with_try(messages, is_english, "gpt4turbo", need_check = False, try_times = 3)
                if not rt:
                    print("============================", idx, "==============error==============")
                    error = True
                    break
            if error and not save_whatever:
                if select_wnd:
                    box_rt = msg_box_2button(text="消息解析出现错误，请选择？", bt0=["跳过", "skip"],
                                         bt1=["重试", "retry"], title="英文" if is_english else "中文")
                else:
                    box_rt = "skip"

                if box_rt == "skip":
                    print("============================", idx, "==============skip==============")
                    idx += 1
                    continue
                elif box_rt == "retry":
                    print("============================", idx, "==============retry==============")
                    continue

            if select_wnd:
                box_rt = msg_box_3button(text="是否保存这条信息？", bt0=["保存", "save"], bt1=["跳过", "skip"], bt2=["重试", "retry"], title = "英文" if is_english else "中文")
            else:
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
                with open(output_json, 'w', encoding='utf-8') as f:
                    f.write(texts_json)
            idx += 1
