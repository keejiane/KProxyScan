#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng

from celery import Celery
from taskStatus import TaskStatus
from autoSqli import AutoSqli
from config import sqlmap_api, redis_broker


app = Celery('task', broker=redis_broker["sqli_url"], backend=redis_broker["sqli_burl"])


@app.task
def scan_sqli(_id, url, data, referer, cookie, req_text):
	print '__________Celery task id: %s' % _id
	if url:
		print 'Scan id:%s, Url: %s' % (_id, url)
		s = AutoSqli(sqlmap_api, url, data, referer, cookie, req_text)
		s.run()

		task_status = TaskStatus()
		task_status.set_sqli_checked(_id)

	else:
		print 'No url for sqli checking...'
