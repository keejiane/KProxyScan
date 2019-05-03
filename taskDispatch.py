#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

import pymongo
import time
from bson.objectid import ObjectId
from Task_sqli import scan_sqli
from Task_XSS import scan_xss
from Task_XSS_dom import scan_xss_dom
from Task_redirect import scan_redirect
from config import mongo_db, scan_plugin_status
from taskStatus import TaskStatus


class TaskDispatch(object):
	def __init__(self):
		self.sleep_time = 5
		self.conn = pymongo.MongoClient(host=mongo_db['host'], port=mongo_db['port'])
		self.db = self.conn.mitmproxy
		self.collection = self.db.requests
		self.no_sqli = self.no_xss = self.no_xss_dom = self.no_redirect = False

	def make_task(self, status):
		tasks = self.collection.find({status: 0}).sort("_id", pymongo.ASCENDING).limit(1)

		task_id, url, method, data, referer, cookies, req_text = '', '', '', '', '', '', ''

		try:
			for task in tasks:
				task_id = task['_id']
				url = task['req']['url']
				method = task['req']['method']
				data = task['req']['data']
				cookies = task['req']['cookies']
				referer = task['req']['referer']
				req_text = task['req_text']
				# sqli_status = task['sqli_status']

		except Exception:
			print 'Make task failed!!!'

		return task_id, method, url, data, referer, cookies, req_text

	def dispatch_task(self):
		task_status = TaskStatus()

		if scan_plugin_status['sqli_plugin']:
			task_id, method, url, data, referer, cookies, req_text = self.make_task('sqli_status')
			if task_id:
				print "Scan sql injection: %s" % task_id
				task_status.set_sqli_checking(ObjectId(task_id))
				scan_sqli.apply_async((str(task_id), url, data, referer, cookies, req_text))

			else:
				self.no_sqli = True
				print 'No more url left for sqli checking!!!'
		else:
			print 'sqli plugin status is set to false, passing!!!'

		if scan_plugin_status['xss_plugin']:
			task_id, method, url, data, referer, cookies, req_text = self.make_task('xss_status')
			if task_id:
				print "Scan xss injection at url: %s" % task_id
				task_status.set_xss_checking(ObjectId(task_id))
				scan_xss.apply_async((str(task_id), url, method, data, cookies, referer))

			else:
				self.no_xss = True
				print 'No more url left for xss checking!!!'
		else:
			print 'xss plugin status is set to false, passing!!!'

		if scan_plugin_status['xss_dom_plugin']:
			task_id, method, url, data, referer, cookies, req_text = self.make_task('xss_dom_status')
			if task_id:
				print "Scan xss injection at dom: %s" % task_id
				task_status.set_xss_dom_checking(ObjectId(task_id))
				scan_xss_dom.apply_async((str(task_id), method, url, data, referer, cookies))

			else:
				self.no_xss_dom = True
				print 'No more url left for xss_dom checking!!!'
		else:
			print 'xss_dom plugin status is set to false, passing!!!'

		if scan_plugin_status['redirect_plugin']:
			task_id, method, url, data, referer, cookies, req_text = self.make_task('redirect_status')
			if task_id:
				print "Scan redirect: %s" % task_id
				task_status.set_redirect_checking(ObjectId(task_id))
				scan_redirect.apply_async((str(task_id), url, method, cookies, referer))
			else:
				self.no_redirect = True
				print 'No more url left for redirect checking!!!'
		else:
			print 'redirect plugin status is set to false, passing!!!'

	def do_task(self):
		while True:
			if all((self.no_sqli, self.no_xss, self.no_xss_dom, self.no_redirect)):
				break

			self.dispatch_task()
			print 'Get One Task Done, Wait %s Seconds...' % str(self.sleep_time)
			time.sleep(self.sleep_time)

		print "No request left for checking~~~"


if __name__ == '__main__':
	t = TaskDispatch()
	t.do_task()
