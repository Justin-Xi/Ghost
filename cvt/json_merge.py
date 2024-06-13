import json
import os
import random
from datetime import datetime

def load_json_inpath(names_path):
    jsons = []
    for parent, dirnames, filenames in os.walk(names_path):
        for filename in filenames:  #
            if filename.endswith('.json'):
                with open(os.path.join(parent, filename), 'r', encoding='utf-8') as f:
                    texts_json = f.read()
                out_list = json.loads(texts_json)
                jsons += out_list
    return jsons


if __name__ == '__main__':
    input_path = r"D:\Dataset_llm_all\dataset_model_train_240613_decode"
    jsons = load_json_inpath(input_path)
    texts_json = json.dumps(jsons, ensure_ascii=False, indent=2)
    filename_out = input_path + "_" + str(len(jsons)) + "_" + datetime.now().strftime("%Y%m%d_%H%M%S") +".json"
    with open(filename_out, 'w', encoding='utf-8') as f:
        f.write(texts_json)

    print("end:",len(jsons), filename_out)
