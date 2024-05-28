from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
from cvt.convert_intent_csv_openai_val import load_csv_inpath
from fine_tuning.test_gpt import gpt_chat
import json

def change_label_to_json(label):
    label_json = json.loads("[" + label + "]")
    return label_json

def get_function_call_msg_text(message):
    msg = []
    for m in message:
        if 'function_call' in m:
            msg.append(m)
    return json.dumps(msg, ensure_ascii=False)[1:-1]
def gpt_chat_bleu(input_text, sys_prompt, label, model_name):
    print("label",label)
    message = gpt_chat(input_text, sys_prompt, model_name)
    label_json = change_label_to_json(label)
    if len(label_json) <= 1:
        # all
        predict = json.dumps(message[2:], ensure_ascii=False)[1:-1]
    else:
        label = get_function_call_msg_text(label_json)
        predict = get_function_call_msg_text(message)
    bleu_score = sentence_bleu([list(label)], list(predict), smoothing_function=SmoothingFunction().method3)
    return bleu_score


def val_bleu():
    sys_prompt = "你的角色是Ghost个人助理，你需要一步一步来完成被吩咐的事项。如果需要总结，尽量简洁，30字以内。"

    raw_data_path = r"G:\Dataset_llm\dataset_intent_openai_replace/raw_data_val/"
    model_name1 = "test_034"
    model_name2 = "test_038"
    model_name3 = "test_039"

    raw_data = load_csv_inpath(raw_data_path, columns_num=4)
    bleus1 = []
    bleus2 = []
    bleus3 = []
    for idx, row in enumerate(raw_data):
        input_text = row[0]
        label = row[2] + row[3]
        bleu_score = gpt_chat_bleu(input_text, sys_prompt, label, model_name1)
        bleus1.append(bleu_score)
        print("bleu-4:", bleu_score)
        bleu_score = gpt_chat_bleu(input_text, sys_prompt, label, model_name2)
        bleus2.append(bleu_score)
        print("bleu-4:", bleu_score)
        bleu_score = gpt_chat_bleu(input_text, sys_prompt, label, model_name3)
        bleus3.append(bleu_score)
        print("bleu-4:", bleu_score)

    if bleus1:
        average_bleus = sum(bleus1) / len(bleus1)
        print(model_name1, "=== mean bleu-4:", average_bleus)
    if bleus2:
        average_bleus = sum(bleus2) / len(bleus2)
        print(model_name2, "=== mean bleu-4:", average_bleus)
    if bleus3:
        average_bleus = sum(bleus3) / len(bleus3)
        print(model_name3, "=== mean bleu-4:", average_bleus)

if __name__ == '__main__':
    val_bleu()
