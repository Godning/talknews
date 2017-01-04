# -*- coding:utf-8 -*-
# !/usr/bin/env python
'''
Created on 2016-12-01
@author: Godning
'''
import tornado.ioloop
import tornado.web
import json
import summary
import recSys

session_id = 1

class MainHandler(tornado.web.RequestHandler):

    def initialize(self):
        #recSys.global_init()
        pass

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')

    def get(self):
        global session_id
        if not self.get_secure_cookie("session"):
            self.set_secure_cookie("session", str(session_id))
            session_id += 1
            print "new user"
        self.render("main.html")

    def post(self, *args, **kwargs):
        user_id = self.get_secure_cookie("session")
        global text
        cmd = self.get_argument("choice")
        #         text = summary.summary(recSys.interactive(user_id, cmd))
        text = recSys.interactive(user_id, cmd)
        #         print(user_id)
        self.write(text)
        #         if cmd == '0':
        #             self.write(u"其他新闻")
        #         else:
        #             text = summary.summary(text)
        #             self.write(text)


settings = {
    "template_path": "templates",
    "static_path": "static",
    "cookie_secret": "SECRET_DONT_LEAK",
}

application = tornado.web.Application([
    (r"/", MainHandler),
], **settings)

if __name__ == "__main__":
    application.listen(8000)
    tornado.ioloop.IOLoop.instance().start()
