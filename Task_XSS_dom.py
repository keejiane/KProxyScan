#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author: kw0ng


import os
import commands
import time
from celery import Celery
from taskStatus import TaskStatus
from models import *
from config import redis_broker


app = Celery('task', broker=redis_broker['xss_dom_url'], backend=redis_broker['xss_dom_burl'])


@app.task
def scan_xss_dom(_id, method, url, data, referer, cookie):
	print '__________Celery task id: %s' % str(_id)
	if url and method == 'GET':
		print 'Scan Url:%s' % url
		js_path = '/path/to/your/workdir/casperXSS'
		os.chdir(js_path)
		print 'Current cwd: %s' % os.getcwd()
		fp = open(js_path+'/cookies.txt')
		try:
			fp.write(cookie)
		except Exception, e:
			print "Can't not open cookie file: %s" % e.message
		finally:
			fp.close()

		cmd = "casperjs --web-security=false --ssl-protocol=any --ignore-ssl-errors=true xss.js --url=\"%s\"" \
		      "--cookiejar=cookie.txt" % url
		print "scan_xss_dom cmd: %s" % cmd

		(status, output) = commands.getstatusoutput(cmd)
		print "status: %s, output: %s" % (status, output)
		dom_url = output[10:]

		XSSRecords.insert(url=dom_url, injection=dom_url, method='xss_dom', special='dom').execute()
		ctime = time.strftime("%Y-%m-%d", time.localtime())
		with open(js_path+'/domxss.'+ctime+'.log', 'a') as ff:
			ff.write(output+'\n')

		task_status = TaskStatus()
		task_status.set_xss_dom_checked(_id)
