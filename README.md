# WattMeter
树莓派485接口抄表（电表）

项目背景：
    有的小区（农村地区）建设大楼后，供电公司不肯一个套房一个电表，只提供了两个公共的三相表，再自己去分表。因此，有必要制作一套远程抄表的方法解决抄表、算电费的问题。

实现功能：
    1.远程抄表（有功电量），并存入数据库。开程序后自动启动抄表一次。
    2.自动发送微博。
    3.自动发送邮件并抄送数据库文件为附件。

使用条件：
    1.电网专用的电表（含485模块），可远程抄表的电表。（既可以直接接入485总线，或者购买载波模块省去接信号线的麻烦）
    2.树莓派（raspberry 系统）
    3.USB转485模块
    4.3.5寸显示屏
 
 
使用方法：
    1.在win.py文件中114行输入微博账号和密码
    2.mail.py文件中输入发件人的账号和密码，以及收件人的邮箱账号
    3.win.py第26行说明了，该程序只能打包之后使用
    4.打包方法：下载所有文件之后，用cmd进入文件夹，然后使用指令：pyinstaller -F -w win.spec进行打包。
    5.打包之后，会生成一个dist文件夹，里面的win文件就可以直接运行了。
    
    ps：注意我用的是USB转485串口，因此wattmeter.py文件的第13行用的是'/dev/ttyUSB0'
    
成品效果图：
![成品效果图](https://github.com/lwpo2008/WattMeter/blob/master/20200114164538.jpg)





另外，树莓派安装CH340芯片的USB模块方法如下：
树莓派安装CH340驱动（USB转串口）
1.	为何有此需求
原本树莓派3B+带有两个串口，一个硬件串口，一个mini串口。硬件串口默认给了蓝牙使用，mini串口使用的是CPU的时钟（CPU频率变化不稳定）。因此，蓝牙与硬件串口不可兼得。
我的3B+用一块3.5寸屏幕插在排针上面，导致排针要另外接线非常麻烦。因此，考虑从USB接口再接一个串口使用。
2.	驱动下载官方网址（linux版本）
http://www.wch.cn/download/CH341SER_LINUX_ZIP.html 
下载下来是三个文件，分别是：ch34x.c、Makefile、readme.txt。通过源码安装步骤为：（1）进入该文件夹；（2）make；（3）make load
3.	遇到问题
（1）	make步骤报错：/lib/modules/4.19.75-v7+/build: 没有那个文件或目录。 停止。
这个时候，是linux-headers的问题。处理办法：
sudo apt-get install linux-headers
ls  /usr/src  查看linux-headrs的版本
cd /lib/modules/4.19.75-v7+ 进入文件夹（上面报错的文件夹）
sudo ln -s /usr/src/linux-headers-4.19.66-v7+ build 形成链接即可
（2）	报错：unknown type name ‘wait_queue_t’。打开ch34x.c查看源码，发现实际上wait_queue_t wait 并没有用，直接注释掉。
（3）	报错：implicit declaration of function ‘signal_pending’。这个错误是因为没有包含一个头文件signal.h。
在文件包含头文件的地方加入 #include <linux/sched/signal.h>。
4.	以上问题解决之后，进入源码文件夹依次执行（1）make；（2）make load即可安装成功。
5.	如何查看是否安装成功。
dmesg | grep ttyS*   执行该命令，即可查看拥有几个串口。能够看到：
[    2.025631] console [ttyS0] enabled
[    7.836397] usb 1-1.2: ch341-uart converter now attached to ttyUSB0
成功！！

    

