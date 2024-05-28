from convert_intent_csv_replace_step1 import read_from_txt,write_to_txt,write_to_json,read_from_txt_path,write_to_json_with_cot
import tools4dataset_lite as custom_tools
import tool_funcs
from json import dumps as json_dumps
from langchain_core.utils.function_calling import convert_to_openai_function

def get_function_list_json(del_para):
    tools = tool_funcs.funcs(custom_tools)
    functions = [convert_to_openai_function(t) for t in tools]
    if del_para:
        tool_funcs.del_func_paras(functions, is_train=True)
    funcs_json = json_dumps(functions)
    return funcs_json

if __name__ == '__main__':
    is_file = False
    system_prompt = "你的角色是Ghost个人助理"
    # system_prompt =None
    funcs_json = get_function_list_json(del_para = True)   #True
    # funcs_json = None
    shuffle = True  #True
    add_cot = False #False
    output_json_filename = r"G:\Dataset_llm\dataset_intent_openai_replace/output/output_openai_train_036_01_02ais_0102ais_4000_rand_with_para.jsonl"
    if is_file:
        input_filename = r"G:\Dataset_llm\dataset_intent_openai_replace/output/output_openai_train_common_3001.txt"
        user_content_list, ai_content_list, ai_summary_content_list = read_from_txt(input_filename)
    else:
        input_path = r"G:\Dataset_llm\dataset_intent_openai_replace/output/1_2_2ai/"
        user_content_list, ai_content_list, ai_summary_content_list = read_from_txt_path(input_path)
    write_to_json(user_content_list, ai_content_list, ai_summary_content_list, output_json_filename, system_prompt, funcs_json, shuffle, add_cot)

    print("end:", len(user_content_list))