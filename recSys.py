# -*- coding: utf-8 -*-

'''
Created on 2016-12-4

@author: Finley
'''

import pymysql.cursors
import random
import sys
import cmd
from numpy import median
from math import sqrt
from sklearn.metrics.pairwise import cosine_similarity
from matplotlib.cbook import Null

reload(sys)
sys.setdefaultencoding('utf8')

''' global variable '''
global user_debug
user_debug = True

news_entries = {}  # Contains all the news which specially group by 'topic'
recommended_list = {}  # Contains the index of the recommended news returned by content_based
#     recommend system. Different user has different recommendation list.
#     Its structure likes below:
#     {'user_id1': rec_list1, 'user_id2': rec_list2, ...}
history_news_list = {}  # Contains all the news that had been recommended. In case
#     repeat recommending. Different user has different history
#     list. Its structure likes below:
#     {'user_id1': his_list1, 'user_id2': his_list2, ...}
global deny_threshold
deny_threshold = 2  # The deny threshold. If times that user deny recommendation more than
#    that, recommendation should change topic.
# The different user is related with different key word list, so we should
#     use dictionary to record hash between user and key word list.
#     The structure likes below:
#     {'user_id1': deny1/next1, 'user_id2': deny2/next2, ...}
deny = {}  # If user refuse the recommend news twice, then change the topic.
#     The initial value is zero and each value is different
#     depend on different user.
next = {}  # Record the position of the next recommended news in the recommended list
#     calculated by content_based recommend algorithm. The initial value
#     is zero and each value is different depend on different user.
cur_top = {}  # Current news topic. Different user should has different current topic.
#     It's a dictionary. {'user_id1': cur_top1, 'user_id2': cur_top2, ...}
cur_news = {}  # Current news content. Different user should has different current news.
#     It's a dictionary. {'user_id1': cur_news1, 'user_id2': cur_news2, ...}
# Connect to the database
connection = pymysql.connect(host='127.0.0.1',
                             port=3306,
                             user='root',
                             password='zmf123',
                             db='rec',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

'''
Read news data from database, and then transform it
to special format.

DATA FORMAT especially like below:
    {'topic': [('id', 'title', 'key words', 'content', 'source'),(...)],
            ...}
Specially the field 'key words' is a directory like below:
    {'key1': frequency, 'key2': frequency, ...}
'''


def read_from_db():
    try:
        # first construct the structure of entries.
        # 1. keys -- all the topics.
        with connection.cursor() as cursor:
            # 执行sql语句，查询所有的新闻类别
            sql = 'select type from news GROUP BY type;'
            cursor.execute(sql)
        result = cursor.fetchall()
        for entry in result:
            for key in entry:
                news_entries[entry[key]] = []
        # 2. value -- news group
        topics = news_entries.keys()
        for topic in topics:
            #             print topic
            with connection.cursor() as cursor:
                # 分类查询新闻，并将新闻组加至相应的 key 下
                sql = 'select * from news where type = \'' + topic + '\';'
                #                 sql = 'select * from news where type = \'' + topic + '\' and id < 80;'
                cursor.execute(sql)
            result = cursor.fetchall()
            news_group = []
            # 构建新闻列表组
            for entry in result:
                # 将每条新闻构建成一个元组
                for key in entry:
                    if key == 'id':
                        id = entry[key]
                    elif key == 'source':
                        source = entry[key]
                    elif key == 'title':
                        title = entry[key]
                    elif key == 'content':
                        content = entry[key];
                    elif key == 'keyword':
                        keys = translate_keysfld(entry[key])
                news_group.append((id, title, keys, content, source))
            # 将其添加至相应key下
            news_entries[topic] = news_group
        # 没有设置默认自动提交，需要主动提交，以保存所执行的语句
        connection.commit()

    finally:
        #         if specific_debug:
        #             pass
        #         else:
        #             connection.close()
        pass


'''
(Optional)Used to format the field 'keys', for the 'keys' field is a dictionary structure.

@param keys_str: The string of 'keys' field. The format specially likes below:
                 'key1:freq1,key2:freq2,...'
@return: The translated dictionary of given keys string.
'''


def translate_keysfld(keys_str):
    key_words = {}
    pants_list = keys_str.split(',')
    for pants in pants_list:
        fields = pants.split(':')
        keyword = fields[0]
        frequency = fields[1]
        key_words[keyword] = int(frequency)
    return key_words


'''
Calculate the median of the given list. The data format must be list.

@param alist: The given list, value must be numeric.
@return: The median of given list.
'''


def get_median(alist):
    # judge the 'NULL' spot.
    if alist == []:
        return []
    blist = sorted(alist)
    length = len(alist)
    if length % 2 == 1:
        # length of list is odd so return middle element.
        return blist[int(((length + 1) / 2) - 1)]
    else:
        # length of list is even so compute midpoint.
        v1 = blist[int(length / 2)]
        v2 = blist[(int(length / 2) - 1)]
        return (v1 + v2) / 2.0


'''
Calculate absolute standard deviation of given list and median.

@param alist: The given list, value must be numeric.
@param median: The median of the given list.
@return: The absolute standard deviation of given list.
'''


def get_abs_std_dev(alist, median):
    summ = 0
    for item in alist:
        summ += abs(item - median)
    return summ / len(alist)


'''
Normalize column of given list, make sure normalized value is between 0 and 1.
Used after selecting key words(feature)

@param list: The data list to be normalized.
             The data format is like: [(index1, [frequency1, frequency2, ...]), (index2, [...]), ...]
'''


def normalize(klist):
    # get length of instance key word vector
    klen = len(klist[0][1])
    # now normalize the list
    for colnum in range(klen):
        # first extract values to list
        col = [v[1][colnum] for v in klist]
        median = get_median(col)
        asd = get_abs_std_dev(col, median)
        for v in klist:
            if asd == 0:
                v[1][colnum] = 0
            else:
                v[1][colnum] = (v[1][colnum] - median) / asd


'''
Calculate the cosine similarity of the two given vector.
The vector element must be numeric.

@param vec1: The first given vector.
@param vec2: The second given vector.
@return: The cosine similarity of two given vector.
'''


def cos_similarity(vec1, vec2):
    xy = 0
    xl = 0
    yl = 0
    vlen = len(vec1)
    for i in range(vlen):
        xy += vec1[i] * vec2[i]
        xl += vec1[i] ** 2
        yl += vec2[i] ** 2
    if xl == 0 or yl == 0:
        return 0
    else:
        return xy / sqrt(xl * yl)


'''
Compute the distance between the specific vector and given vector list.
No return instance, but modify the recommended_list for current news topic and key words.
The modified recommended_list is sorted.

@param user_id: The user id.
@param svec: The specific vector we want to know its neighbor.
@param vec_list: The given vector list, the neighbor is selected from it.
                 Its structure likes below:
                     [(index1, [frequency1, frequency2, ...]), (index2, [...]), ...]
'''


def compute_neighbors(user_id, svec, vec_list):
    # first clear the recommended list.
    recommended_list[user_id][:] = []
    # second calculate the distance between neighbors.
    for cvec in vec_list:
        distance = cos_similarity(svec, cvec[1])
        recommended_list[user_id].append((cvec[0], distance))
    # third sort the recommended list.
    recommended_list[user_id].sort(key=lambda newsTuple: newsTuple[1],
                                   reverse=True)


'''
Recommend news from news_entries specific by current topic and key words.
It does not return the specified news, but modify the recommended_list(global variable).
When we use the content-based recommend, it is return the news from recommend_list.

@param user_id: The user id, used in var{cur_top} and var{cur_news}.
@param choose_keys: The custom function used to choose key words later used
                    in calculating nearest neighbor list as feature.
'''


def content_recommend(user_id, choose_keys=None):
    # Step 1: Create news features list based on current keys(regard it as feature).
    news_flist = []
    spec_newslen = len(news_entries[cur_top[user_id]])
    cur_wkeys = cur_news[user_id][2].keys()
    # if no need to change the keys, use the top three key words.
    if choose_keys != None:
        selected_keys = choose_keys(cur_wkeys)  # function pointer
    else:
        selected_keys = cur_wkeys[0:5]
    # generate the specific news feature list.
    for index in range(spec_newslen):
        news_keys = news_entries[cur_top[user_id]][index][2]  # it is a dictionary
        keys_freq = []
        for key in selected_keys:
            if key in news_keys.keys():
                keys_freq.append(news_keys[key])
            else:
                keys_freq.append(0)
        news_flist.append((index, keys_freq))
        # the news_flist is like below: [(index1, [freq1, freq2, ...]), (index2, [...]), ...]
    # Step 2: Normalize the news feature list.
    normalize(news_flist)
    # Step 3. Calculate the nearest neighbor and refresh the recommended list.
    #    get the normalized current news from news_flist.
    for i in range(spec_newslen):
        if cur_news[user_id][0] == news_entries[cur_top[user_id]][i][0]:
            cnews_kfreq = news_flist[i][1]
    # now compute neighbors.
    compute_neighbors(user_id, cnews_kfreq, news_flist)
    # end ...


'''
Custom function. Used to choose key words from given key words list.
The algorithm is self-defined.
'''


def choose_keys(keys_list):
    # waiting for realizing~~~
    # depend on yourself
    return keys_list[-6:-1]


'''
Randomly select one news from news_entries and recommend it to user.
Especially used on the spot *init* or *change_topic*.

@param current: The current topic user was reading. If no need to
                change topic, it should be empty.
@return: The tuple of fresh news recommended to user and its topic. Format likes below:
         (topic, ('field1', 'field2', ...))
'''


def random_recommend(current=''):
    topics = news_entries.keys();
    # current is empty means the *init* spot, otherwise the *change_topic* spot.
    while True:
        top_index = random.randint(0, len(topics) - 1)
        rec_topic = topics[top_index];
        if current != '' and rec_topic == current:
            # means that it is on the *change_topic* spot.
            continue
        else:
            # means:
            # 1. the *init* spot OR
            # 2. the *change_topic* spot and recommended topic is differrent from current.
            break
    # now random select news corresponded to special topic.
    news_index = random.randint(0, len(news_entries[rec_topic]) - 1)
    # return the recommend news.
    return (rec_topic, news_entries[rec_topic][news_index])


'''
Global initialization.
'''


def global_init():
    # Initialization operation. Including news entries list,
    #    random recommendation and recommended news list.
    read_from_db()


'''
Interactive with client, handle the post command.
This function is called by itself.

@param user_id: The user id, different user should returned different news.
@param cmd: The command sended by client, indicates whether to recommend relative news.
@param repeat: The flag indicates whether current recommend news had been recommended before.
@return: The recommended news content.
'''


def handle_post(user_id, cmd, repeat):
    global deny_threshold
    # If "deny/next" dictionary do not contain the var{user_id}, it means
    #     this user is first access the page.
    if not deny.has_key(user_id):
        # debug
        if user_debug:
            print 'do not contain the user id: ', user_id
        deny[user_id] = 0
        next[user_id] = 0
        recommended_list[user_id] = []
        history_news_list[user_id] = []
        recommendation = random_recommend()
        cur_top[user_id] = recommendation[0]
        cur_news[user_id] = recommendation[1]
        # initialize the content-based recommended list.
        content_recommend(user_id, choose_keys)
        # debug
        if user_debug:
            print 'The user id is: ', user_id
            print 'The news id ---> ', recommendation[1][0]
            print recommendation[0]
            show_keys(recommendation[1], True)
            print '\n'
        # debug
        return recommendation[1][3]

    if cmd == '1':
        # debug
        if user_debug:
            print 'cmd = 1, topic, keys same'
        # debug
        deny[user_id] = 0
        next[user_id] += 1  # recommend next news.
        # get news from news entries list.
        rec_news = news_entries[cur_top[user_id]][recommended_list[user_id][next[user_id]][0]]
        recommendation = (cur_top[user_id], rec_news)
    elif cmd == '0':
        # if the current recommend news is not repeat, continue normal logic,
        #     otherwise do not calculate var{deny}.
        if repeat == False:
            deny[user_id] += 1
        # Different operation based on var{deny}.
        if deny[user_id] == deny_threshold:
            # debug
            if user_debug:
                print 'cmd = 0, twice, topic change'
                # debug
            recommendation = random_recommend(cur_top[user_id])
            deny[user_id] = 0
        else:
            # debug
            if user_debug:
                print 'cmd = 0, once, key change'
                # debug
            # need to change the key word(which used as feature to compute distance)
            content_recommend(user_id, choose_keys)
            if repeat == False:
                next[user_id] = 1
            else:
                next[user_id] += 1
            rec_news = news_entries[cur_top[user_id]][recommended_list[user_id][next[user_id]][0]]
            recommendation = (cur_top[user_id], rec_news)

    if is_repeat_recommended(user_id, recommendation[1][0]):
        return handle_post(user_id, cmd, True)
    else:
        history_news_list[user_id].append(recommendation[1][0])
        cur_top[user_id] = recommendation[0]
        cur_news[user_id] = recommendation[1]
        # debug
        if user_debug:
            print 'The user id is: ', user_id
            print 'The news id ---> ', recommendation[1][0]
            print recommendation[0]
            show_keys(recommendation[1], True)
            print '\n'
        # debug
        return recommendation[1][3]


'''
Whether the current news has been recommended.

@param user_id: The user id, judge specific user.
@param news_id: The news id.
@return: Whether current news had been recommended before.
'''


def is_repeat_recommended(user_id, news_id):
    for rid in history_news_list[user_id]:
        if rid == news_id:
            return True
    return False


'''
Handle the command sended by client.
Called by server.

@param user_id: The user id, different user should returned different news.
@param cmd: The command sended by client.
@return: The recommend news content.
'''


def interactive(user_id, cmd):
    return handle_post(user_id, cmd, False)


'''
Get specified news from database corresponding to the given id.
Used in 'specific debug' mode.

@param id: The given id
@return: The tuple of specified news and its topic. Like below:
         (topic, ('field1', 'field2', ...))
'''


def get_news_byid(id):
    try:
        with connection.cursor() as cursor:
            # 执行sql语句，查询所有的新闻类别
            sql = 'select * from news where id=%d;' % id
            cursor.execute(sql)
        result = cursor.fetchall()
        for entry in result:
            for field in entry:
                if field == 'id':
                    id = entry[field]
                elif field == 'source':
                    source = entry[field]
                elif field == 'title':
                    title = entry[field]
                elif field == 'content':
                    content = entry[field];
                elif field == 'type':
                    type = entry[field]
                elif field == 'keyword':
                    keys = translate_keysfld(entry[field])
            spec_news = (id, title, keys, content, source)
            connection.commit()

    finally:
        pass
        connection.close()

    return (type, spec_news)


'''
Show the key words and its frequency of each news. The as-feature key words can
be show as well.

@param news: The specified news that you wanna to show its key words.
@param show_feature: Whether to show the as-feature key words.
'''


def show_keys(news, show_feature=False):
    show_keys = ''
    feature = ''
    count = 0
    for (key, value) in news[2].items():
        if count < 5:
            feature += key + ', '
        show_keys += key + (': %d' % value) + ',  '
        count += 1
    if show_feature:
        print 'Feature key word:'
        print '[', feature[:-2], ']'
    print 'The news key words:'
    print '[', show_keys[:-3], ']'

