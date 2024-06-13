import json
import random

from crypto import open_file_auto
import tools4dataset_zh as custom_tools_zh
import tools4dataset_en as custom_tools_en
from tool_funcs import *

def load_json(filename):
    texts_json = open_file_auto(filename)
    out_list = json.loads(texts_json)
    return out_list

def is_func_name_in_conver(func_name, conversations):
    for conver in conversations:
        if conver['from'] == 'gpt':
            if conver['value'].find(func_name) >= 0:
                return True
    return False
def get_usefull_func(functions, conversations, uselessnum=7):
    funcs_usefull = []
    funcs_useless = []
    funcs_new = []
    for func in functions:
        if is_func_name_in_conver(func['name'],conversations):
            funcs_usefull.append(func)
        else:
            funcs_useless.append(func)
    for idx in range(uselessnum):
        rand_pos = random.randint(0, len(funcs_useless)-1)
        funcs_new.append(funcs_useless[rand_pos])
        del funcs_useless[rand_pos]
    funcs_new += funcs_usefull
    random.shuffle(funcs_new)
    return funcs_new

if __name__ == '__main__':
    sys_prompt_en = open_file_auto("../cfg/system_prompt_en.txt",json_ext=".txt")
    sys_prompt_zh = open_file_auto("../cfg/system_prompt_zh2.txt",json_ext=".txt")

    # sys_prompt_en = load_json(r"E:\Download/ghost_user_llm_test_dataset - 2_search_msg_pos_out_20240607_192746.cbin")[0]
    # sys_prompt_zh = load_json(r"E:\Download/ghost_user_llm_test_dataset - 2_search_msg_pos_out_20240607_192644.cbin")[0]

    # filename = r"G:\Dataset_llm\dataset_intent_openai_replace\output\output_openai_train_022_01_02_0102_cmn_with_cot_6000.jsonl"
    # check_file(filename)
    filename_in = r"D:\Dataset_llm_all\dataset_model_train_240613_decode_153_20240613_112311"
    filename_out = filename_in + "_func_rand_del.json"
    filename_in += ".json"

    out_list = load_json(filename_in)
    for line in out_list:
        is_english = line['system'].startswith("You are a tool invocation expert. ")
        custom_tools = custom_tools_en if is_english else custom_tools_zh
        functions = funcs_json(custom_tools)
        functions = get_usefull_func(functions, line['conversations'], uselessnum=7)
        funcs_js = json.dumps(functions, ensure_ascii=False)
        if is_english:
            sys_prompt = sys_prompt_en
            sys_prompt += "[Function List]=\"\"\"\n" + funcs_js + "\n\nBegin reasoning!"
        else:
            sys_prompt = sys_prompt_zh
            sys_prompt += "[函数列表]=\"\"\"\n" + funcs_js + "\n\n开始推理！"
        line['system'] = sys_prompt
    texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
    with open(filename_out, 'w', encoding='utf-8') as f:
        f.write(texts_json)
