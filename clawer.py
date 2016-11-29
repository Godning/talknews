# -*- coding:utf-8 -*-
'''
Created on 2016-11-23

@author: Godning
'''
import pymysql.cursors
from datetime import date

from config import config
import urllib2
from bs4 import BeautifulSoup
import socket
import httplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')

class Spider(object):
    """Spider"""
    def __init__(self, url):
        self.url = url

    def getNextUrls(self):
        urls = []
        request = urllib2.Request(self.url)
        request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; \
            WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
        try:
            html = urllib2.urlopen(request)
        except socket.timeout, e:
            pass
        except urllib2.URLError,ee:
            pass
        except httplib.BadStatusLine:
            pass

        soup = BeautifulSoup(html,'html.parser')
        for link in soup.find_all('a'):
            print("http://m.sohu.com" + link.get('href'))
            if link.get('href')[0] == '/':
                urls.append("http://m.sohu.com" + link.get('href'))
        return urls

def getNews(url):
    """
    return: News Object
    """
    print url
    xinwen = ''
    request = urllib2.Request(url)
    request.add_header('User-Agent','Mozilla/5.0 (Windows NT 6.1; \
        WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36')
    try:
        html = urllib2.urlopen(request)
    except urllib2.HTTPError, e:
        print e.code

    soup = BeautifulSoup(html, 'html.parser')
    try:
        news_title = soup.h1.string.decode('utf-8')
        news_type = soup.find('div', class_='article-info clearfix').contents[1].span.string
        news_time = soup.find('div', class_='article-info clearfix').contents[3].contents[0]
    except AttributeError,e:
        return None

    for news in soup.select('p.para'):
        xinwen += news.get_text().decode('utf-8')

    news_object = News(source=url,title=news_title,time=news_time,content=xinwen,type=news_type)

    return news_object


class News(object):
    """
    source:from where 从哪里爬取的网站
    title:title of news  文章的标题
    time:published time of news 文章发布时间
    content:content of news 文章内容
    type:type of news    文章类型
    """
    def __init__(self, source, title, time, content, type):
        self.source = source
        self.title = title
        self.time = time
        self.content = content
        self.type = type


def write_data(connection, news):
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            year = 2016
            dd = news.time.split(' ')[0].split('-')
            month = int(dd[0])
            day = int(dd[1])
            sql = 'INSERT INTO news (source, title, time, content, type) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (news.source, news.title, date(year,month,day),news.content,news.type))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception, e:
        print e


def main():
    # Connect to the database
    connection = pymysql.connect(**config)
    # file = open('test.txt', 'a')
    for i in range(38, 50):
        for j in range(1, 5):
            url = "http://m.sohu.com/cr/" + str(i) + "/?page=" + str(j)
            print url
            s = Spider(url)
            for newsUrl in s.getNextUrls():
                news = (connection, getNews(newsUrl))
                if news:
                    write_data(news=news)
                    print "---------------------------"
    # file.close()

    connection.close()

if __name__ == '__main__':
    main()

