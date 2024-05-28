import random

from openai import AzureOpenAI

def gen_user_prompt_input(model_name):
    if model_name == "gpt4turbo":
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    elif model_name == "gpt35":
        api_key = "1b35094b9d7841d083386c76a06d2cff"
        azure_endpoint = "https://loox-northcentralus.openai.azure.com/"
    else:
        assert False

    sys_prompt = "你是一个文案生成助手，负责生成对话任务，这些任务用来控制ai助手操作手机上的app，这个app包括微信、飞书、钉钉等，" \
                 "你要模拟日常使用环境，生成任务包括发送消息、接收消息、转发消息等，可以复杂一些，用跟人类聊天的方式产生任务，尽量随意自然。" \
                 "用json的方式返回[{\"content\":任务内容1},{\"content\":任务内容2}]，一下返回10组以上，尽量每条有显著的差别。"
    input_text = "加入一些有条件的操作，比如看看我的未读消息，有张三发给我的就转给李四等，不要照抄这一句，有自己的想法"

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
    return msg.message.content

def get_user_msg(messages):
    for msg in messages:
        if msg['role'] == 'user':
            return msg['content']

    assert False
    return ""

def str_replace(text):
    return text.replace("\"", "'").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("/", " ").replace("\b", " ").replace("\f", " ")

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

def gen_user_prompt_function(model_name, is_english, messages):
    model_name = "gpt4turbo"    # only gpt4 can do

    if model_name == "gpt4turbo":
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    elif model_name == "gpt35":
        api_key = "1b35094b9d7841d083386c76a06d2cff"
        azure_endpoint = "https://loox-northcentralus.openai.azure.com/"
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