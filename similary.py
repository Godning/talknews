# -*- coding:utf-8 -*-
'''
Created on 2016-11-29

@author: Godning
'''
import sys,math
reload(sys)
sys.setdefaultencoding('utf8')

from utils import *

def get_similary(textA,textB,threshold):
    seg_list_a, l1 = get_seg_list(textA)
    seg_list_b, l2 = get_seg_list(textB)
    seg_a = []
    seg_b = []
    for item in seg_list_a:
        seg_a.extend(item)
    for item in seg_list_b:
        seg_b.extend(item)
    total_key = []
    total_key.extend(seg_a)
    total_key.extend(seg_b)
    total_key = list(set(total_key))
    dic_a = [0] * len(total_key)
    dic_b = [0] * len(total_key)
    for key in seg_a:
        dic_a[total_key.index(key)] += 1
    for key in seg_b:
        dic_b[total_key.index(key)] += 1
    up = 0
    down1 = 0
    down2 = 0
    for key in range(len(total_key)):
        up += dic_a[key] * dic_b[key]
        down1 += dic_a[key] ** 2
        down2 += dic_b[key] ** 2

    cos_ans = up / (math.sqrt(down1)*math.sqrt(down2))
    print cos_ans
    if cos_ans > threshold:
        return True
    else:
        return False

if __name__ == '__main__':
    textA = get_content(110)

    textB = get_content(112)
    print get_similary(textA,textB,0.6)
    db_close()
