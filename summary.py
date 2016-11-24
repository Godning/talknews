# -*- coding:utf-8 -*-
'''
Created on 2016-11-25

@author: Godning
'''
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import jieba
from snownlp import SnowNLP
import pymysql.cursors
from datetime import date

config = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': '123',
    'db': 'clawer',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor,
}
connection = pymysql.connect(**config)

try:
    with connection.cursor() as cursor:
        # 执行sql语句，插入记录
        sql = 'select * from news where id = 1'
        cursor.execute(sql)
    # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
    result = cursor.fetchone()
    #print(result)
    #for key in result:
    #    print result[key]
    s = SnowNLP(result['content'])
    connection.commit()

finally:
    connection.close()

summ = s.summary(5)
for item in summ:
    print item
