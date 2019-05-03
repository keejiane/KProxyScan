#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng


import requests
import time
import json

from threading import Thread
from models import *


class AutoSqli(Thread):
	def __init__(self, server='', target='', data='', referer='', cookie='', req_text=''):
		Thread.__init__(self)
		self.server = server
		if self.server[-1] != '/':
			self.server += '/'
		self.target = target
		self.taskid = ''
		self.engineid = ''
		self.status = ''
		self.data = data
		self.referer = referer
		self.cookie = cookie
		self.req_text = req_text
		self.start_time = time.time()

	def task_new(self):
		self.taskid = json.loads(
			requests.get(self.server + 'task/new').text)['taskid']
		print 'Created new task: ' + self.taskid + "\t" + self.target
		if len(self.taskid) > 0:
			return True
		return False

	def task_delete(self):
		if json.loads(requests.get(self.server + 'task/' + self.taskid + '/delete').text)['success']:
			print '[%s] Deleted task' % self.taskid
			return True
		return False

	def scan_start(self):
		headers = {'Content-Type': 'application/json'}
		payload = {
			'url': self.target,
			'data': self.data,
			'cookie': self.cookie,
			'referer': self.referer}
		url = self.server + 'scan/' + self.taskid + '/start'
		t = json.loads(
			requests.post(url, data=json.dumps(payload), headers=headers).text)
		self.engineid = t['engineid']
		if len(str(self.engineid)) > 0 and t['success']:
			return True
		return False

	def scan_status(self):
		self.status = json.loads(
			requests.get(self.server + 'scan/' + self.taskid + '/status').text)['status']
		if self.status == 'running':
			return 'running'
		elif self.status == 'terminated':
			return 'terminated'
		else:
			return 'error'

	def scan_data(self):
		self.data = json.loads(
			requests.get(self.server + 'scan/' + self.taskid + '/data').text)['data']
		if len(self.data) == 0:
			print 'not injection:\t' + self.target
		else:
			print '=======> injection:\t' + self.target

			try:
				for n in self.data[0]['value']:
					dbms = n['dbms']
					dbms_version = n['dbms_version']

					for k, v in n['data'].iteritems():
						num = k
						matchratio = v['matchRatio']
						payload = v['payload']
						title = v['title']
						vector = v['vector']

						SQLIRecords.insert(url=self.target, num=num, dbms=dbms, dbms_version=dbms_version,
						                   matchRatio=matchratio, payload=payload, title=title, vector=vector,
						                   request_text=self.req_text).execute()

			except Exception, e:
				print 'Parse sqlmap data failed:%s' % e

	def option_set(self):
		headers = {'Content-Type': 'application/json'}
		option = {"options": {
			"risk": 1,
			"smart": True,
			"batch": True,
			"verbose": 4
			}
		}
		url = self.server + 'option/' + self.taskid + '/set'
		t = json.loads(
			requests.post(url, data=json.dumps(option), headers=headers).text)

	def scan_stop(self):
		json.loads(
			requests.get(self.server + 'scan/' + self.taskid + '/stop').text)['success']

	def scan_kill(self):
		json.loads(
			requests.get(self.server + 'scan/' + self.taskid + '/kill').text)['success']

	def write_to_db(self):
		pass

	def run(self):
		try:
			if not self.task_new():
				return False
			self.option_set()
			if not self.scan_start():
				return False
			while True:
				if self.scan_status() == 'running':
					time.sleep(10)
				elif self.scan_status() == 'terminated':
					break
				else:
					break
				print self.target + ":\t" + str(time.time() - self.start_time)
				if time.time() - self.start_time > 500:
					error = True
					self.scan_stop()
					self.scan_kill()
					break
			self.scan_data()
			self.task_delete()
			print self.target + ":\t" + str(time.time() - self.start_time)
		except Exception, e:
			print e

# if __name__ == '__main__':
#     t = AutoSqli('http://127.0.0.1:8775', 'http://www.zxssyxx.com/read.asp?id=2471')
#     t.run()
