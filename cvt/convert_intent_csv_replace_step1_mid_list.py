from convert_intent_csv_replace_step1 import read_from_txt,write_to_txt,write_to_json,read_from_txt_path,write_to_json_with_cot,rand_cat_conv_list
import os

# 每个目录下取base_num个，混合mix_num个
def read_sub_path(input_path):
    files = os.listdir(input_path)
    directories = [os.path.join(input_path, file) for file in files if os.path.isdir(os.path.join(input_path, file))]
    return directories

if __name__ == '__main__':
    input_path = r"G:\Dataset_llm\dataset_intent_openai_replace\mid_txt\output_0428/"
    output_filename = r"G:\Dataset_llm\dataset_intent_openai_replace/output/output_01_02_ais"
    output_filename_base = output_filename + "_base.txt"
    output_filename_mix = output_filename + "_mix.txt"
    base_num = 500
    mix_num = 500 * 4

    a1_bs,a2_bs,a3_bs = [],[],[]
    a1_la,a2_la,a3_la = [],[],[]
    sub_path_list = read_sub_path(input_path)
    for sub_path in sub_path_list:
        a1,a2,a3 = read_from_txt_path(sub_path)
        a1_bs += a1[:base_num]
        a2_bs += a2[:base_num]
        a3_bs += a3[:base_num]
        a1_la += a1[base_num:]
        a2_la += a2[base_num:]
        a3_la += a3[base_num:]


    write_to_txt(a1_bs,a2_bs,a3_bs, output_filename_base, False)
    print("end:", base_num, output_filename_base)

    _, user_content_list3, ai_content_list3 = rand_cat_conv_list(a1_la, a2_la, mix_num, del_user_con = True)
    write_to_txt(user_content_list3, ai_content_list3, [], output_filename_mix, True)
    print("end:", mix_num, output_filename_mix)

