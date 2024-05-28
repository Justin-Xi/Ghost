import json

def load_json(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        texts_json = f.read()
    out_list = json.loads(texts_json)
    return out_list


if __name__ == '__main__':

    sys_prompt_en = load_json(r"D:\Dataset_llm\dataset_llama3_val/ghost_en_user_llm_test_dataset_2_watch_msg_pos_asr_out_20240524_114827.json")[0]
    sys_prompt_zh = load_json(r"D:\Dataset_llm\dataset_llama3_val/ghost_zh_user_llm_test_dataset_2_watch_msg_pos_asr_out_20240524_114754.json")[0]

    # filename = r"G:\Dataset_llm\dataset_intent_openai_replace\output\output_openai_train_022_01_02_0102_cmn_with_cot_6000.jsonl"
    # check_file(filename)
    filename_in = r"D:\Dataset_llm\dataset_llama3_val/gt_ghost_user_llm_val_dataset_zh_387_hj_review"
    filename_out = filename_in + "_out.json"
    filename_in += ".json"

    out_list = load_json(filename_in)
    for line in out_list:
        if line['system'][:10] == sys_prompt_en['system'][:10]:
            line['system'] = sys_prompt_en['system']
        elif line['system'][:10] == sys_prompt_zh['system'][:10]:
            line['system'] = sys_prompt_zh['system']
        else:
            print("没有找到对应的sys_prompt：", line['system'])
    texts_json = json.dumps(out_list, ensure_ascii=False, indent=2)
    with open(filename_out, 'w', encoding='utf-8') as f:
        f.write(texts_json)
