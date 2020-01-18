#!/usr/bin/env python
# -*- coding: utf-8 -*-
import serial

class ReadMsg():
	def __init__(self):
		#假设初始化成功
		self.status = True
		#初始化串口
		try:
			self.ser = serial.Serial(
			#	'/dev/ttyAMA0',					#linux系统的串口号，windows为COM1等
			#	'/dev/ttyUSB0',
				'COM3',
				baudrate=2400,					#设置为电表默认波特率
				bytesize=serial.EIGHTBITS,		#8位
				parity=serial.PARITY_EVEN,		#偶校验，电表(DL/T645-2007)为偶校验
				stopbits=serial.STOPBITS_ONE,	#1位停止位
				timeout=0.5						#读超时，单位为秒
				)
		except:
			#初始化失败标志
			self.status = False

		#初始化电表字典
		self.dianbiao = {
				'201':['010097796152','-1','-1'],
				'202':['010126762145','-1','-1'],
				'301':['010097796152','-1','-1'],
				'302':['010126762145','-1','-1'],
				'401':['010097796152','-1','-1'],
				'402':['010126762146','-1','-1'],
				'501':['010097796153','-1','-1'],
				'502':['010126762145','-1','-1'],
				'601':['010097796152','-1','-1'],
				'602':['010126762145','-1','-1'],
				'701':['010097796152','-1','-1'],
				'702':['010097796151','-1','-1'],
				'801':['010097796152','-1','-1'],
				'802':['010126762145','-1','-1'],
				'901':['010097796152','-1','-1'],
				'902':['010126762145','-1','-1'],
				'1001':['010097796152','-1','-1'],
				'1002':['010126762145','-1','-1'],
				'1101':['010097796152','-1','-1'],
				'1102':['010097796152','-1','-1'],
				'1201':['010097796151','-1','-1'],
				'1202':['010126762145','-1','-1'],
				'1301':['010097796152','-1','-1'],
				'1302':['010126762145','-1','-1'],
				'1401':['010097796152','-1','-1'],
				'1402':['010126762145','-1','-1'],
				'1501':['010097796152','-1','-1'],
				'1502':['010097796152','-1','-1']
				}

		#设置tuple，存储读取数据块命令
		self.zuheyougong = ('0x33','0x33','0x33','0x33')				#组合有功
		self.zhengxiang = ('0x33','0x33','0x34','0x33')					#正向有功
		self.zuhejiesuan1 = ('0x34','0x33','0x33','0x33')				#上1个结算日组合有功
		self.zxjiesuan1 = ('0x34','0x33','0x34','0x33')					#上1个结算日正向有功
		self.zuhejiesuan2 = ('0x35','0x33','0x33','0x33')				#上2个结算日组合有功
		self.zxjiesuan2 = ('0x35','0x33','0x34','0x33')					#上2个结算日正向有功

	def CreatMsg(self,list,tuple):
		msg = [hex(x) for x in bytes.fromhex(list[0])]	#地址，16进制数组转为字节串
		msg.reverse()						#小端在前
		msg.insert(0,'0x68')				#68H开头
		msg.append('0x68')					#地址码后面加68H
		msg.append('0x11')					#控制字11H，表示读数据
		msg.append('0x04')					#数据域长度，0字节
		for x in tuple : msg.append(x)		#加入数据块命令
		msg.append(hex(sum([int(x,16) for x in msg])&0x00000000FF))	#校验码
		msg.append('0x16')
		msg=bytes([int(x,16) for x in msg])		#数组转为16进制字符串
		return msg

	def DecodeMsg(self,by):											#str为字节串
		msg = [x for x in bytes(by)]								#转为16进制数组
		while msg[0] != 0x68:	msg.pop(0)							#去除开头的唤醒数据
		#校验数据是否正确，若不正确，则返回False
		if msg[-2] != (sum(x for x in msg[:-2])&0x00000000FF):		#计算校验码
			return False
		
		address = msg[1:7]											#获取电表地址
		address.reverse()											#改为大端在前
		address = [(x>>4&0x0F)*10+(x&0x0F) for x in address]		#BCD码转换公式
		address = ''.join(str(x) for x in address)
		if msg[8] == 0x91 :
			dl = msg[10:-2]
			dl.reverse()
			dl = [x-0x33 for x in dl]								#接收方，减0x33处理
			dl = [(x>>4&0x0F)*10+(x&0x0F) for x in dl]				#BCD码转换公式
			result = 0.0
			for x in dl[:-4]:			
				result = result*100+x
			return address,result/100
		return address

	def send(self):
		if self.ser.isOpen():
			pass
		else:
			self.ser.open()
		#开始读表
		for k,v in self.dianbiao.items():
			#读取正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[k],self.zhengxiang))
			s = self.ser.readline()
			if s == b'':
				self.dianbiao[k][1] = '失败'
			else:
				self.dianbiao[k][1] = self.DecodeMsg(s)[1]
			#读取上一个结算日正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[k],self.zxjiesuan1))
			s = self.ser.readline()
			if s == b'':
				self.dianbiao[k][2] = '失败'
			else:
				self.dianbiao[k][2] = self.DecodeMsg(s)[1]
		self.ser.close()

	def achieve(self):
		#打开串口
		if self.ser.isOpen():
			pass
		else:
			self.ser.open()
		for room,data in self.dianbiao.items():
			#读取正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[room],self.zhengxiang))
			s = self.ser.read()
			if s != b'':
				while(ord(s) != 0x68):
					s = self.ser.read()
				for i in range(8):
					s += self.ser.read()
				L = self.ser.read()
				s += L
				for i in range(ord(L)+2):
					s += self.ser.read()
				result = self.DecodeMsg(s)
				if result != False:
					self.dianbiao[room][1] = result[1]
				else:
					self.dianbiao[room][1] = '失败'
			else:
				self.dianbiao[room][1] = '失败'
			self.ser.reset_input_buffer()
			#读取上一个结算日正向有功
			self.ser.write(self.CreatMsg(self.dianbiao[room],self.zxjiesuan1))
			s = self.ser.read()
			if s != b'':
				while(ord(s) != 0x68):
					s = self.ser.read()
				for i in range(8):
					s += self.ser.read()
				L = self.ser.read()
				s += L
				for i in range(ord(L)+2):
					s += self.ser.read()
				result = self.DecodeMsg(s)
				if result != False:
					self.dianbiao[room][2] = result[1]
				else:
					self.dianbiao[room][2] = '失败'
			else:
				self.dianbiao[room][2] = '失败'
			self.ser.reset_input_buffer()
		#关闭串口
		self.ser.close()
	
	def __del__(self):
		if self.ser.isOpen():
			self.ser.close() 
		print('串口已关闭！')