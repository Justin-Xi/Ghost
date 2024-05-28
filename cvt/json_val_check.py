import json


def check_str(text):
    try:
        data = json.loads(text)
        for ln in data:
            if "role" in ln and "function_call" in ln:
                if "arguments" in ln["function_call"]:
                    try:
                        data2 = json.loads(ln["function_call"]["arguments"])
                    except Exception as e:
                        print("check_str function_call arguments error !!!!")
                        return False
                    # print("")
    except Exception as e:
        return False
    return True

def check_file(filename):
    with open(filename, 'r', encoding='utf-8-sig') as f:
        lines = f.readlines()

    val = True
    for idx,line in enumerate(lines):
        if not check_str(line):
            print("json error:", idx, line, filename)
            val = False

    return val


if __name__ == '__main__':
    # filename = r"G:\Dataset_llm\dataset_intent_openai_replace\output\output_openai_train_022_01_02_0102_cmn_with_cot_6000.jsonl"
    # check_file(filename)
    filename_in = r"D:\Dataset_llm\dataset_llama3/val_dataset - 1_send_msg_pos_out.json"
    filename_out = r"D:\Dataset_llm\dataset_llama3/val_dataset_1_send_msg_pos_out.json"
    with open(filename_in, 'r', encoding='utf-8') as f:
        texts_json = f.read()

    out_list = json.loads(texts_json)
    texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
    with open(filename_out, 'w', encoding='utf-8') as f:
        f.write(texts_json)
