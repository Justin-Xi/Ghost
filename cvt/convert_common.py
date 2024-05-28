import json
import os
import random


def read_from_txt_path(names_path):
    lines = []
    for parent, dirnames, filenames in os.walk(names_path):
        for filename in filenames:  #
            if filename.endswith('.jsonl'):
                with open(os.path.join(parent, filename), 'r',encoding='utf-8') as f:
                    lines += f.readlines()
    return lines

def str_replace(text):
    return text.replace("\"", "'").replace("\r", " ").replace("\n", " ").replace("\t", " ").replace("\\", " ").replace("/", " ").replace("\b", " ").replace("\f", " ")

if __name__ == '__main__':
    input_filename = r"G:\Dataset_llm\dataset_intent_openai_replace\common/"
    lines = read_from_txt_path(input_filename)

    output_filename = r"G:\Dataset_llm\dataset_intent_openai_replace\output/output_openai_train_common_3000.txt"
    convert_num = 3000

    all_txt = ""
    for idx in range(convert_num):
        ln_json = json.loads(lines[random.randint(0, len(lines)-1)])
        ln_txt = ""
        assert len(ln_json['conversation']) > 0
        for js1 in ln_json['conversation']:
            if ln_txt != "":
                ln_txt += ","
            js_user = {"role": "user", "content": str_replace(js1['human'])}
            js_ai = {"role": "assistant", "content": str_replace(js1['assistant'])}
            # ln_txt += json.dumps(js_user, ensure_ascii=False) + "," + json.dumps(js_ai, ensure_ascii=False)
            ln_txt += "{\"role\": \"user\", \"content\": \"" + str_replace(js1['human']) + "\"},{\"role\": \"assistant\", \"content\": \"" + str_replace(js1['assistant']) + "\"}"
        ln_txt += "\t\t\n"
        all_txt += ln_txt

    with open(output_filename, 'w', encoding='utf-8-sig') as f:
        f.write(all_txt)
        print("end:", convert_num)