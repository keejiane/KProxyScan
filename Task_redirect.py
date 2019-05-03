#!/usr/bin/env python
# encoding: utf-8
# Author: Kw0ng

from celery import Celery
from taskStatus import TaskStatus
from CheckRedirect import CheckRedirect
from config import redis_broker
from RandomUA import RandomUA


app = Celery('task', broker=redis_broker['redirect_url'], backend=redis_broker['redirect_burl'])


@app.task
def scan_redirect(_id, url, method, cookie, referer):
	print '__________Celery task id: %s' % _id
	if url:
		print 'Scan id:%s, Url: %s' % (_id, url)

		random_UA = RandomUA()
		c = CheckRedirect(url, method, cookie, referer, random_UA.ua)
		if method == 'GET':
			c.make_redirect_url()

		for poc in c.lst_poc_url_test:
			print "--sub main url: %s" % poc
			if c.check_url_redirected(poc):
				break

	else:
		print "url: %s method: %s pass" % (url, method)

	task_status = TaskStatus()
	task_status.set_sqli_checked(_id)
