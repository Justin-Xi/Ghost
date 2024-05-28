import csv
import random
import json

import numpy as np
import os
import tools4dataset_lite as custom_tools
import tool_funcs
from json import dumps as json_dumps
from langchain_core.utils.function_calling import convert_to_openai_function
from pypinyin import lazy_pinyin
import json_val_check

def load_csv(filename, columns_num):
    csv_reader = csv.reader(open(filename,encoding='utf-8-sig'))
    lines = []
    for idx,row in enumerate(csv_reader):
        if len(row) != columns_num:
            print(idx, "warning=======invalid line================", filename, len(row))
            continue
        if len(row) == 1:
            lines.append(row[0])
        else:
            lines.append(row)
    return lines

def load_csv_inpath(names_path, columns_num):
    lines = []
    for parent, dirnames, filenames in os.walk(names_path):
        for filename in filenames:  #
            if filename.endswith('.csv'):
                lines += load_csv(os.path.join(parent, filename), columns_num)
    return lines

def str_replace(text):
    return text.replace("\"", "'").replace("\n", "；").replace("\t", " ")

def text_replace(text, rep, to):
    to = str_replace(to)
    if rep == "[mingzi]":
        text = text.replace("[mingzi_pinyin]", name2pinyin(to))
    return text.replace(rep, to)

def rand_replace(text1, text2, text3, repl_table):
    for repl in repl_table:
        assert len(repl[1]) > 0
        rand_num = random.randint(0,len(repl[1])-1)
        text1 = text_replace(text1, repl[0],repl[1][rand_num])
        text2 = text_replace(text2, repl[0],repl[1][rand_num])
        text3 = text_replace(text3, repl[0],repl[1][rand_num])
    return text1, text2, text3

def replace_kong(user_content, ai_content, name_kong, name_raw, fd_name):
    name_no_kong = name_kong.replace("/kong]", "]")
    need_this_fd = False
    if user_content.find(name_no_kong) >= 0:
        # 如果user content中有不带kong的这个字段，说明一定需要这个字段
        need_this_fd = True
        user_content = user_content.replace(name_no_kong, name_kong)
    if ai_content.find(name_kong) >= 0 and user_content.find(name_kong) < 0:    # user content没有，只有json里有，直接删除字段
        name_kong_w_type = ",\\\"" + fd_name + "\\\":\\\"" + name_kong + "\\\""
        ai_content = ai_content.replace(name_kong_w_type, "")
    elif user_content.find(name_kong) >= 0:
        name_kong_w_type = ",\\\"" + fd_name + "\\\":\\\"" + name_kong + "\\\""
        assert ai_content.find(name_kong_w_type) >= 0
        if need_this_fd or random.randint(0, 1) == 0:  # no kong
            user_content = user_content.replace(name_kong, name_raw)
            ai_content = ai_content.replace(name_kong, name_raw)
        else:
            user_content = user_content.replace(name_kong, "")
            ai_content = ai_content.replace(name_kong_w_type, "")

    return user_content, ai_content
def replace_engine(user_content, ai_content, ai_summary_content, repl_table):
    user_content, ai_content = replace_kong(user_content, ai_content, "[shijian/kong]", "[shijian]", "Time")
    user_content, ai_content = replace_kong(user_content, ai_content, "[weidubiaoji/kong]", "[weidubiaoji]", "Type")
    user_content, ai_content = replace_kong(user_content, ai_content, "[sender_mingzi/kong]", "[mingzi]", "Sender")

    user_content, ai_content = replace_kong(user_content, ai_content, "[jiage/kong]", "[jiage]", "Price")
    user_content, ai_content = replace_kong(user_content, ai_content, "[weizhi/kong]", "[weizhi]", "Location")
    user_content, ai_content = replace_kong(user_content, ai_content, "[fanwei/kong]", "[fanwei]", "Range")
    user_content, ai_content = replace_kong(user_content, ai_content, "[shuliang/kong]", "[shuliang]", "Limit")
    user_content, ai_content = replace_kong(user_content, ai_content, "[paixufangshi/kong]", "[paixufangshi]", "OrderBy")
    user_content, ai_content = replace_kong(user_content, ai_content, "[dianyingleixing/kong]", "[dianyingleixing]", "MovieType")




    for repl in repl_table:
        assert len(repl[1]) > 0
        rand_num = random.randint(0, len(repl[1]) - 1)
        if isinstance(repl[1][rand_num], list):
            assert len(repl[1][rand_num]) == 2
            user_content = text_replace(user_content, repl[0],repl[1][rand_num][0])
            ai_content = text_replace(ai_content, repl[0],repl[1][rand_num][1])
        else:
            user_content = text_replace(user_content, repl[0],repl[1][rand_num])
            ai_content = text_replace(ai_content, repl[0],repl[1][rand_num])

    return user_content, ai_content, ai_summary_content

def name2pinyin(name):
    name_py = lazy_pinyin(name)
    name_pystr = ""
    for py in name_py:
        if name_pystr != "":
            name_pystr += " "
        name_pystr += py
    return name_pystr

def check_json(prom, text, idx):
    if len(text) > 0:
        if text[-1] != ",":
            print("json check 1 failed:", idx, prom, text)
            return
        else:
            text = text[:-1]
    if not json_val_check.check_str("[" + text + "]"):
        print("json check 2 failed:", idx, prom, text)


def get_conv_list_raw(path):
    raw_data_path = path + "raw_data/"
    raw_data = load_csv_inpath(raw_data_path, columns_num=4)
    print("==============line num raw:", len(raw_data))

    user_content_list = []
    ai_content_list = []
    ai_summary_content_list = []
    for idx, row in enumerate(raw_data):
        row0 = row[0].replace("\"", "'").replace("\n", "; ")
        check_json(row0, row[2], idx)
        check_json(row0, row[3] + ",", idx)
        user_content_list.append(row0)
        ai_content_list.append(row[2])
        ai_summary_content_list.append(row[3])
    return len(raw_data), user_content_list, ai_content_list, ai_summary_content_list

def gen_read_msg(name, msg):
    read_msg_list = []
    read_msg_list2 = []
    read_msg_list3 = []
    for idx in range(len(msg)):
        read_msg_list.append(name[random.randint(0,len(name)-1)] + ":“" + msg[random.randint(0,len(msg)-1)] + "”")
        read_msg_list2.append(name[random.randint(0,len(name)-1)] + ":“" + msg[random.randint(0,len(msg)-1)] + "”")
    for idx in range(len(msg)):
        range_len = random.randint(2,3)
        text = ""
        for idx2 in range(range_len):
            if text != "":
                text += ";"
            text += read_msg_list2[random.randint(0,len(read_msg_list2)-1)]
        read_msg_list3.append(text)
    read_msg_list += read_msg_list3
    return read_msg_list

def get_conv_list_rep(path, convert_num, fix_summary):
    raw_data_path = path + "raw_data_rep/"
    raw_data = load_csv_inpath(raw_data_path, columns_num=4)
    # print("==============line num rep:", len(raw_data))

    tool_path = path + "tool/"
    msg_path = path + "msg/"
    name_path = path + "name/"
    receivername_path = path + "receivername/"
    unread_path = path + "unread/"
    time_path = path + "time/"

    tool2_path = path + "tool2/"
    location_path = path + "location/"
    range_path = path + "range/"
    price_path = path + "price/"
    limit_path = path + "limit/"
    orderby_path = path + "orderby/"
    movietype_path = path + "movietype/"
    moviemsg_path = path + "moviemsg/"

    tool = load_csv_inpath(tool_path, columns_num=1)
    msg = load_csv_inpath(msg_path, columns_num=1)
    name = load_csv_inpath(name_path, columns_num=1)
    receivername = load_csv_inpath(receivername_path, columns_num=2)
    time = load_csv_inpath(time_path, columns_num=2)
    unread_flag = load_csv_inpath(unread_path, columns_num=2)
    read_msg = gen_read_msg(name, msg)

    tool2 = load_csv_inpath(tool2_path, columns_num=1)
    location = load_csv_inpath(location_path, columns_num=2)
    range_flag = load_csv_inpath(range_path, columns_num=1)
    price = load_csv_inpath(price_path, columns_num=2)
    limit = load_csv_inpath(limit_path, columns_num=2)
    orderby = load_csv_inpath(orderby_path, columns_num=1)
    movietype = load_csv_inpath(movietype_path, columns_num=1)
    movie_msg = load_csv_inpath(moviemsg_path, columns_num=1)

    repl_table = [["[gongju]", tool],
                  ["[gongju1]", tool],
                  ["[gongju2]", tool],
                  ["[mingzi]", name],
                  ["[mingzi1]", name],
                  ["[mingzi2]", name],
                  ["[receiver_mingzi]", receivername],
                  ["[xiaoxi]", msg],
                  ["[shijian]", time],
                  ["[weidubiaoji]", unread_flag],
                  ["[chakanxiaoxi]", read_msg],

                  ["[localgongju]", tool2],
                  ["[weizhi]", location],
                  ["[fanwei]", range_flag],
                  ["[jiage]", price],
                  ["[shuliang]", limit],
                  ["[paixufangshi]", orderby],
                  ["[dianyingleixing]", movietype],
                  ["[chazhaoneirong]", movie_msg],
                  ]

    user_content_list = []
    ai_content_list = []
    ai_summary_content_list = []
    num = 0
    if len(raw_data) == 0:
        print("replace 表空的！")
        return num, user_content_list, ai_content_list, ai_summary_content_list
    while num < convert_num:
        for row in raw_data:
            # row0, row2, row3 = rand_replace(row[0], row[2], row[3], repl_table)
            check_json(row[0], row[2], num)
            check_json(row[0], row[3] + ",", num)
            row0, row2, row3 = replace_engine(row[0], row[2], row[3], repl_table)
            row0 = row0.replace("\"", "'").replace("\n", "; ")
            check_json(row0, row[2], num)
            check_json(row0, row[3] + ",", num)
            user_content_list.append(row0)
            ai_content_list.append(row2)
            if fix_summary is not None:
                ai_summary_content_list.append(fix_summary)
            else:
                ai_summary_content_list.append(row3)
            num += 1
            if num >= convert_num:
                break

    return num, user_content_list, ai_content_list, ai_summary_content_list

def del_user_content(text, del_user_con):
    if del_user_con:
        con_head = "{\"role\": \"user\", \"content\": \""
        con_end = "\"},"
        assert text.startswith(con_head)
        assert text.endswith(con_end)
        text2 = text[len(con_head):-len(con_end)]
        return text2
    else:
        return text

def rand_cat_conv_list(user_content_list, ai_content_list, convert_num, del_user_con = False):
    assert len(user_content_list) == len(ai_content_list)
    user_content_list2 = []
    ai_content_list2 = []
    cat_range = [2, 3]
    while len(user_content_list2) < convert_num:
        cat_num = random.randint(cat_range[0],cat_range[1])
        text_user = ""
        text_ai = ""
        for idx in range(cat_num):
            rand_idx = random.randint(0,len(user_content_list)-1)
            if text_user != "":
                text_user += "。"
            # if text_ai != "":
            #     text_ai += ","
            text_user += del_user_content(user_content_list[rand_idx], del_user_con)
            text_ai += ai_content_list[rand_idx]
        user_content_list2.append(text_user)
        ai_content_list2.append(text_ai)
    return convert_num, user_content_list2, ai_content_list2

def add_step_flag(user_content, ai_content, ai_summary_content):
    if ai_content == "":
        return user_content, ai_content, ai_summary_content
    assert ai_content[-1] == ","
    try:
        ai_cont_json = json.loads("[" + ai_content[:-1] + "]")
    except Exception as e:
        print("ai json error !!!!")
        assert False

    text_step_list = "step_list:"
    idx = 0
    while idx < len(ai_cont_json):
        assert ai_cont_json[idx]['role'] == 'assistant'
        assert ai_cont_json[idx+1]['role'] == 'function'
        assert ai_cont_json[idx]['function_call']['name'] == ai_cont_json[idx+1]['name']
        text_step_list += f"[{idx//2}]{ai_cont_json[idx]['function_call']['name']};"
        idx += 2

    text_step_list += "end;"

    idx = 0
    while idx < len(ai_cont_json):
        assert ai_cont_json[idx]['role'] == 'assistant'
        assert ai_cont_json[idx+1]['role'] == 'function'
        assert ai_cont_json[idx]['function_call']['name'] == ai_cont_json[idx+1]['name']
        text_step_now = f"step_now:[{idx//2}]{ai_cont_json[idx]['function_call']['name']};"
        ai_cont_json[idx]['content'] = text_step_list+text_step_now if idx==0 else text_step_now
        idx += 2

    ai_content2 = json.dumps(ai_cont_json, ensure_ascii=False)
    ai_content = ai_content2[1:-1] + ","
    return user_content, ai_content, ai_summary_content

def get_step_flag(ai_content):
    assert ai_content[-1] == ","
    try:
        ai_cont_json = json.loads("[" + ai_content[:-1] + "]")
    except Exception as e:
        print("ai json error !!!!")
        assert False

    text_step_list = "step_list:"
    idx = 0
    while idx < len(ai_cont_json):
        assert ai_cont_json[idx]['role'] == 'assistant'
        assert ai_cont_json[idx+1]['role'] == 'function'
        assert ai_cont_json[idx]['function_call']['name'] == ai_cont_json[idx+1]['name']
        text_step_list += f"[{idx//2}]{ai_cont_json[idx]['function_call']['name']};"
        idx += 2

    return text_step_list

def write_to_json_with_cot(user_content_list, ai_content_list, ai_summary_content_list, output_filename, system_prompt, system_prompt_pre, funcs_json):
    assert len(user_content_list) == len(ai_content_list) and len(user_content_list) == len(ai_summary_content_list)
    system_text_pre = "{\"role\": \"system\", \"content\": \""+ system_prompt_pre +"\"}," if system_prompt_pre is not None else ""
    system_text = "{\"role\": \"system\", \"content\": \""+ system_prompt +"\"}," if system_prompt is not None else ""
    texts = ""
    for idx in range(len(user_content_list)):
        assert ai_summary_content_list[idx] != ""
        cot_content = get_step_flag(ai_content_list[idx])
        cot_text = "{\"role\": \"assistant\", \"content\": \"" + cot_content + "\"},"
        # user_content, ai_content, ai_summary_content = add_step_flag(user_content_list[idx], ai_content_list[idx], ai_summary_content_list[idx])
        # txt = system_text + user_content + ai_content + ai_summary_content
        txt = system_text_pre + user_content_list[idx] + cot_text + system_text + user_content_list[idx] + ai_content_list[idx] + ai_summary_content_list[idx]
        if funcs_json is None:
            txt_all = "{\"messages\": ["+ txt +"]}\n"   #不加函数调用
        else:
            txt_all = "{\"messages\": ["+ txt +"], \"functions\":"+ funcs_json +"}\n"
        texts += txt_all

    with open(output_filename, 'w',encoding='utf-8-sig') as f:
        f.write(texts)

def write_to_json(user_content_list, ai_content_list, ai_summary_content_list, output_filename, system_prompt, funcs_json, shuffle, add_cot):
    assert len(user_content_list) == len(ai_content_list) and len(user_content_list) == len(ai_summary_content_list)
    if shuffle:
        list_all = list(zip(user_content_list, ai_content_list, ai_summary_content_list))
        random.shuffle(list_all)
        user_content_list, ai_content_list, ai_summary_content_list = list(zip(*list_all))

    system_text = "{\"role\": \"system\", \"content\": \""+ system_prompt +"\"}," if system_prompt is not None else ""
    texts = ""
    for idx in range(len(user_content_list)):
        # assert ai_summary_content_list[idx] != ""
        if add_cot:
            user_content, ai_content, ai_summary_content = add_step_flag(user_content_list[idx], ai_content_list[idx], ai_summary_content_list[idx])
            txt = system_text + user_content + ai_content + ai_summary_content
        else:
            txt = system_text + user_content_list[idx] + ai_content_list[idx] + ai_summary_content_list[idx]
        if funcs_json is None:
            txt_all = "{\"messages\": ["+ txt +"]}\n"   #不加函数调用
        else:
            txt_all = "{\"messages\": ["+ txt +"], \"functions\":"+ funcs_json +"}\n"
        texts += txt_all

    with open(output_filename, 'w',encoding='utf-8-sig') as f:
        f.write(texts)

def write_to_txt(user_content_list, ai_content_list, ai_summary_content_list, output_filename, add_user_content):
    assert len(user_content_list) == len(ai_content_list)
    texts = ""
    for idx in range(len(user_content_list)):
        if add_user_content:
            user_text = "{\"role\": \"user\", \"content\": \"" + user_content_list[idx] + "\"},"
        else:
            user_text = user_content_list[idx]

        if idx < len(ai_summary_content_list):
            txt = user_text + "\t" + ai_content_list[idx] + "\t" + ai_summary_content_list[idx] + "\n"
        else:
            txt = user_text + "\t" + ai_content_list[idx] + "\t\n"
        texts += txt

    with open(output_filename, 'w',encoding='utf-8-sig') as f:
        f.write(texts)

def read_from_txt(filename):
    with open(filename, 'r',encoding='utf-8-sig') as f:
        lines = f.readlines()

    user_content_list = []
    ai_content_list = []
    ai_summary_content_list = []
    for line in lines:
        if line[-1] == "\n":
            line = line[:-1]
        ln = line.split("\t")
        assert len(ln) == 3
        user_content_list.append(ln[0])
        ai_content_list.append(ln[1])
        ai_summary_content_list.append(ln[2])

    return user_content_list, ai_content_list, ai_summary_content_list

def read_from_txt_path(names_path):
    user_content_list = []
    ai_content_list = []
    ai_summary_content_list = []
    for parent, dirnames, filenames in os.walk(names_path):
        for filename in filenames:  #
            if filename.endswith('.txt'):
                user_content_list2, ai_content_list2, ai_summary_content_list2 = read_from_txt(os.path.join(parent, filename))
                user_content_list += user_content_list2
                ai_content_list += ai_content_list2
                ai_summary_content_list += ai_summary_content_list2
    return user_content_list, ai_content_list, ai_summary_content_list

def do_convert(path, convert_num, output_file, need_cat, fix_summary):
    output_path = path + "output/"
    output_filename = output_path + output_file

    if need_cat:
        convert_num_base = convert_num * 4
        convert_num_cat = convert_num
    else:
        convert_num_base = convert_num
        convert_num_cat = 0

    line_num, user_content_list, ai_content_list, ai_summary_content_list = get_conv_list_raw(path)
    assert line_num < convert_num_base
    _, user_content_list2, ai_content_list2, ai_summary_content_list2 = get_conv_list_rep(path, convert_num_base-line_num, fix_summary)
    user_content_list += user_content_list2
    ai_content_list += ai_content_list2
    if fix_summary is not None:
        ai_summary_content_list += ai_summary_content_list2

    if need_cat:
        _, user_content_list3, ai_content_list3 = rand_cat_conv_list(user_content_list, ai_content_list, convert_num_cat)
        write_to_txt(user_content_list3, ai_content_list3, [], output_filename, True)
        return

    # tools = tool_funcs.funcs(custom_tools)
    # functions=[convert_to_openai_function(t) for t in tools]
    # tool_funcs.del_func_paras(functions)
    # funcs_json = json_dumps(functions)
    #
    # # system_text = "{\"role\": \"system\", \"content\": \""+ system_prompt +"\"},"
    # system_text = "" # 不加system prompt
    write_to_txt(user_content_list, ai_content_list, ai_summary_content_list, output_filename, True)
    return


if __name__ == '__main__':
    # fix_summary = "{\"role\": \"assistant\", \"content\": \"消息已查看。\"}"
    fix_summary = None
    root_path = r"D:\Dataset_llm\dataset_intent_openai_replace/"
    convert_num = 250
    output_file = "output_openai_train_2_1_2500.txt"
    need_cat = False    #True 只导出拼接的
    do_convert(root_path, convert_num, output_file, need_cat, fix_summary)

    # convert_num = 1000
    # output_file = "output_openai_train_019_test.txt"
    # need_cat = True    #True 只导出拼接的
    # do_convert(root_path, convert_num, output_file, need_cat, fix_summary)

    print("end:", convert_num)