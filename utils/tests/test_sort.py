from functools import cmp_to_key
import Levenshtein
import requests

def cmp_list(a,b):
    if a[0] > b[0]:
        return 1
    elif a[0] < b[0]:
        return -1
    else:
        if a[1] > b[1]:
            return 1
        elif a[1] < b[1]:
            return -1
        else:
            return 0
    return 0

def test():
    return 1,2

if __name__ == '__main__':
    xx1 = "dda"
    xx2 = "ddb"
    # cc = strcmp(xx2)
    # a,b = 0,0
    # [a,b] += test()
    str1 = "good1"
    str2 = "1go1od"

    distance = Levenshtein.distance(str1, str2)

    zzz = [["c",10],["b",2],["d",3],["b",1]]

    zzz.sort(key = cmp_to_key(cmp_list))
    print("")

    # # 关键参数列表，会优先根据这个列表对参数排序
    # key_para_list = ['App', 'Receiver', 'Sender', 'Time', 'Type']
    #
    #
    # def cmp_list(a, b):
    #     if a['Action'][0]['name'] == b['Action'][0]['name']:
    #         pass
    #     else:
    #         return 1 if a['Action'][0]['name'] > b['Action'][0]['name'] else -1
    #     return
    #
    #
    # def sort_list(json_list):
    #     json_list.sort(key=cmp_to_key(cmp_list))
    #     return
