import binascii
from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad
import os

def encrypt(data):
    # 参数key: 秘钥，要求是bytes类型，并且长度必须是16、24或32 bytes，因为秘钥的长度可以为：128位、192位、256位
    # 参数mode: 加密的模式，有ECB、CBC等等，最常用的是CBC
    # 参数iv: 初始向量，是CBC加密模式需要的初始向量，类似于加密算法中的盐
    # 创建用于加密的AES对象
    cipher1 = AES.new(key, AES.MODE_CBC, iv)
    # 使用对象进行加密，加密的时候，需要使用pad对数据进行填充，因为加密的数据要求必须是能被128整除
    # pad参数内容，第一个是待填充的数据，第二个是填充成多大的数据，需要填充成128位即16bytes
    ct = cipher1.encrypt(pad(data, 16))
    # 将加密后的结果（二进制）转换成十六进制的或者其它形式
    ct_hex = binascii.b2a_hex(ct)
    return ct_hex


def decrypt(ct_hex):
    # 创建用于解密的AES对象
    cipher2 = AES.new(key, AES.MODE_CBC, iv)
    # 将十六进制的数据转换成二进制
    hex_data = binascii.a2b_hex(ct_hex)
    # 解密完成后，需要对数据进行取消填充，获取原来的数据
    pt = unpad(cipher2.decrypt(hex_data), 16)
    return pt


key = b"TinRdLne20240516@)@$)%!^"
iv = b"v9dl4dfkvorvisl4"

def encrypt_str(text):
    texts_byte = text.encode('utf-8')
    enc_data = encrypt(texts_byte)
    return enc_data

def decrypt_str(data):
    dec_data = decrypt(data)
    text = dec_data.decode('utf-8')
    return text

def split_file_ex(file_name):
    pos = file_name.rfind('.')
    if pos < 0:
        return file_name,""
    return file_name[:pos],file_name[pos+1:]


def encrypt_file(file_name, out_file = None, ext=".cbin"):
    with open(file_name, 'r', encoding='utf-8') as f:
        texts_json = f.read()
    enc_data = encrypt_str(texts_json)
    if out_file is None:
        file_out,_ = split_file_ex(file_name)
        file_out += ext
    else:
        file_out = out_file
    with open(file_out, 'wb') as f:
        f.write(enc_data)
    return file_out


def decrypt_file(file_name, out_file = None, ext=".json"):
    with open(file_name, 'rb') as f:
        enc_data = f.read()
    dec_text = decrypt_str(enc_data)
    if out_file is None:
        file_out,_ = split_file_ex(file_name)
        file_out += "_decry" + ext
    else:
        file_out = out_file
    with open(file_out, 'w', encoding='utf-8') as f:
        f.write(dec_text)
    return file_out

def open_file_auto(file_name, crypt_ext=".cbin", json_ext=".json"):
    if not os.path.exists(file_name):
        print("文件不存在：", file_name)
        return ""
    if file_name.endswith(crypt_ext):
        with open(file_name, 'rb') as f:
            enc_data = f.read()
        dec_text = decrypt_str(enc_data)
        return dec_text
    elif file_name.endswith(json_ext):
        with open(file_name, 'r', encoding='utf-8') as f:
            return f.read()

    print("未知的文件类型：", file_name)
    return ""

def save_file_crypt(texts_json, file_name):
    enc_data = encrypt_str(texts_json)
    with open(file_name, 'wb') as f:
        f.write(enc_data)

def encrypt_path(path_name, out_path, crypt_ext=".cbin", json_ext=".json"):
    os.makedirs(out_path, exist_ok=True)
    for parent, dirnames, filenames in os.walk(path_name):
        for filename in filenames:  #
            if filename.endswith(json_ext):
                out_file,_ = split_file_ex(filename)
                encrypt_file(os.path.join(parent, filename), os.path.join(out_path, out_file+crypt_ext), ext=crypt_ext)
                print("encrypt:",os.path.join(parent, filename))

def decrypt_path(path_name, out_path, crypt_ext=".cbin", json_ext=".json"):
    os.makedirs(out_path, exist_ok=True)
    for parent, dirnames, filenames in os.walk(path_name):
        for filename in filenames:  #
            if filename.endswith(crypt_ext):
                out_file,_ = split_file_ex(filename)
                decrypt_file(os.path.join(parent, filename), os.path.join(out_path, out_file+json_ext), ext=json_ext)
                print("decrypt:",os.path.join(parent, filename))

if __name__ == '__main__':
    # file_name = r"D:\Dataset_llm\dataset_llama3_val/ghost_user_llm_val_dataset_169.json"
    # file_out = encrypt_file(file_name)
    # decrypt_file(file_out)
    # file_path = r"D:\Dataset_llm\dataset_llama3\ghost_user_llm_train_dataset"
    # encrypt_path(file_path, file_path + "_out") #加密
    file_path = r"D:\Dataset_llm_all\dataset_model_train_240613"
    decrypt_path(file_path, file_path + "_decode")  #解密
