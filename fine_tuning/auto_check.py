import json
import tools4dataset_zh as custom_tools
import tool_funcs
from langchain_core.utils.function_calling import convert_to_openai_function
from openai import AzureOpenAI

def gpt_chat(input_text):
    model_name= "gpt4turbo"
    api_key = "a7d194b6355e4b5b83a47979fe20d245"
    azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    sys_prompt = "你是一个function call 检查助手，负责检查function call每一步调用是否正确，参数是否正确，如果发现有错误，说出具体位置和原因" \
                 ";如果没有发现错误输出”正确“;如果没有function call也不需要调用function call也是正确的。function call如果有条件，要看清这个条件，" \
                 "没有明确符合条件就发送的视作错误。"

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
    return


def get_func_info(name, functions):
    for func in functions:
        if name == func['name']:
            return json.dumps(func, ensure_ascii=False)
    assert False
    return ""
def check_result(messages):
    tools = tool_funcs.funcs(custom_tools)
    functions=[convert_to_openai_function(t) for t in tools]
    # str_func = json.dumps(functions, ensure_ascii=False)
    str_func = ""
    for msg in messages:
        if 'function_call' in msg:
            str_func += "," + msg['function_call']['name'] + ":" + get_func_info(msg['function_call']['name'], functions)

    str_msg = json.dumps(messages, ensure_ascii=False)
    if str_func != "":
        str_msg += "其中function_call的函数信息如下，仔细检查调用的函数是否正确，使用的参数是否正确，description 中有详细函数及参数描述，如果函数或参数不在这个列表里视为错误；type=null的参数是可以忽略的参数，其他参数不能被忽略，务必检查正确性。" + str_func
    str_msg += "请判断以上这个流程是否正确？如果是正确的流程请先输出“正确”再输出其他信息;如果有多出错误请全部列出来并给出正确的脚本。"
    gpt_chat(str_msg)
    return