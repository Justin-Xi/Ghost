import json
from nltk.translate.bleu_score import SmoothingFunction, sentence_bleu
# from functools import cmp_to_key
# import Levenshtein
from openai import AzureOpenAI
import numpy as np
from datetime import datetime

# use_cmp_type = "embedding"  # embedding,gpt,bleu
use_cmp_type = "bleu"  # embedding,gpt,bleu
use_para_cmp_type = "embedding"  # embedding,gpt,bleu

def safe_chat_create(client, model, messages):
    try:
        response = client.chat.completions.create(model=model, messages=messages)
        msg = response.choices[0]
        if msg.finish_reason == 'content_filter':
            print("error!content_filter 1!")
            return "0"
        return msg.message.content
    except Exception as e:
        print("error!content_filter 2!")
        return "0"

def get_gpt_cmp(pred, gt):
    model_name = "gpt35"
    api_key = "1b35094b9d7841d083386c76a06d2cff"
    azure_endpoint = "https://loox-northcentralus.openai.azure.com/"

    sys_prompt = "请比较下面两个语句表达的含义是否一致，只返回浮点类型的相似度值，不要返回其他内容，越一致越靠近1，越不同越靠近0"
    # sys_prompt = "下面两个语句表达的含义是否一致，一致请回答:是，不一致回答：否"

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )

    input_text = "语句1:“" + pred + "”;语句2:“" + gt + "”"

    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": input_text}
    ]

    content = safe_chat_create(client, model=model_name, messages=messages)
    return float(content)

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def get_embedding_cmp(pred, gt):
    try:
        pred_emb = get_gpt_embedding(pred)
        gt_emb = get_gpt_embedding(gt)
        return cosine_similarity(pred_emb, gt_emb)
    except Exception as e:
        print("get_embedding_cmp error:", pred, gt)
        return 0
def get_gpt_embedding(input):
    # model_name = "embedding"
    model_name = "embedding_s"
    api_key = "a7d194b6355e4b5b83a47979fe20d245"
    azure_endpoint = "https://loox-eastus2.openai.azure.com/"

    client = AzureOpenAI(
      api_key = api_key,
      api_version = "2024-02-15-preview",
      azure_endpoint = azure_endpoint
    )
    response = client.embeddings.create(input=input, model=model_name)
    return response.data[0].embedding

def str_to_json(text):
    try:
        js_value = json.loads(text)
        return js_value
    except Exception as e:
        print("str_to_json json error:", e)
        return None

def cvt_one_msg(line, keyword_list):
    for kwd in keyword_list:
        if line.startswith(kwd):
            key = line[:len(kwd)][2:-3] #remove <| |>:
            value = line[len(kwd):].strip()
            if key == "Action" or key == "Observation": #json
                try:
                    js_value = json.loads(value)
                    return key, js_value
                except Exception as e:
                    print("cvt_one_msg json error:", value)
                    return key, None
            else:
                return key, value
    print("cvt_one_msg json ignore:", line)
    return None, None

def cvt_ai_msg_to_json(text):
    keyword_list = ["<|Task|>:","<|Thought|>:","<|Action|>:","<|Observation|>:","<|Final_Answer|>:"]
    spe_flag = "<#|#|#>"
    # assert text.find(spe_flag) < 0
    text = text.replace(spe_flag, "<#| |#>")
    for kwd in keyword_list:
        text = text.replace(kwd, spe_flag+kwd)
    lines = text.split(spe_flag)
    jsons = {}
    for line in lines:
        if line.strip() == "":
            continue
        key, value = cvt_one_msg(line, keyword_list)
        if key is None:
            continue
        if value is None:
            return None
        jsons[key] = value
    return jsons

def get_ai_answer(json_a_record):
    if 'conversations' not in json_a_record:
        return None
    rt_list = []
    for vl in json_a_record['conversations']:
        if vl['from'] == 'gpt':
            json_vl = cvt_ai_msg_to_json(vl['value'])
            if json_vl is None:
                print("get_ai_answer error json:", vl['value'])
                continue
            rt_list.append(json_vl)
    return rt_list

def ai_answer_to_func_final(json_ai):
    func_list = []
    final_list = []
    for js in json_ai:
        if 'Action' in js:
            func_list.append(js)
        else:
            final_list.append(js)
    return func_list, final_list

def calc_thought_score(pred, gt):
    return calc_string_similarity_score(pred, gt, use_cmp_type)

def calc_eval_thought(json_pred, json_gt):
    max_num = min(len(json_pred),len(json_gt))
    max_num_u = max(len(json_pred),len(json_gt))
    score = 0.0
    for idx in range(max_num):
        if 'Thought' in json_pred[idx] and 'Thought' in json_gt[idx]:
            score += calc_thought_score(json_pred[idx]['Thought'], json_gt[idx]['Thought'])
    return score/max_num_u

def calc_final_answer_score(pred, gt):
    return calc_string_similarity_score(pred, gt, use_cmp_type)

def calc_string_similarity_score(pred, gt, use_type):
    if use_type == "embedding":
        score = get_embedding_cmp(gt, pred)
    elif use_type == "gpt":
        score = get_gpt_cmp(gt, pred)
    else:
        score = sentence_bleu([list(gt)], list(pred), smoothing_function=SmoothingFunction().method3)
    return score
def calc_eval_final_answer(json_pred, json_gt):
    max_num = min(len(json_pred),len(json_gt))
    max_num_u = max(len(json_pred),len(json_gt))
    score = 0.0
    for idx in range(max_num):
        if 'Final_Answer' in json_pred[idx] and 'Final_Answer' in json_gt[idx]:
            score += calc_final_answer_score(json_pred[idx]['Final_Answer'], json_gt[idx]['Final_Answer'])
    return score/max_num_u

def is_valid_func(js):
    return isinstance(js,list) and len(js) > 0 and 'name' in js[0]  and 'parameters' in js[0]

def get_func_name_and_para(js):
    if is_valid_func(js['Action']):
        return js['Action'][0]['name'], js['Action'][0]['parameters']
    else:
        return "",""

def calc_eval_func_name(pred, gt):
    return 1.0 if pred == gt else 0

def calc_eval_para_value(pred, gt):
    return calc_string_similarity_score(str(pred), str(gt), use_para_cmp_type)

def calc_eval_func_para(pred, gt):
    max_num_u = max(len(pred),len(pred))
    score_para_name = 0.0
    score_para_value = 0.0
    score_para_value_imp = 0.0
    unimp_para_list = ['Msg']

    if max_num_u == 0:
        return 1,1,1

    for para in gt:
        if para in pred:
            score_para_name += 1
            value = calc_eval_para_value(pred[para], gt[para])
            score_para_value += value
            if para in unimp_para_list:
                score_para_value_imp += 1
            else:
                score_para_value_imp += value

    return score_para_name/max_num_u, score_para_value/max_num_u, score_para_value_imp/max_num_u

def calc_eval_func(json_pred, json_gt):
    max_num = min(len(json_pred),len(json_gt))
    max_num_u = max(len(json_pred),len(json_gt))
    if max_num_u == 0:
        return {"func_name":1.0, "para_name":1.0, "para_value":1.0, "para_value_imp":1.0}

    def get_actions(js):
        txt = ""
        for j in js:
            if isinstance(j['Action'],list) and len(j['Action']) > 0:
                txt += json.dumps(j['Action'][0], ensure_ascii=False) + ","
            else:
                txt += json.dumps(j['Action'], ensure_ascii=False) + ","
        return txt
    # 感觉不用排序，AI调用函数的顺序应该跟GT是一致的。
    # json_pred = sort_list(json_pred)
    # json_gt = sort_list(json_gt)
    write_log(out_file, "func pred:"+ get_actions(json_pred) + "func gt:" + get_actions(json_gt))

    score_func_name = 0.0
    score_func_para_name = 0.0
    score_func_para_value = 0.0
    score_func_para_value_imp = 0.0
    # 找到两个集合里最相近的函数，做对比
    for idx in range(max_num):
        func_name_pred, func_para_pred = get_func_name_and_para(json_pred[idx])
        func_name_gt, func_para_gt = get_func_name_and_para(json_gt[idx])
        if func_name_pred == func_name_gt:
            score_func_name += calc_eval_func_name(func_name_pred, func_name_gt)
            para_name, para_value, para_value_imp = calc_eval_func_para(func_para_pred, func_para_gt)
            score_func_para_name += para_name
            score_func_para_value += para_value
            score_func_para_value_imp += para_value_imp

    return {"func_name":score_func_name/max_num_u, "para_name":score_func_para_name/max_num_u,
            "para_value":score_func_para_value/max_num_u, "para_value_imp":score_func_para_value_imp/max_num_u}

def calc_eval_field_one(json_pred):
    score = 0.0
    if "Task" in json_pred:
        score -= 0.5
    if "Observation" in json_pred:
        score -= 0.5
    if "Action" in json_pred and "Final_Answer" in json_pred:
        score -= 0.5

    if "Action" in json_pred and "Thought" in json_pred:
        score += 1
    elif "Final_Answer" in json_pred and "Thought" in json_pred:
        score += 1
    elif "Final_Answer" in json_pred:
        score += 0.5
    elif "Action" in json_pred:
        score += 0.5
    return score


def calc_eval_field(json_pred):
    max_num = len(json_pred)
    score = 0.0
    if max_num == 0:
        return score
    for idx in range(max_num):
        score += calc_eval_field_one(json_pred[idx])
    return score/max_num

def eval(json_pred, json_gt):
    if json_pred is None or json_gt is None:
        print("eval error json invalid!")
        return None
    json_pred = get_ai_answer(json_pred)
    json_gt = get_ai_answer(json_gt)
    score_field = calc_eval_field(json_pred)
    score_thought = calc_eval_thought(json_pred, json_gt)
    func_list_pred, final_answer_list_pred = ai_answer_to_func_final(json_pred)
    func_list_gt, final_answer_list_gt = ai_answer_to_func_final(json_gt)
    score_final_answer = calc_eval_final_answer(final_answer_list_pred, final_answer_list_gt)
    score_func = calc_eval_func(func_list_pred, func_list_gt)

    return {"action":score_func, "final_answer":score_final_answer, "field":score_field, "thought":score_thought}

def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(filename, text):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(text)

def write_log(filename, text):
    with open(filename, 'a', encoding='utf-8') as f:
        print(text)
        f.write(text + "\n")

if __name__ == '__main__':
    # text_gt = read_file("../dataset/gt_test.json")
    # text_pred = read_file("../dataset/pred_test.json")
    # score = eval(text_pred, text_gt)
    # print(score)
    root_path = r"D:\_LLM_Eval\20240515/"
    # pred_file = root_path + "ds2_result_387"
    # pred_file = root_path + "gpt4_ghost_user_llm_val_dataset_387_20240515_190344"
    # pred_file = root_path + "llama3_int4_result_387"
    # pred_file = root_path + "llama3_8b_finetune_387"
    pred_file = root_path + "llama3_70b_lora_ghost670_zh_new_prompt_epoch5_0526_6"
    out_file = pred_file + "_score_" +  datetime.now().strftime("%Y%m%d_%H%M%S") +".txt"
    pred_file += ".json"

    text_pred = read_file(pred_file)
    text_gt = read_file(root_path + "gt_ghost_user_llm_val_dataset_zh_387_hj_review_20240524.json")

    json_pred_all = str_to_json(text_pred)
    json_gt_all = str_to_json(text_gt)
    list_num = min(len(json_pred_all),len(json_gt_all))

    score_field = 0.0
    score_thought = 0.0
    score_final_answer = 0.0
    score_func_name = 0.0
    score_para_name = 0.0
    score_para_value = 0.0
    score_para_value_imp = 0.0
    for idx in range(list_num):
        # if idx <266:    # 4444
        #     continue
        json_pred = json_pred_all[idx]
        json_gt = json_gt_all[idx]
        score = eval(json_pred, json_gt)
        if score is None:
            print("error eval!", idx)
            continue
        write_log(out_file, f"{idx},{score}")
        score_thought += score["thought"]
        score_field += score["field"]
        score_final_answer += score["final_answer"]
        score_func_name += score["action"]["func_name"]
        score_para_name += score["action"]["para_name"]
        score_para_value += score["action"]["para_value"]
        score_para_value_imp += score["action"]["para_value_imp"]
        write_log(out_file, f"avg score:para_imp={score_para_value_imp/(idx+1):.4f}, score:score_func_name={score_func_name/(idx+1):.4f},score_para_name={score_para_name/(idx+1):.4f},"
              f"score_para_value={score_para_value/(idx+1):.4f},score_final_answer={score_final_answer/(idx+1):.4f},"
                            f"score_field={score_field/(idx+1):.4f},score_thought={score_thought/(idx+1):.4f}")

    write_log(out_file, f"===========avg score:para_imp={score_para_value_imp / list_num:.4f},score_func_name={score_func_name / list_num:.4f},score_para_name={score_para_name / list_num:.4f},"
          f"score_para_value={score_para_value / list_num:.4f},score_final_answer={score_final_answer / list_num:.4f},"
                        f"score_field={score_field / list_num:.4f},score_thought={score_thought / list_num:.4f}")