#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

from celery import Celery
from taskStatus import TaskStatus
from XssScanTag import XssScanTag
from config import redis_broker
from RandomUA import RandomUA


app = Celery('task', broker=redis_broker['xss_url'], backend=redis_broker['xss_burl'])


@app.task
def scan_xss(_id, url, method, data, cookie, referer):
	print '__________Celery task id: %s' % _id
	if url:
		if method == 'GET':
			print 'Scan id:%s, Url: %s' % (_id, url)
			dict_cookie = {}
			cookies_text = cookie.split("; ")
			for i in cookies_text:
				try:
					dict_cookie[str(i.split("=")[0])] = str(i.split("=")[1])

				except Exception as e:
					print "dict_cookie error: %s" % e.message

			rua = RandomUA()
			s = XssScanTag(url, method, data, dict_cookie, referer, rua.ua)

			s.run()

		elif method == 'POST':
			# 将data数据添加有直观展现的标签，类似<img src=1><iframe></iframe>等, 没办法存到数据库，只能人工检查
			pass

	task_status = TaskStatus()
	task_status.set_xss_checked(_id)
