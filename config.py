#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sqlite3
import platform
import time

class Config :

	def __init__(self):
		self.appTitle = 'WattMeterData'
		self.configPath = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', self.appTitle)

		self.table = 'config'
		if self.__connect() == False:
			self.connStat = False
		else :
			self.connStat = True
			self.__chkTable()

	def __del__ (self) :
		if self.connStat == True :
			try:
				self.__disConn()
			except Exception as e:
				pass

	def get (self) :
		result = {'stat' : 1, 'msg' : ''}

		if self.connStat != False : 
			sql = "SELECT * FROM " + self.table + " ORDER BY id DESC LIMIT 1"
			self.cur.execute(sql)
			values = self.cur.fetchone()

			if values :
				result['stat'] = 0
				result['room'] = values[1]
				result['number'] = values[2]
				result['total_power'] = values[3]
				result['prev_power'] = values[4]
				result['udrate'] = values[5]
				result['udtime'] = values[6]
		
		return result
		
	def save (self, data) :
		result = {'stat' : 1, 'msg' : ''}

		value = ""
		field = ""
		for k, v in list(data.items()) :
			field += "," + k
			value += "," + "'" + str(v) + "'"
			
		value = value[1:]
		field = field[1:]

		if self.connStat != False : 
			sql = "INSERT INTO " + self.table + " (" + field + ") VALUES" + " (" + value + ")"
			self.cur.execute(sql)
			self.conn.commit()
			result['msg'] = '更新成功！'

		return result

	def lastUd (self, timeStr) :
		if self.connStat != False : 
			sql = "UPDATE " + self.table + " SET udtime = " + str(timeStr)
			self.cur.execute(sql)
			self.conn.commit()

	def __connect (self) :
		try:
			if not os.path.exists(self.configPath) :
				os.makedirs(self.configPath)

			self.configPath = os.path.join(self.configPath, 'Config')

			self.conn = sqlite3.connect(self.configPath, check_same_thread = False)
			self.cur = self.conn.cursor()
			return True
		except:
			return False

	def __chkTable (self) :
		if self.connStat == False : return False

		sql = "SELECT tbl_name FROM sqlite_master WHERE type='table'"
		tableStat = False

		self.cur.execute(sql)
		values = self.cur.fetchall()

		for x in values:
			if self.table in x :
				tableStat = True

		if tableStat == False :
			self.__create()

	def __create (self) :
		if self.connStat == False : return False

		sql = 'create table ' + self.table + ' (id integer PRIMARY KEY autoincrement, room text, number varchar(500), total_power varchar(500), prev_power varchar(500), udrate int(1), udtime varchar(100))'
		self.cur.execute(sql);

		room = ''
		number = ''
		total_power = ''
		prev_power = ''
		udrate = '2'
		udtime = str(int(time.time()))

		sql = "insert into " + self.table + " (room, number, total_power, prev_power, udrate, udtime) values ('" + room + "', '" + number + "', '" + total_power + "', '" + prev_power + "', " + udrate + ", '" + udtime + "')"

		self.cur.execute(sql)
		self.conn.commit()

	def __disConn (self) :
		if self.connStat == False : return False

		self.cur.close()
		self.conn.close()