# -*- coding:utf-8 -*-
'''
Created on 2016-11-28

@author: Godning
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')

import jieba,codecs,math,pymysql
from config import config

connection = pymysql.connect(**config)

def get_content():
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            sql = 'select * from news where id = 3'
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        result = cursor.fetchone()
        # print(result)
        # for key in result:
        #    print result[key]
        # s = SnowNLP(result['content'])
        connection.commit()

    finally:
        connection.close()
    return result['content']


def get_seg_list(text):
    stop_words_file = "stopwords.txt"
    stop_words = []

    for word in codecs.open(stop_words_file, 'r', 'utf-8', 'ignore'):
        stop_words.append(word.strip())

    sentences = text.split(u'。')
    seg_list = []
    for item in sentences:
        seg_list.append([word for word in jieba.cut(item, cut_all=False) if word not in stop_words])
        # seg_list.append(jieba.cut(item, cut_all=False))
    return seg_list,sentences


def sen_similarity_calc(seg_list):
    w = []
    for i in range(len(seg_list)):
        w.append([])
        for j in range(len(seg_list)):
            common = [word for word in seg_list[i] if word in seg_list[j]]
            ans = len(common) / (math.log(len(seg_list[i]))+math.log(len(seg_list[j])))
            if ans>0.6:
                w[i].append(1)
            else:
                w[i].append(0)
    return w


def get_summary(seg_list, sentences):
    w = sen_similarity_calc(seg_list)
    """
    for i in range(len(w)):
        for j in range(len(w[i])):
            print w[i][j],' ',
        print
    """
    from numpy import *

    m = mat(w)

    pr = []
    for i in range(len(w)):
        pr.append([1])

    pr = mat(pr)
    for i in range(100):
        pr = 0.15 + 0.85 * m * pr

    rank_dict = {}
    for i in range(len(pr)):
        rank_dict[i] = pr[i][0]

    # print rank_dict

    num_dict = sorted(rank_dict.items(), key=lambda items: items[1], reverse=True)
    # print num_dict
    summary = u""
    for i in range(3):
        summary += sentences[num_dict[i][0]]
    return summary

if __name__ == '__main__':
    text = get_content()
    seg_list, contences = get_seg_list(text)
    summary = get_summary(seg_list, contences)
    print summary
