#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Kw0ng


import re
import sys
import urlparse

import pycurl
import StringIO

from models import *


class CheckRedirect(object):
	def __init__(self, url, method, cookies, referer, user_agent):
		# method: GET

		self.url = url
		self.headers = {
			"User-Agent": user_agent,
			"Referer": referer,
			"Accept": "*/*",
			"Accept-Encoding": "gzip, deflate",
			"Accept-Language": "zh-CN"
		}

		self.header = []
		for k, v in self.headers.items():
			self.header.append("%s: %s" % (k, v))

		self.cookies = cookies
		self.noexisturl = "noexist.com"
		self.status = 'ToReplacePoC_'
		self.method = method

		self.lst_poc_url_test = []
		self.dict_poc_url = {}

	def make_redirect_poc(self, url):
		"""
		http://www.baidu.com
		http://www.baidu.com/http://xiaomi.com
		http://www.xiaomi.com.baidu.com
		http://igame.xiaomi.com@baidu.com
		http://www.baidu.com/?http://www.xiaomi.com
		http://www.baidu.com?www.xiaomi.com
		"""

		lst_poc_url = []

		lst_poc_temp = [
			"hack",
			"hack/http://domain",
			"domain.hack",
			"domain@hack",
			"hack/?http://domain",
			"hack?domain"
		]

		paras = urlparse.urlparse(url)
		scheme = paras[0]
		netloc = paras[1]
		path = paras[2]
		query = paras[4]

		for poc_temp in lst_poc_temp:
			mix = poc_temp.replace("hack", self.noexisturl).replace("domain", netloc)

			if query:
				poc_url = "%s://%s%s?%s" % (scheme, mix, path, query)

			else:
				poc_url = "%s://%s%s" % (scheme, mix, path)

			lst_poc_url.append(poc_url)

		return lst_poc_url

	def _make_redirect_url(self, tuple_paras, j):
		query_new = ''
		# lst_poc_url = []

		i = 0

		for k, v in tuple_paras:
			# print "k: %s v: %s" % (k, v)

			if re.search('^(http|https):', v) and i == j:
				# just do once
				lst_poc_url = self.make_redirect_poc(v)
				v = self.status + str(j)
				self.dict_poc_url[v] = lst_poc_url

			i = i + 1

			c = "%s=%s" % (k, v)
			query_new = "%s&%s" % (query_new, c)
			# print 'query_new is:%s' % query_new

		# print 'dict_poc_url is:%s' % self.dict_poc_url
		return query_new

	def make_redirect_url(self):
		paras = urlparse.urlparse(self.url)
		scheme = paras[0]
		netloc = paras[1]
		path = paras[2]

		tuple_paras = urlparse.parse_qsl(paras[4], 1)

		dict_query = {}

		for j in xrange(len(tuple_paras)):
			query_new = self._make_redirect_url(tuple_paras, j)
			dict_query[self.status + str(j)] = query_new[1:]
		# print 'dict_query is:%s' % dict_query

		for k, v in dict_query.items():
			url = v
			try:
				lst_poc = self.dict_poc_url[k]

				for poc in lst_poc:
					new_query = url.replace(k, poc)
					# print 'new_query is:%s' % new_query
					poc_url = "%s://%s%s?%s" % (scheme, netloc, path, new_query)
					self.lst_poc_url_test.append(poc_url)

			except Exception:
				# print "dict_poc_url key :%s not exists" % k
				pass

		return

	def check_url_redirect(self, url, timeout=10):
		# so stable than requests and urllib2

		io_t = StringIO.StringIO()
		io_b = StringIO.StringIO()
		curl = pycurl.Curl()
		curl.setopt(pycurl.HTTPHEADER, self.header)
		curl.setopt(pycurl.URL, url)
		curl.setopt(pycurl.FOLLOWLOCATION, 1)
		curl.setopt(pycurl.MAXREDIRS, 5)
		curl.setopt(pycurl.CONNECTTIMEOUT, timeout)
		curl.setopt(pycurl.TIMEOUT, 30)
		curl.setopt(pycurl.SSL_VERIFYPEER, 0)
		curl.setopt(pycurl.NOSIGNAL, 1)
		# crl.setopt(crl.POSTFIELDS, urllib.urlencode(post_data_dic))
		curl.setopt(pycurl.HEADERFUNCTION, io_t.write)
		curl.setopt(pycurl.WRITEFUNCTION, io_b.write)

		try:
			curl.perform()

		except pycurl.error, error:
			errno, errstr = error
			print '[Warning]error: %s' % errstr

		code = curl.getinfo(curl.HTTP_CODE)
		rnum = curl.getinfo(curl.REDIRECT_COUNT)
		# get located url
		eurl = curl.getinfo(curl.EFFECTIVE_URL)

		# print "eurl: %s" % eurl
		curl.close()

		return eurl

	def check_url_redirected(self, url):
		status = False
		eurl = self.check_url_redirect(url)

		paras = urlparse.urlparse(eurl)
		netloc = paras[1]

		if re.search(self.noexisturl, netloc):
			print "FFFFound Redirect url: %s" % url
			Redirect.insert(url=self.url, payload=url, method=self.method).execute()
			status = True

		else:
			print "Not found url: %s" % url

		return status


if __name__ == '__main__':
	url = "http://cps.dianping.com/redirect/hao123?url=http://www.mi.com?dianping.com&tn=baidutuan_tg&" \
	      "baiduid=c0adc20971eb3c064dc0cbd3adaf36c1 "
	method = "GET"
	cookies = ""
	referer = ""
	user_agent = ""

	print "+main url: %s" % url
	c = CheckRedirect(url, method, cookies, referer, user_agent)
	if method != 'GET':
		sys.exit()

	c.make_redirect_url()

	for poc in c.lst_poc_url_test:
		print "--sub main url: %s" % poc

		if c.check_url_redirected(poc):
			break

