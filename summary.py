# -*- coding:utf-8 -*-
'''
Created on 2016-11-28

@author: Godning
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import math,codecs,jieba


def sen_similarity_calc(seg_list, threshold):
    w = []
    for i in range(len(seg_list)):
        w.append([])
        for j in range(len(seg_list)):
            common = [word for word in seg_list[i] if word in seg_list[j]]
            ans = len(common) / (math.log(len(seg_list[i]))+math.log(len(seg_list[j])))
            if ans > threshold:
                w[i].append(1)
            else:
                w[i].append(0)
    return w


def get_seg_list(text):
    stop_words_file = "stopwords.txt"
    stop_words = []

    for word in codecs.open(stop_words_file, 'r', 'utf-8', 'ignore'):
        stop_words.append(word.strip())

    sentences = text.split(u'。')
    seg_list = []
    for item in sentences:
        words = [word for word in jieba.cut(item, cut_all=False) if word not in stop_words]
        if len(words) != 0:
            seg_list.append(words)
        # seg_list.append(jieba.cut(item, cut_all=False))
    return seg_list, sentences


def get_summary(seg_list, sentences, threshold):
    w = sen_similarity_calc(seg_list, threshold)
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
    for i in range(min(len(num_dict), 2)):
        summary += sentences[num_dict[i][0]]+u"。"
    return summary


def summary(text= ""):

    seg_list, sentences = get_seg_list(text)
    return get_summary(seg_list, sentences, 0.7)


if __name__ == '__main__':
    #text = get_content(1653)
    text = ""
    seg_list, contences = get_seg_list(text)
    summary = get_summary(seg_list, contences, threshold=0.6)
    print summary
