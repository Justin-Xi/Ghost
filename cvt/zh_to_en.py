from openai import AzureOpenAI

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

def user_prompt_to_english(input_text, sys_prompt):
    model_name = "gpt4turbo"    # only gpt4 can do

    if model_name == "gpt4turbo":
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False


    input_text = "需要翻译的内容如下：“" + input_text + "”"

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
    return content


def write_log(filename, input_txt_zh, input_txt_en, input_txt_en2):
    if input_txt_zh[-1] != "\n":
        input_txt_zh += "\n"
    if input_txt_en[-1] != "\n":
        input_txt_en += "\n"
    if input_txt_en2[-1] != "\n":
        input_txt_en2 += "\n"
    input_txt_zh = "\n" + input_txt_zh
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(input_txt_zh)
        f.write(input_txt_en)
        f.write(input_txt_en2)


if __name__ == '__main__':
    root_path = r"D:\_Work_llm/用户指令，中英对照.txt"
    with open(root_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    sys_prompt1 = "你是一个翻译助手，请把下面的内容译成英语，确保英文和中文表达了相同的含义，尽量使用普通口语，非常亲密朋友之间的口语，尝试2种不同的翻译，用1,2标记"
    sys_prompt2 = "please simulate a scenario that I am sending an oral command to a smart speaker and ask the device to take actions upon the command. translate tthe following chinese command into english and try to mimic oral and casual tone like a nativeenglish speaker"

    for idx,line in enumerate(lines):
        # if idx < 24:
        #     continue
        if idx % 2 == 1:
            continue
        print(idx, line)
        line_en = user_prompt_to_english(line, sys_prompt1)
        if line_en == "":
            continue
        line_en = line_en.replace("\n\n", "\n")
        line_en2 = user_prompt_to_english(line, sys_prompt2)
        if line_en2 == "":
            continue
        line_en2 = "3: " + line_en2
        line_en2 = line_en2.replace("\n\n", "\n")
        print(idx, line)
        print(line_en)
        print(line_en2)
        write_log("D:/out.txt", line, line_en, line_en2)
