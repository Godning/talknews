# -*- coding:utf-8 -*-
'''
Created on 2016-11-23

@author: Godning
'''
import pymysql
import urllib2
from bs4 import BeautifulSoup
import socket
import httplib
import sys
reload(sys)
sys.setdefaultencoding('utf8')
import codecs,jieba
from config import config


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


def get_seg_list(text):
    stop_words_file = "stopwords.txt"
    stop_words = [' ', '\n']

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


def get_keyword_list(text):
    tags = []
    num = []
    seg_list_tmp, sen = get_seg_list(text)
    seg_list = []
    for list in seg_list_tmp:
            seg_list.extend(list)

    for word in seg_list:
        if word in tags and word != ' ':
            index = tags.index(word)
            num[index] += 1
        else:
            tags.append(word)
            num.append(1)
    for i in range(len(num)):
        for j in range(len(num)):
            if(num[i]>num[j]):
                tmp = num[i]
                num[i] = num[j]
                num[j] = tmp
                tmp = tags[i]
                tags[i] = tags[j]
                tags[j] = tmp
    wordlist = []
    try:
        for i in range(6):
            wordlist.append((tags[i],num[i]))
    finally:
        keyword_str = ""
        for word, value in wordlist:
            keyword_str += word + ':' + str(value) + ','
        return keyword_str[:-1]


def getNews(url, news_type):
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
    except AttributeError,e:
        return None

    for news in soup.select('p.para'):
        xinwen += news.get_text().decode('utf-8')
    if len(xinwen) <20: return None
    news_object = News(source=url, title=news_title, content=xinwen, keywordlist=get_keyword_list(xinwen), type=news_type)


    return news_object


class News(object):
    """
    source:from where 从哪里爬取的网站
    title:title of news  文章的标题
    time:published time of news 文章发布时间
    content:content of news 文章内容
    type:type of news    文章类型
    """
    def __init__(self, source, title, content, type, keywordlist):
        self.source = source
        self.title = title
        self.content = content
        self.type = type
        self.keywordlist = keywordlist


def write_data(connection, news):
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，插入记录
            sql = 'INSERT INTO news (source, title, content, keyword, type) VALUES (%s, %s, %s, %s, %s)'
            cursor.execute(sql, (news.source, news.title, news.content, news.keywordlist, news.type))
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()
    except Exception, e:
        print e


def main():
    # Connect to the database
    connection = pymysql.connect(**config)
    # file = open('test.txt', 'a')
    n_type = {2:u"新闻", 3:u"体育", 4:u"娱乐", 5:u"财经", 6:u"时尚",7:u"科技", 8:u"军事", 9:u"星座"}
    """
    2:：新闻，3：体育，4：娱乐，5：财经，6：时尚，7：科技，8：军事，9：星座
    """
    for i in range(2, 9):
        for j in range(1, 5):
            url = "http://m.sohu.com/cr/" + str(i) + "/?page=" + str(j)
            news_type = n_type[i]
            print url
            s = Spider(url)
            for newsUrl in s.getNextUrls():
                news = getNews(newsUrl, news_type)
                if news:
                    write_data(connection=connection, news=news)
                    print "---------------------------"
    # file.close()

    connection.close()

if __name__ == '__main__':
    main()


