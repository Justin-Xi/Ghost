from cvt.cvt_llama3_step1 import *

def gpt_chat2(messages, model_name):

    if model_name == "gpt4turbo":
        api_key = "a7d194b6355e4b5b83a47979fe20d245"
        azure_endpoint = "https://loox-eastus2.openai.azure.com/"
    else:
        assert False

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    msg = safe_chat_create_with_retry(client, model=model_name, messages=messages, retry_times=5)
    if msg is None:
        print("============gpt4===error=========1==========")
        return messages
    ai_type, ai_json = get_ai_msg_type(msg)
    add_msgs_ai(messages, msg, ai_type, ai_json)
    return messages

if __name__ == '__main__':
    select_wnd = False

    if True:
        input_filename = r"D:\Dataset_llm\dataset_llama3_val/ghost_user_llm_val_dataset_387_20240515_190344"
        output_json = input_filename + "_out_" + datetime.now().strftime("%Y%m%d_%H%M%S") +".json"
        input_filename += ".json"
        to_json = True

        with open(input_filename, 'r', encoding='utf-8') as f:
            text_pred = f.read()
        input_lines = json.loads(text_pred)

        begin_idx = 0

        out_list = []
        idx = 0
        while idx < len(input_lines):
            if idx < begin_idx:
                idx += 1
                continue
            print("=============", idx, "========================")
            json_line = input_lines[idx]
            sys_prompt = json_line['system']
            messages = [
                {"role": "system", "content": sys_prompt},
            ]
            error = False
            row_num = len(json_line['conversations'])
            for row_idx in range(0, row_num, 2):
                user_prompt = json_line['conversations'][row_idx]
                assert user_prompt['from'] == 'human'
                input_text = user_prompt['value']
                func_msg = make_msgs_user(("human", input_text))
                add_msgs_user(messages, func_msg)

                messages = gpt_chat2(messages, "gpt4turbo")

            messages = to_sharegpt_format(messages)
            out_list.append(messages)
            if to_json:
                texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
                with open(output_json, 'w', encoding='utf-8') as f:
                    f.write(texts_json)
            idx += 1
