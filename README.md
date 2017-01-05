# 2016-课程设计

## 当前完成情况
* 爬虫：clawer.py(爬取搜狐新闻，极简）
* == 添加关键词列表 （3）
* 文本摘要：summary.py(TextRank算法，我也不知道写的对不对，反正就是摘要了）
* 文本相似度对比：similary.py(新闻查重）（这个东西已经不用了）
* 推荐系统：基于内容的推荐（主要是冷启动问题）
* 后端模块：采用tornado 不到30行，主要是get和post请求再加上处理一下跨域问题
* 前端：直接jquery了，不想加动画，。。。
* 雏形有了，后续问题还很多，先写文档。。。找个时间再改改爬虫

## Demo
![Demo](https://github.com/Godning/talknews/blob/master/demo.png)

## Bug
* 爬虫不能识别异常url 
* 推荐系统的准确性
* 用户信息存储问题