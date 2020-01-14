#!/usr/bin/env python
# -*- coding: utf-8 -*-
from tkinter import *
import tkinter.messagebox as messagebox
import time
import threading
import os,sys

import wattmeter
import weibo
import mail
import config

class App:
    
    def __init__(self,master):   
        
        #线程锁
        self.lock = threading.Lock()
        #初始化读表
        self.RMsg = wattmeter.ReadMsg()
        self.RMsg.time = 'None'             #临时增加一个保存时间的属性
        #初始化界面
        self.master = master
        #self.quitButton = Button(self.master,text='退出',bg='gray',command=self.__quit)
        quit_photo = PhotoImage(file=os.path.join(sys._MEIPASS, 'quit.png'))        #仅能通过生成文件执行
        self.quitButton = Label(self.master,compound='left',image=quit_photo)
        self.quitButton.grid(row=0,column=0) 
        self.quitButton.bind('<Button-1>',self.__quit)

        self.readButton = Button(self.master,text='读表',bg='gray',fg='red',command=self.read_meter)
        self.readButton.grid(row=13,column=0)
        self.publishButton = Button(self.master,text='发布',bg='gray',fg='red',command=self.send_to_mail_and_weibo)
        self.publishButton.grid(row=11,column=0)     

        Label(self.master,text = '数据：',bg='#4e4e4e',fg='#04a89f').grid(row=0,column=1)
        Label(self.master,text = '数据：',bg='#4e4e4e',fg='#04a89f').grid(row=0,column=3)
        Label(self.master,text = '待读表',bg='#4e4e4e',fg='#04a89f').grid(row=3,column=0)
        r = 0
        for k,v in self.RMsg.dianbiao.items():
            if r%2 == 0:
                Label(self.master,text = k+'室:  '+str(v[1])+'千瓦时',bg='black',fg='white').grid(row=int(r/2),column=2,sticky="w")
            else:
                Label(self.master,text = k+'室:  '+str(v[1])+'千瓦时',bg='black',fg='white').grid(row=int((r-1)/2),column=5,sticky="w")
            r += 1
    
    #读表按钮
    def read_meter(self):        
        t = threading.Thread(target = lambda:self.__process())         #开启多线程
        t.setDaemon(True)
        t.start()
    #读取电表数据线程
    def __process(self):
        #获得线程锁
        self.lock.acquire()
        self.readButton.config(state=DISABLED)               #禁用按钮
        Label(self.master,text = '读表中',bg='black',fg='white').grid(row=3,column=0)
        Label(self.master,text = '........',bg='black',fg='white').grid(row=4,column=0)
        Label(self.master,text = '请等待',bg='black',fg='white').grid(row=5,column=0)
        Label(self.master,text = '........',bg='black',fg='white').grid(row=6,column=0)
        Label(self.master,text = '未发邮',bg='black',fg='white').grid(row=10,column=0) 
        Label(self.master,text = '未发布',bg='black',fg='white').grid(row=12,column=0)
        try:
            self.RMsg.send()
            self.RMsg.time = time.strftime('%Y-%m-%d %H:%M')
        finally:
            #存储至数据库
            self.save_to_db(self.RMsg.dianbiao,self.RMsg.time)          #存储至数据库
            #释放线程锁
            self.lock.release()            
            #进行界面显示
            r = 0
            for k,v in self.RMsg.dianbiao.items():
                if r%2 == 0:
                    Label(self.master,text = k+'室:  '+str(v[1])+'千瓦时',bg='black',fg='white').grid(row=int(r/2),column=2,sticky="w")
                else:
                    Label(self.master,text = k+'室:  '+str(v[1])+'千瓦时',bg='black',fg='white').grid(row=int((r-1)/2),column=5,sticky="w")
                r += 1
            Label(self.master,text = '已更新',bg='#4e4e4e',fg='#04a89f').grid(row=3,column=0)
            Label(self.master,text = time.strftime('%Y'),bg='black',fg='white').grid(row=4,column=0)
            Label(self.master,text = time.strftime('%m-%d'),bg='black',fg='white').grid(row=5,column=0)
            Label(self.master,text = time.strftime('%H:%M'),bg='black',fg='white').grid(row=6,column=0)
            self.readButton.config(state=NORMAL)                 #启用按钮

    #发布微博、邮件函数
    def send_to_mail_and_weibo(self):
        #先启用发布邮件
        mail_thread = threading.Thread(target = lambda:self.__mail_process())         #开启多线程
        mail_thread.setDaemon(True)
        mail_thread.start()
        #再启用发布微博
        weibo_thread = threading.Thread(target = lambda:self.__weibo_process())         #开启多线程
        weibo_thread.setDaemon(True)
        weibo_thread.start()

    #发邮件线程
    def __mail_process(self):                
        self.send_mail = mail.SendMail() 
        self.lock.acquire()
        appendix_file = '/home/pi/Library/Application Support/WattMeterData/Config'

        Label(self.master,text = '发邮中',bg='black',fg='white').grid(row=10,column=0) 
        if self.send_mail.send_mail(self.RMsg.dianbiao,self.RMsg.time,appendix_file) == True:
            Label(self.master,text = '已发邮',bg='black',fg='white').grid(row=10,column=0)
        else:
            Label(self.master,text = '邮失败',bg='black',fg='white').grid(row=10,column=0)

        self.lock.release()

    #发布微博线程
    def __weibo_process(self):
        self.publishButton.config(state=DISABLED)           #禁用按钮       
        #请填入微博账号和密码        
        self.publish = weibo.WeiBo('微博账号','微博密码') 
        if self.publish.status == False:
            messagebox.showerror('错误','网络连接失败，请重新连接后再发布微博！')
            Label(self.master,text = '发失败',bg='black',fg='white').grid(row=12,column=0)    
        else:
            #获得线程锁：
            self.lock.acquire()
            Label(self.master,text = '发布中',bg='black',fg='white').grid(row=12,column=0)  
            try:
                self.publish.publish(self.RMsg.dianbiao,self.RMsg.time)
                Label(self.master,text = '已发布',bg='black',fg='white').grid(row=12,column=0)
            finally:
                self.lock.release()
        self.publishButton.config(state=NORMAL)             #启用按钮

    #数据存储进数据库
    def save_to_db(self,data,time):
        cfg = config.Config()  
        for k,v in data.items():
            if 'db' in locals():
                db.append({'room':k,'number':v[0],'total_power':v[1],'prev_power':v[2],'udtime':time})
            else:
                db = [{}]
                db[0] = {'room':k,'number':v[0],'total_power':v[1],'prev_power':v[2],'udtime':time}
        #存储
        for dic in db:
            cfg.save(dic)
        #删掉db变量，防止下次重复存储旧数据
        del db
        del cfg

    #退出程序按钮
    def __quit(self,event):
        #退出程序
        self.master.destroy()

#主程序从这里开始
if __name__ == '__main__':

    win = Tk()    
    win.title('远程抄表')
    w = win.winfo_screenwidth()
    h = win.winfo_screenheight()
    print('w:%d,h:%d'%(w,h))

    win.geometry("%dx%d" %(w,h))
    win.attributes("-fullscreen",True)
    win.resizable(width = 'false', height = 'false')
    win.configure(bg='black')
    
    app = App(win)
    if app.RMsg.status == False:
        messagebox.showerror('错误','USB串口打开失败，请检查USB串口是否插入且正常工作!\n确认正常后，请重启程序！')
    else:        
        #开启成功后，首先读取一次并发表微博
        app.read_meter()
        app.send_to_mail_and_weibo()
        #开启窗口循环
        win.mainloop()