#!/usr/bin/env python
# -*- coding: utf-8 -*-
from urllib import request, parse
from http import cookiejar
import re

class WeiBo():

    def __init__(self,username,password):
        #设置初始化状态标志，假设成功
        self.status = True
        #以下为微博登录代码
        # 创建cookiejar实例对象
        self.cookie = cookiejar.CookieJar()
        # 根据创建的cookie生成cookie的管理器
        self.cookie_handle = request.HTTPCookieProcessor(self.cookie)	
        # 创建http请求管理器
        self.http_handle = request.HTTPHandler()	
        # 创建https管理器
        self.https_handle = request.HTTPSHandler()	
        # 创建请求管理器，将上面3个管理器作为参数属性
        # 有了opener，就可以替代urlopen来获取请求了
        self.opener =  request.build_opener(self.cookie_handle,self.http_handle,self.https_handle)	
        #负责初次登录
        #需要传递用户名和密码，来获取登录的cookie凭证	
        # 登录url，需要从登录form的action属性中获取
        self.url = 'https://passport.weibo.cn/sso/login'
        # 登录所需要的数据，数据为字典形式，
        # 此键值需要从form_data中对应的input的name属性中获取
        self.form_data = {
                'username': username, 
                'password': password, 
                'savestate': '1',
                'r':'http://m.weibo.cn/',
                'entry': 'mweibo',
                'client_id': '',
                'ec': '',
                'pagerefer': 'https://m.weibo.cn/login?backURL=https%253A%252F%252Fm.weibo.cn%252F',
                'mainpageflag':'1'
                }

        # 将数据解析成urlencode格式
        self.form_data = parse.urlencode(self.form_data) 
        self.req = request.Request(self.url,data=self.form_data.encode('utf-8'))
        self.req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36')
        self.req.add_header('Content-Type','application/x-www-form-urlencoded')
        self.req.add_header('Referer','https://passport.weibo.cn/signin/login?entry=mweibo&res=wel&wm=3349&r=https%3A%2F%2Fm.weibo.cn%2F')
        self.req.add_header('Sec-Fetch-Mode','cors')
        # 正常是用request.urlopen(),这里用opener.open()发起请求
        try:
            with self.opener.open(self.req) as self.response:
                print('Status:', self.response.status, self.response.reason)
                for k, v in self.response.getheaders():
                    print('%s: %s' % (k, v))
                print('Data:', self.response.read().decode('utf-8'))

            #获取ST值
            self.req = request.Request('https://m.weibo.cn/compose')
            self.req.add_header('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36')
            with self.opener.open(self.req) as self.response:
                print('Status:', self.response.status, self.response.reason)
                for k, v in self.response.getheaders():
                    print('%s: %s' % (k, v))
                #print('Data:', response.read().decode('utf-8'))
                data=self.response.read().decode('utf-8')
            self.st = re.findall('st:.........',data)[0][5:11]   #正则表达式寻找到ST
            print(self.st)          

        except:
            self.status = False

    def publish(self,dianbiao,time):
        #发布微博
        content = '当前电量:\n'
        for k,v in dianbiao.items():
            content += k + '室:' + '正向有功:' +str(v[1]) + '千瓦时;上一个结算日:' + str(v[2]) + '千瓦时;\n'
        content += '更新时间：' + time

        self.form_data = parse.urlencode([
            ('content',content),
            ('st',self.st)
            ])
        self.update_url='https://m.weibo.cn/api/statuses/update'
        self.req = request.Request(self.update_url,data=self.form_data.encode('utf-8'))
        headers = ([
            ('Accept','application/json, text/plain, */*'),
            ('Content-Type','application/x-www-form-urlencoded'),
            ('MWeibo-Pwa','1'),
            ('Referer','https://m.weibo.cn/compose/'),
            ('Sec-Fetch-Mode','cors'),
            ('User-Agent','Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.75 Safari/537.36'),
            ('X-Requested-With','XMLHttpRequest'),
            ('X-XSRF-TOKEN', self.st)
            ])

        for h in headers:
            self.req.add_header(h[0],h[1])
            pass

        with self.opener.open(self.req) as f:
            print('Status:', f.status, f.reason)
            for k, v in f.getheaders():
                print('%s: %s' % (k, v))
            print('Data:', f.read().decode('utf-8'))