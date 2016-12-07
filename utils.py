# -*- coding:utf-8 -*-
'''
Created on 2016-11-29

@author: Godning
'''
import sys,pymysql,jieba,codecs
reload(sys)
sys.setdefaultencoding('utf8')
from config import config

def get_content(id):
    try:
        connection = pymysql.connect(**config)
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            sql = 'select * from news where id = '+str(id)
            cursor.execute(sql)
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        result = cursor.fetchone()
        # print(result)
        # for key in result:
        #    print result[key]
        # s = SnowNLP(result['content'])
        connection.commit()

    finally:
        pass
    return result['content']
    connection.close()


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

