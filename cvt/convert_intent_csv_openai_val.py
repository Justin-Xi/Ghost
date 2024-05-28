import csv
import random
import json

import numpy as np
import os
import tools4dataset_lite as custom_tools
import tool_funcs
from json import dumps as json_dumps
from langchain_core.utils.function_calling import convert_to_openai_function
import cvt.json_val_check as json_val_check

def check_json(prom, text, idx):
    if len(text) > 0:
        if text[-1] != ",":
            print("json check 1 failed:", idx, prom, text)
            return
        else:
            text = text[:-1]
    if not json_val_check.check_str("[" + text + "]"):
        print("json check 2 failed:", idx, prom, text)

def load_csv(filename, columns_num):
    csv_reader = csv.reader(open(filename,encoding='utf-8-sig'))
    lines = []
    for idx,row in enumerate(csv_reader):
        if len(row) != columns_num:
            print(idx, "=======invalid line================", len(row))
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


def do_convert(path, system_prompt):
    raw_data_path = path + "raw_data_val/"
    output_path = path + "output/"
    output_filename = output_path + "output_openai_common_val_020.jsonl"
    raw_data = load_csv_inpath(raw_data_path, columns_num=4)
    print("==============line num:", len(raw_data))

    # tools = tool_funcs.funcs(custom_tools)
    # functions=[convert_to_openai_function(t) for t in tools]
    # tool_funcs.del_func_paras(functions)
    # funcs_json = json_dumps(functions)

    # system_text = "{\"role\": \"system\", \"content\": \""+ system_prompt +"\"},"

    texts = ""
    for idx, row in enumerate(raw_data):
        row0 = row[0].replace("\"", "'").replace("\n", "; ")
        check_json(row0, row[2], idx)
        check_json(row0, row[3] + ",", idx)
        user_text = "{\"role\": \"user\", \"content\": \"" + row0 + "\"},"
        txt = user_text + row[2] + row[3]
        # txt = user_text + row[2][:-1]
        # txt_all = "{\"messages\": ["+ txt +"], \"functions\":"+ funcs_json +"}\n"
        txt_all = "{\"messages\": ["+ txt +"]}\n"   #不加函数调用
        texts += txt_all
    with open(output_filename, 'w',encoding='utf-8-sig') as f:
        f.write(texts)


if __name__ == '__main__':
    root_path = r"G:\Dataset_llm\dataset_intent_openai_replace/"
    system_prompt = "你的角色是Ghost个人助理"
    do_convert(root_path, system_prompt)
    print("end:")