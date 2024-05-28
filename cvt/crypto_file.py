from tkinter import filedialog
import os
from crypto import *

def open_file():
    filetypes = (
        ('cbin files', (('*.cbin'),('*.json'),('*.txt'))),
        ('All files', '*.*')
    )
    filename = filedialog.askopenfilename(
        title='Open a file',
        initialdir='/',
        filetypes=filetypes)

    print(filename)
    return filename


if __name__ == '__main__':
    input_file = open_file()
    if os.path.exists(input_file):
        if input_file.lower().endswith(".json") or input_file.lower().endswith(".txt"):
            # json 文件转成cbin文件
            out_file, _ = split_file_ex(input_file)
            out_file += ".cbin"
            if os.path.exists(out_file):
                print("json文件转换失败，cbin文件已存在！", input_file)
            else:
                encrypt_file(input_file, out_file)
        elif input_file.lower().endswith(".cbin"):
            out_file, _ = split_file_ex(input_file)
            out_file += ".json"
            if os.path.exists(out_file):
                print("文件转换失败，json文件已存在！", input_file)
            else:
                decrypt_file(input_file, out_file)

