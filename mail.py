#!/usr/bin/python
# -*- coding: UTF-8 -*-

from email.header import Header
from smtplib import SMTP_SSL
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class SendMail():

    def __init__(self):
        #邮箱服务器地址（用的新浪邮箱，比较稳定，不会判定未垃圾邮件）
        self.host_server = 'smtp.sina.com'
        # sender_mail为发件人的邮箱
        self.sender = 'xxxxxx@sina.com'
        # pwd为邮箱的授权码
        self.pwd = 'xxxxxxxxxx'  
        # 收件人邮箱
        self.receiver = 'xxxxxxxx@qq.com'

    def send_mail(self,dianbiao,time,appendix):        
        mail_content = '当前电量:\n'
        for k,v in dianbiao.items():
            mail_content += k + '室电表号(' + str(v[0]) +')：' + str(v[1]) + '千瓦时;上一个结算日:' + str(v[2]) + '千瓦时;\n'
        mail_content += '更新时间：' + time
        mail_title = time + '三落大厦电量统计'
        mail_appendix = appendix

        try:          
            # ssl登录
            smtp = SMTP_SSL(self.host_server)
            # set_debuglevel()是用来调试的。参数值为1表示开启调试模式，参数值为0关闭调试模式
            smtp.set_debuglevel(1)
            smtp.ehlo(self.host_server)
            smtp.login(self.sender, self.pwd)
            #正文处理
            msg = MIMEMultipart()            
            msg["Subject"] = Header(mail_title, 'utf-8')
            msg["From"] = self.sender
            msg["To"] = self.receiver
            msg.attach(MIMEText(mail_content, "plain", 'utf-8'))
            #附件处理
            if os.path.exists(mail_appendix):
                appendix_msg = MIMEText(open(mail_appendix, "rb").read(), "base64", "utf-8")
                appendix_msg["Content-Type"] = "application/octet-stream"
                appendix_msg["Content-Disposition"] = 'attachment; filename="database"'
                msg.attach(appendix_msg)
            else:
                pass
            #发送邮件
            smtp.sendmail(self.sender, self.receiver, msg.as_string())
            smtp.quit()
            return True
        except Exception as e:
            print(e)
            return False

